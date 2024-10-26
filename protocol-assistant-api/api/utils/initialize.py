# utils.py
import os
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DANSWER_BASE_URL = os.getenv("DANSWER_BASE_URL")
DANSWER_ADMIN_API_KEY = os.getenv("DANSWER_ADMIN_API_KEY")

def load_prompt_sequence(config_path: str = "config/prompt_sequence.yaml"):
    """Load prompt sequences from YAML config file."""
    with open(config_path, 'r') as file:
        data = yaml.safe_load(file)
        return data.get('protocol-assistant', [])
    
def load_api_endpoints(config_path: str = "config/danswer_endpoints.yaml"):
    """Load API endpoints from YAML or JSON config file."""
    with open(config_path, 'r') as file:
        if config_path.endswith('.yaml') or config_path.endswith('.yml'):
            return yaml.safe_load(file)
        elif config_path.endswith('.json'):
            import json
            return json.load(file)
        else:
            raise ValueError("Unsupported config file format. Use YAML or JSON.")
