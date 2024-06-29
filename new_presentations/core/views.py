from django.shortcuts import render
from core.presentation_service import main
from core.language_service import get_all_languages
from core.wikipedia_service import results_for_title
from django.http import HttpResponseBadRequest, FileResponse, JsonResponse

# Create your views here.


def index(request, *args, **kwargs):
    return render(request, 'core/index.html', {"languages": get_all_languages()})


def create_presentation(request):
    try:
        title, language, num_slides, name = request.GET['title'], request.GET[
            'language'], request.GET['slides'], request.GET['name']
    except Exception:
        HttpResponseBadRequest()
    return JsonResponse({"presentation": main(title, language, num_slides, name)})


def get_title(request):
    try:
        title, language = request.GET['title'], request.GET['language']
    except Exception:
        return HttpResponseBadRequest()
    return JsonResponse({"titles": results_for_title(title, language)})


def download(request):
    return render(request, 'core/download.html', {"presentation": request.GET.get('presentation_name')})


def download_presentation(request):
    presentation_name = request.GET.get("presentation_name")
    response = FileResponse(
        open(f'static/core/presentations/{presentation_name}', 'rb'), as_attachment=True)
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    response['Content-Disposition'] = f'attachment;filename="{presentation_name}"'
    return response


def handler404(request, *args, **kwargs):
    response = render(request, '404.html', {})
    response.status_code = 404
    return response


def handler500(request, *args, **kwargs):
    response = render(request, '404.html', {})
    response.status_code = 500
    return response
