from utils import DANSWER_ADMIN_API_KEY

def get_headers():
    return {
        "Authorization": f"Bearer {DANSWER_ADMIN_API_KEY}",
        "Content-Type": "application/json",
        "Accept-Language": 'en-US,en;q=0.9',
        'Accept': '*/*'
    }