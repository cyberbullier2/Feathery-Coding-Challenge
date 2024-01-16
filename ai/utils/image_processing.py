import fitz  # PyMuPDF
import os
import base64
from django.conf import settings

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

def encode_image_to_base64(image_path):
    print("encoding pdf images to base 64")
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image to base64: {e}")
        return None
