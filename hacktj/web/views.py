from django.conf import settings
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from pytube import YouTube
import urllib.parse as urlparse
import uuid
import os
import ast
import video.process
import audio.process

from .models import UploadedFile


def index_view(request):
    return render(request, "index.html")


@require_http_methods(["POST"])
def upload_view(request):
    fname = f"download_{uuid.uuid4()}"
    ylink = request.POST.get("link")
    if not ylink:
        raise Http404
    parsed = urlparse.urlparse(ylink)
    vid = urlparse.parse_qs(parsed.query)['v'][0]
    sterms = "_".join(request.POST.getlist("terms"))
    sopts = "_".join(request.POST.getlist("types"))
    if UploadedFile.objects.filter(video_id=vid).exists():
        return redirect(reverse('results', kwargs={'vid': vid, 'search_opts': sopts, 'search_terms': sterms}))
    YouTube(ylink).streams.filter(file_extension='mp4').first().download(output_path=settings.UPLOAD_DIR, filename=fname)
    UploadedFile.objects.create(name=fname, video_id=vid, audio_data="{}", video_data="{}")
    return redirect(reverse('results', kwargs={'vid': vid, 'search_opts': sopts, 'search_terms': sterms}))


def results_view(request, vid, search_opts, search_terms):
    v = get_object_or_404(UploadedFile, video_id=vid)
    if not ast.literal_eval(v.audio_data):
        v.audio_data = audio.process.word_data(os.path.join(settings.UPLOAD_DIR, "{}.mp4".format(v.name)))
        if not v.audio_data:
            v.audio_data = "{}"
    if not ast.literal_eval(v.video_data):
        v.video_data = video.process.word_data(os.path.join(settings.UPLOAD_DIR, "{}.mp4".format(v.name)))
        if not v.video_data:
            v.video_data = "{}"
    v.save()
    results = {}
    print(v.audio_data, v.video_data)
    adata = eval(v.audio_data)
    vdata = eval(v.video_data)
    if 'audio' in search_opts.lower():
        for term in search_terms.split("_"):
            if term.lower() in adata:
                results[term.lower()] = adata[term.lower()]
    if 'image' in search_opts.lower():
        for term in search_terms.split("_"):
            if term in vdata:
                if term.lower() in results:
                    results[term.lower()] += vdata[term.lower()]
                else:
                    results[term.lower()] = vdata[term.lower()]
    return JsonResponse({"results": results})
