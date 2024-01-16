from openai import OpenAI
import time
from ..models.portfolio import PortfolioSummary
from ..prompts import create_text_model_prompt,VISION_MODEL_PROMPT  

import instructor

def call_openai_vision_model(encoded_images, api_key):
    client = OpenAI(api_key=api_key)
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": VISION_MODEL_PROMPT,
                },
            ],
        }
    ]
    
    for base64_image in encoded_images:
        if base64_image:
            messages[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}})
        else:
            return None  # Return None if any image fails to encode

    try:
        start_time = time.time()
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=1000
        )
        duration = time.time() - start_time
        print(f"Vision model API call took {duration:.2f} seconds.")
        return response
    except Exception as e:
        print(f"Error calling OpenAI Vision model: {e}")
        return None

def call_openai_text_model(vision_response, api_key):
    # Logic to call the text model
    content_text = vision_response.choices[0].message.content
    client = instructor.patch(OpenAI(api_key=api_key))
    try:
        start_time = time.time()
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            response_model = PortfolioSummary,
            messages=[{"role": "user", "content": create_text_model_prompt(content_text)}],
            max_tokens=400
        )
        duration = time.time() - start_time
        print(f"Text model API call took {duration:.2f} seconds.")
        return response
    except Exception as e:
        print(f"Error calling OpenAI Text model: {e}")
        return None

