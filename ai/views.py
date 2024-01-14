from django.shortcuts import render
from django.http import HttpResponse
from .forms import PDFUploadForm

# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the ai index.")


def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            return render(request, 'ai/upload_success.html')
    else:
        form = PDFUploadForm()
    return render(request, 'ai/upload_pdf.html', {'form': form})
