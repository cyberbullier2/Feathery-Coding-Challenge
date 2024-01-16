# Coding Challenge

## Demo

(https://drive.google.com/file/d/1kJLowmdeDNbRQKyOerfQRp7FiPweySIK/view?usp=sharing)

## Implementaion Discussion

![High level design diagram](/high_level.png)

1. Client uploads their portfolio summary PDF via the view accesible at ```http://127.0.0.1:8000/ai/upload_pdf/```. Invokes upload_pdf POST endpoint.
   - Added logic to prevent non pdf file type uploads

2. Convert pdf files into png images ```ai/utils/image_processing.py``` 
   - Store PDF on local disk since [third party library]([url](https://pymupdf.readthedocs.io/en/latest/module.html)) I leveraged to convert from PDF to PNG format don't support reading files from remote URLs or streams directly.
   - Read PDF pages from disk, convert into .png format, save images on disk.
   - Locally stored PDF is deleted after.
3. Encode png images to base64 encoding  ```ai/utils/image_processing.py``` 
   - start building part of the messages payload for the open ai ```GPT4-vision-preview``` model api request by aggregating base64 encodings of the .png images.
4. Using Open AIs developer API, use ```GPT4-vision-preview``` model ```ai/utils/openai_helpers.py```
   - The response from the model is the chat response(String) when given the prompt below + based 64 encodings of our images
      - prompt: "Visually interpret the account owner name, portfolio value of the portfolio and the name and cost basis of each holding."
      - collection of the base64 encodings of the .png images.
      - ```max_tokens``` set to 1000.
  
6. Using Open AIs developer API, use ```GPT4-turbo``` model ```ai/utils/openai_helpers.py```
   - The purpose of this model is given the unstructured response of the  ```GPT4-vision-preview``` model, extract account owner name, portfolio value, and the name and cost basis of each holding.
      - Response strictly follows the structure of custom model type named ```PortfolioSummary```,found in ```ai/models/portfolio.py```
7. Render Response
    - Data client wanted to know about various financial records of uploaded PDF is now in structured format. Render success view showing these financial records.

## Design Process

1. How did you choose your prompts?
  - Prompt selection was tricky due to many factors( more on this in limitation section)
  - I heavily referenced [the open ai promp engineering guide]([url](https://platform.openai.com/docs/guides/prompt-engineering/six-strategies-for-getting-better-results))
  - Prompt for the vision model: ""Visually interpret the account owner name, portfolio value of the portfolio and the name and cost basis of each holding. Don't respond saying you're unable to assist with this request."
    - This prompt was able to accuratley extract the account owner name and portfolio value, but struggled interpretting holdings
    - Firstly I tried[ splitting the prompt into sub-prompts ]([url](https://platform.openai.com/docs/guides/prompt-engineering/strategy-split-complex-tasks-into-simpler-subtasks)), feeding those sub-prompts into the vision model, then aggregating the results. In theory this should result in a less complex prompt hence more accurate model response. Unfortunatley, this was not the case as I found the model struggling to interpret holdings .
    - Secondly, I tried incorporating [reference text]([url](https://platform.openai.com/docs/guides/prompt-engineering/strategy-provide-reference-text)) pertaining to definition of holdings. No noticable changes to how the model interpreted holdings.
   - Prompt for text model: "Extract account owner name, portfolio value, and the name and cost basis of each holding from the following portfolio summary description text. If missing value or unable to parse the value, make str fields value equal '' ans float field types equal 0: {response_text}"
      - Unlike the vision model prompt, this prompt yielded favourable model results
      - Gave additional instructions in the case of empty fields when extracting data with respect to holdings
3. How did you approach testing?
   - I approached testing mainly through manual testing with the sample investment statement pdf, incorrect file formats. If given more time I would prioritize unit and integration tests
4. Did you make any decisions on engineering tradeoffs?
     - A solution with a high latency + simpler to implement over a more complex solution with lower latency
          - Latency for both model API calls were high, ranging between 10-30 seconds
          - The high latency, simple solution was chosen due to the 24hr time constraint of the challenge and limited amount of open ai challenge I had access to this challenge(~40 cents for a full request loop!). Trying to develop a more performant solution(asynchronous open ai calls) would cost a lot of API credits, which I did not have.
     - Focused more on document extraction over the overall visual aesthetic of my solution.
            - Time constraint
            -  Importance of the document extraction feature
     - Focused on single use over being able to handle large client volume
          - Solution I proposed was built on local django server on personal machine. Launching my service to handle a large volume of requests would be too resource intensive for a coding challenge
       

## Limitations

1. Asset storage done locally on disk
2. High model latecy(10-30s per model)
3. Limited number of times I can manually test end-to-end in order to optimize accuracy and latency(costs ~ 43 cents of credit to test end-to-end, 10/.43 ~= 23 end-to-end tests before I ran out of credit)
4. Innacurate vision model response when interpreting "holdings"
   

## Areas to improve

1. Store assets in blobstore(S3) > local disk
2. Break prompts into chunks such that models can asychronously process the chunked prompts,independently
3. If high load, talk about how to leverage a load balancer and multiple application servers to distribute client volume

