# endpoints/chat.py
import requests
from typing import List, Optional
from logging_config import logger  # Import the logger

from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse

from auth import verify_firebase_token
from utils.initialize import DANSWER_BASE_URL, load_api_endpoints, load_prompt_sequence
from config.headers import get_headers

from .upload_protocol import upload_protocol
from config.base_chat_payload import get_base_payload
from utils.parsing import extract_json_from_message, extract_json_markdown, collect_streamed_response

router = APIRouter()

# Load API endpoints
api_endpoints = load_api_endpoints()


def create_chat_session(headers=get_headers()):
    logger.info("Creating chat session...")
    url_create_chat_session = f"{DANSWER_BASE_URL}{api_endpoints['create_chat_session']}"
    payload = {
        "persona_id": 0,
        "description": "New chat session"
    }
    response = requests.post(url_create_chat_session, json=payload, headers=headers)
    logger.debug(f"Create chat session response status: {response.status_code}")
    if response.status_code != 200:
        logger.error(f"Error creating chat session: {response.text}")
        return None, response
    chat_session_id = response.json().get("chat_session_id")
    logger.info(f"Chat session ID: {chat_session_id}")
    return chat_session_id, response

def get_prompt_content(prompt_name, headers):
    logger.info(f"Retrieving prompt content for '{prompt_name}'...")
    url_input_prompt = f"{DANSWER_BASE_URL}{api_endpoints['input_prompt']}"
    response = requests.get(url_input_prompt, headers=headers)
    logger.debug(f"Get input prompt response status: {response.status_code}")
    if response.status_code != 200:
        logger.error(f"Error retrieving prompts: {response.text}")
        return None, response
    prompts = response.json()
    for prompt in prompts:
        if prompt.get("prompt") == prompt_name:
            prompt_content = prompt.get("content", "")
            logger.info(f"Found prompt content: {prompt_content}")
            return prompt_content, response
    logger.warning(f"Prompt '{prompt_name}' not found")
    return None, None

def send_chat_message(payload, headers):
    logger.info("Sending chat message...")
    url_send_message = f"{DANSWER_BASE_URL}{api_endpoints['send_message']}"
    response = requests.post(url_send_message, json=payload, headers=headers)
    logger.debug(f"Send message response status: {response.status_code}")
    return response


@router.post("/chat")
async def chat_endpoint(
    user_request: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    token_data=Depends(verify_firebase_token)
):
    headers = get_headers()

    # Load prompt sequence
    prompts = load_prompt_sequence()
    protocol_reviewer_prompt, protocol_action_prompt = prompts[0], prompts[1]

    # Step 1: Upload files if provided
    file_descriptors = []
    if files:
        upload_response = await upload_protocol(files=files, token_data=token_data)
        if "files" not in upload_response:
            logger.error("Failed to upload files, unexpected response format")
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Failed to upload files",
                    "error": upload_response.get("error", "Unknown error")
                }
            )

        file_descriptors = [
            {"id": file_info["id"], "type": file_info["type"], "name": file_info["name"]}
            for file_info in upload_response["files"]
        ]
        logger.debug(f"File descriptors for uploaded files: {file_descriptors}")

    # Step 2: Create chat session
    chat_session_id, response = create_chat_session()
    if not chat_session_id:
        logger.error("Failed to create chat session")
        return JSONResponse(
            status_code=response.status_code,
            content={"detail": "Failed to create chat session", "error": response.text}
        )

    # Step 3: Prepare and send initial message
    message = protocol_reviewer_prompt + user_request
    logger.info(f"Initial message to send: {message}")
    base_payload = get_base_payload(chat_session_id)
    payload = base_payload.copy()
    payload.update({
        "parent_message_id": None,
        "message": message,
        "file_descriptors": file_descriptors  # Attach file descriptors here
    })

    response = send_chat_message(payload, headers)
    if response.status_code != 200:
        logger.error(f"Error sending initial message: {response.text}")
        return JSONResponse(
            status_code=response.status_code,
            content={"detail": "Failed to send message", "error": response.text}
        )

    last_message_data = collect_streamed_response(response)
    if not last_message_data:
        logger.error("Failed to process initial response in streaming")
        return JSONResponse(status_code=500, content={"detail": "Failed to process initial response"})
    else:
        logger.info(f"Last message data no.1: {last_message_data}")
    protocol_summary = extract_json_from_message(last_message_data.get('message'))
    logger.info(f"Extracted protocol summary: {protocol_summary}")

    parent_message_id = last_message_data.get('parent_message')
    reserved_assistant_message_id = parent_message_id + 1 if parent_message_id is not None else None
    logger.info(f"Reserved assistant message ID: {reserved_assistant_message_id}")

    if reserved_assistant_message_id is None:
        logger.error("Failed to calculate reserved_assistant_message_id")
        return JSONResponse(status_code=500, content={"detail": "Failed to calculate reserved_assistant_message_id"})

    message2 = protocol_action_prompt
    logger.info(f"Second message to send: {message2}")

    payload2 = base_payload.copy()
    payload2.update({
        "parent_message_id": reserved_assistant_message_id,
        "message": message2,
        "file_descriptors": []
    })

    response = send_chat_message(payload2, headers)
    if response.status_code != 200:
        logger.error(f"Error sending second message: {response.text}")
        return JSONResponse(
            status_code=response.status_code,
            content={"detail": "Failed to send second message", "error": response.text}
        )

    last_message_data2 = collect_streamed_response(response)
    if not last_message_data2:
        logger.error("Failed to process second response in streaming")
        return JSONResponse(status_code=500, content={"detail": "Failed to process second response"})
    else:
        logger.info(f"Last message data no.2: {last_message_data2}")

    final_protocol_summary = extract_json_from_message(last_message_data2.get('message'))
    logger.info(f"Final protocol summary: {final_protocol_summary}")

    if not final_protocol_summary:
        logger.error("Failed to extract final protocol summary from response")
        return JSONResponse(status_code=500, content={"detail": "Failed to extract final protocol summary from response"})

    return final_protocol_summary