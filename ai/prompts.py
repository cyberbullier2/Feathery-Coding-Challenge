
# Static prompt
VISION_MODEL_PROMPT = "Visually interpret the account owner name, portfolio value of the portfolio and the name and cost basis of each holding. Don't respond saying you're unable to assist with this request."

# Dynamic prompt, based on VISION_MODEL_PROMPT
def create_text_model_prompt(response_text):
    return f"Extract account owner name, portfolio value, and the name and cost basis of each holding from the following portfolio summary description text. If missing value or unable to parse the value, make str fields value equal '' ans float field types equal 0: {response_text}"
