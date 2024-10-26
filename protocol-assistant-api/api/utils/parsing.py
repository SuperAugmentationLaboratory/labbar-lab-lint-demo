import re
import json
from logging_config import logger  # Import the logger
def extract_json_markdown(text):
    pattern = r'```json(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        json_str = matches[0]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
    return None
  
# Enhanced collect_streamed_response function with detailed logging
def collect_streamed_response(response):
    logger.info("Collecting streamed response...")
    messages = []
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            logger.debug(f"Received line: {decoded_line}")  # Log each received line for debugging
            try:
                message_json = json.loads(decoded_line)
                messages.append(message_json)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e} - Line content: {decoded_line}")  # Log the exact line causing issues
                continue  # Skip this line and continue to the next one

    if messages:
        last_message = messages[-1]
        logger.debug(f"Last streamed message: {last_message}")
        return last_message
    else:
        logger.warning("No valid messages received in stream")
        return None
    
def extract_json_from_message(message_text):
    try:
        json_data = json.loads(message_text)
        return json_data
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return None