from django.core.exceptions import ValidationError
from django import forms

class PDFUploadForm(forms.Form):
    pdf_file = forms.FileField()

    def clean_pdf_file(self):
        file = self.cleaned_data['pdf_file']
        if not file.name.endswith('.pdf'):
            raise ValidationError("Only PDF files are allowed.")
        return file
