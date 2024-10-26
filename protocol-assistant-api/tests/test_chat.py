# /tests/test_chat.py

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

# Mock responses
mock_upload_response = {
    "files": [
        {
            "id": "f926076c-9fb8-4d94-9a3a-c9dacce24082",
            "type": "plain_text",
            "name": "Polymerase-Chain-Reaction-Protocol.pdf"
        }
    ]
}

mock_create_chat_session_response = {
    "chat_session_id": "ac759d14-3a51-4c43-a149-018f95ec3d08"
}

mock_send_message_response = {
    "parent_message": 1,
    "message": "{\"summary\": \"This is a protocol summary.\"}"
}

# Patching dependencies in the chat route
@patch("api.routes.chat.upload_protocol", new_callable=AsyncMock)
@patch("api.routes.chat.create_chat_session")
@patch("api.routes.chat.send_chat_message")
@patch("api.routes.chat.collect_streamed_response")
def test_chat_endpoint(mock_collect_streamed_response, mock_send_chat_message, mock_create_chat_session, mock_upload_protocol):
    # Step 1: Mock upload_protocol function
    mock_upload_protocol.return_value = mock_upload_response
    # Step 2: Mock create_chat_session function
    mock_create_chat_session.return_value = (mock_create_chat_session_response["chat_session_id"], None)
    # Step 3: Mock send_chat_message function for initial and secondary messages
    mock_send_chat_message.return_value = AsyncMock(status_code=200)
    # Step 4: Mock collect_streamed_response for sequential responses
    mock_collect_streamed_response.side_effect = [
        mock_send_message_response,  # First response for initial message
        mock_send_message_response   # Second response for action message
    ]

    # Test data
    user_request = "This is a user request."
    files = [("files", ("Polymerase-Chain-Reaction-Protocol.pdf", b"File content", "application/pdf"))]

    # Send request to the /chat endpoint
    response = client.post(
        "/api/chat",
        data={"user_request": user_request},
        files=files
    )

    # Assertions
    assert response.status_code == 200
    response_data = response.json()
    assert "summary" in response_data
    assert response_data["summary"] == "This is a protocol summary."

    # Check that each function was called as expected
    mock_upload_protocol.assert_called_once()
    mock_create_chat_session.assert_called_once()
    assert mock_send_chat_message.call_count == 2
    assert mock_collect_streamed_response.call_count == 2
