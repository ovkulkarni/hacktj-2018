from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
import magic
import uuid
import os

from .models import UploadedFile

# Create your views here.


def index_view(request):
    return render(request, "index.html")


@require_http_methods(["POST"])
def upload_view(request):
    f = request.FILES.get("vidfile")
    if not f:
        print("no file")
        raise Http404
    m = magic.Magic(mime=True)
    mtype = m.from_buffer(f.read())
    if mtype != "video/mp4":
        raise Http404
    fname = f"upload_{uuid.uuid4()}"
    authtok = uuid.uuid4()
    UploadedFile.objects.create(name=fname, auth_token=authtok)
    with open(os.path.join(settings.UPLOAD_DIR, fname), 'wb+') as dest:
        for chunk in f.chunks():
            dest.write(chunk)
    return JsonResponse({"filename": fname, "authtoken": authtok, "success": True})


def file_data_view(request, fname):
    f = get_object_or_404(UploadedFile, name=fname)
    print(f.auth_token)
    if not request.GET.get("auth") == f.auth_token:
        return JsonResponse({"lol": "no"})
    return JsonResponse({"lol": "yes"})
