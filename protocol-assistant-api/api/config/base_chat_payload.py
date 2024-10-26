def get_base_payload(chat_session_id):
    # Base payload for chat messages
    base_payload = {
        "alternate_assistant_id": 0,
        "chat_session_id": chat_session_id,
        "parent_message_id": None,  # Will be updated per message
        "message": "",              # Will be updated per message
        "prompt_id": 0,
        "search_doc_ids": None,
        "file_descriptors": [],     # Will be updated if files are provided
        "regenerate": False,
        "retrieval_options": {
            "run_search": "auto",
            "real_time": True,
            "filters": {
                "source_type": None,
                "document_set": None,
                "time_cutoff": None,
                "tags": []
            }
        },
        "prompt_override": None,
        "llm_override": None
    }
    return base_payload