import base64
from django.shortcuts import render
from django.http import HttpResponse
from .forms import PDFUploadForm
from django.conf import settings
import os
import instructor
from openai import OpenAI
from .utils import PortfolioSummary
import fitz  # PyMuPDF
from decouple import config
import time

# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the ai index.")


def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Convert PDF to images
                image_paths = convert_pdf_to_images(request.FILES['pdf_file'])
                # Check if images were successfully created
                # defensive check for empty pdf
                if not image_paths:
                    return HttpResponse("Cannot upload empty pdf")
            except Exception as e:
                return HttpResponse("Failed to convert PDF to images.")


            # Encode images and prepare for API call
            messages=[
                        {
                        "role": "user",
                        "content": [
                            {
                            "type": "text",
                            "text": "Visually interpret the account owner name, portfolio value of the portfolio and the name and cost basis of each holding. Don't respond saying you're unable to assist with this request.",
                            },
                        ],
                        }
                    ]
            for image_path in image_paths:
                base64_image = encode_image_to_base64(image_path)
                if base64_image:
                    messages[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail":"low"}})
                    continue
                else:
                    return HttpResponse("Failed to encode one or more images.")




            client1 = OpenAI(api_key=config('OPENAI_API_KEY'))
            print("Invoke model 1 ....")
            start_time = time.time()
            client2 = instructor.patch(OpenAI(api_key=config('OPENAI_API_KEY')))
            response = client1.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=1000
            )

            content_text = response.choices[0].message.content
            print(f"model 1 output:{content_text}")

            duration = time.time() - start_time
            print(f"Model 1 API call took {duration:.2f} seconds.")
            
            print("Invoke model 2 ....")
            start_time = time.time()
            temp = client2.chat.completions.create(
                model="gpt-4-1106-preview",
                response_model=PortfolioSummary,
                messages=[{"role": "user", "content": "Extract account owner name, portfolio value, and the name and cost basis of each holding from the following portfolio summary description text. If missing value or unable to parse the value, make str fields value equal '' ans float field types equal 0:" + content_text}
                ],
                max_tokens=400
            )
            
            print(f"model 2 output:{temp}")

            duration = time.time() - start_time
            print(f"Model 2 API call took {duration:.2f} seconds.")
        return render(request, 'ai/upload_pdf_success.html',{"portfolio_summary": temp})
    else:
        form = PDFUploadForm()

    return render(request, 'ai/upload_pdf.html', {'form': form})

def encode_image_to_base64(image_path):
    print("encoding pdf images to base 64")
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image to base64: {e}")
        return None

def convert_pdf_to_images(pdf_file):
    print("Converting PDF to images")
    output_folder = os.path.join(settings.BASE_DIR, 'pdf_images')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Save the uploaded PDF file temporarily
    pdf_path = os.path.join(output_folder, pdf_file.name)
    image_paths = []
    try:
        # Save the uploaded PDF file temporarily
        pdf_path = os.path.join(output_folder, pdf_file.name)
        with open(pdf_path, 'wb+') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)

        # Convert PDF to images
        doc = fitz.open(pdf_path)
        for page_number in range(len(doc)):
            page = doc.load_page(page_number)
            pix = page.get_pixmap()
            image_path = os.path.join(output_folder, f"page_{page_number}.png")
            pix.save(image_path)
            image_paths.append(image_path)
        doc.close()

        # Remove the PDF file after conversion
        os.remove(pdf_path)
    except Exception as e:
        print(f"Error converting PDF to images: {e}")

    return image_paths