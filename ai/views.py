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
            except Exception as e:
                return HttpResponse("Failed to convert PDF to images.")

            # defensive check for empty pdf
            if not image_paths:
                return HttpResponse("Cannot upload empty pdf")

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
                    messages[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})
                    continue
                else:
                    return HttpResponse("Failed to encode one or more images.")

            # Make API call



            client1 = OpenAI(api_key=config('OPENAI_API_KEY'))
            client2 = instructor.patch(OpenAI(api_key=config('OPENAI_API_KEY')))
            response = client1.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=4096
            )

            content_text = response.choices[0].message.content
            print(f"model 1 output:{content_text}")
            temp = client2.chat.completions.create(
                model="gpt-4",
                response_model=PortfolioSummary,
                messages=[{"role": "user", "content": "Extract account owner name, portfolio value, and the name and cost basis of each holding from the following portfolio summary description text. If missing value or unable to parse the value, make field value equal 'None' type:" + content_text}
                ],
                max_tokens=4096
            )
            print(f"model 2 output:{temp}")





            # Process the response as needed
            # ...

            # Render a response page or redirect as necessary
            # ...
        # print(response)
        return render(request, 'ai/upload_pdf_success.html',{"portfolio_summary": temp})
    else:
        form = PDFUploadForm()

    return render(request, 'ai/upload_pdf.html', {'form': form})

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image to base64: {e}")
        return None

def convert_pdf_to_images(pdf_file):
    output_folder = 'path_to_output_folder'
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