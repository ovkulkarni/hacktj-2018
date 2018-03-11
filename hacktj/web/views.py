from django.conf import settings
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from pytube import YouTube
import urllib.parse as urlparse
import uuid
import os
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
    adata, vdata = dict(), dict()
    if not eval(v.audio_data):
        adata = audio.process.word_data(os.path.join(settings.UPLOAD_DIR, "{}.mp4".format(v.name)))
        v.audio_data = adata
        if not v.audio_data:
            v.audio_data = "{}"
    print(adata)
    if not eval(v.video_data):
        vdata = video.process.word_data(os.path.join(settings.UPLOAD_DIR, "{}.mp4".format(v.name)))
        v.video_data = vdata
        if not v.video_data:
            v.video_data = "{}"
    print(vdata)
    v.save()
    results = {}
    if not adata:
        adata = eval(v.audio_data)
    if not vdata:
        vdata = eval(v.video_data)
    if 'audio' in search_opts.lower():
        for term in search_terms.split("_"):
            res = audio.process.find_matches(adata, term.lower())
            if term.lower() not in results:
                results[term.lower()] = []
            if res:
                results[term.lower()] += res
    if 'image' in search_opts.lower():
        for term in search_terms.split("_"):
            res = video.process.find_matches(vdata, term.lower())
            if term.lower() not in results:
                results[term.lower()] = []
            results[term.lower()] += res
    print(results)
    return JsonResponse({"results": results})
