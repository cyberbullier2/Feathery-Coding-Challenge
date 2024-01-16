from django.shortcuts import render
from django.http import HttpResponse
from ..forms import PDFUploadForm
from decouple import config
from ..utils.image_processing import convert_pdf_to_images, encode_image_to_base64
from ..utils.openai_helpers import call_openai_vision_model, call_openai_text_model
from ..models.portfolio import PortfolioSummary
from ..prompts import VISION_MODEL_PROMPT, create_text_model_prompt

def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_paths = convert_pdf_to_images(request.FILES['pdf_file'])
            if not image_paths:
                return HttpResponse("Cannot upload empty pdf")

            encoded_images = [encode_image_to_base64(img) for img in image_paths]
            if None in encoded_images:
                return HttpResponse("Failed to encode one or more images.")

            vision_response = call_openai_vision_model(encoded_images, config('OPENAI_API_KEY'))
            if vision_response is None:
                return HttpResponse("Failed to call OpenAI Vision API.")

            summary_response = call_openai_text_model(vision_response, config('OPENAI_API_KEY'))
            if summary_response is None:
                return HttpResponse("Failed to call OpenAI Text API.")

            return render(request, 'ai/upload_pdf_success.html', {"portfolio_summary": summary_response})
        else:
            return HttpResponse("Invalid form submission.")
    else:
        form = PDFUploadForm()

    return render(request, 'ai/upload_pdf.html', {'form': form})
