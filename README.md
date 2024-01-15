# Coding Challenge


## Implementaion Discussion

![High level design diagram](/high_level.png)

1. Client uploads their portfolio summary PDF via the view accesible at ```http://127.0.0.1:8000/ai/upload_pdf/```. Invokes upload_pdf POST endpoint.
2. Business logic in ```ai/views.py``` converts pdf into PNG images. This is done by the ```convert_pdf_to_images``` helper function.
   - Store PDF on local disk since third party library I leverage to convert from PDF to PNG format don't support reading files from remote URLs or streams directly.
   - Read PDF pages from disk, convert into .png format, save images on disk.
   - Locally stored PDF is deleted after.
3. Buisiness logic in ```ai/views.py``` encodes .png images to base64.
   - start building payload for the open ai ```GPT4-vision-preview``` model api request by aggregating base64 encodings of the .png images.
4. Invoke ```GPT4-vision-preview``` model. High level payload design below:
   - prompt: ```Visually interpret the account owner name, portfolio value of the portfolio and the name and cost basis of each holding.```
   - collection of the base64 encodings of the .png images.
   - ```max_tokens``` set to 1000.
  
5. Invoke ```GPT4``` model. The purpose of feeding the response of the previous model into a new model is to further structure the data, making it easier to extract. High level payload design below:
   - prompt: ```Extract account owner name, portfolio value, and the name and cost basis of each holding from the following portfolio summary description text: {INSERT GPT4-vision-preview model response content text here}.```
   - set ```response_model``` parameter with a custom data type in order to extracted structured data from the by default unstructered model response
   - ```max_tokens``` set to 300. Expecting a shorter response than the previous ```GPT4-vision-preview``` model request.
6. Data client wanted to know about initial PDF is now in strctured format. Render success view showing the structured data.
