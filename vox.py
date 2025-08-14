import os
import requests
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
VOX_CLIENT_ID = os.getenv("VOX_CLIENT_ID")
VOX_CLIENT_SECRET = os.getenv("VOX_CLIENT_SECRET")
API_ENDPOINT = os.getenv("API_ENDPOINT")
AUTH_URL = os.getenv("AUTH_URL")

def get_bearer_token():
    """
    Get a Bearer token using the client ID and secret from .env file
    """
    if not VOX_CLIENT_ID or not VOX_CLIENT_SECRET or not AUTH_URL:
        raise ValueError("Missing required environment variables. Please check your .env file.")
    
    # Encode credentials for Basic Authentication header
    credentials = f"{VOX_CLIENT_ID}:{VOX_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    payload = {
        "grant_type": "client_credentials"
    }
    
    try:
        response = requests.post(AUTH_URL, headers=headers, data=payload)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Error getting bearer token: {e}")
        return None

def call_vox_api(token,system_prompt, user_input, model_name="gpt-3.5-turbo", max_tokens=1000, temperature=0.7,image=None):
    """
    Call the VOX API with the specified parameters
    
    Args:
        system_prompt (str): The system prompt
        user_input (str): The user input text
        model_name (str): The model to use
        max_tokens (int): Maximum number of tokens to generate
        temperature (float): Temperature parameter for controlling randomness
        
    Returns:
        dict: A dictionary containing the result and token usage information
    """
    if not API_ENDPOINT:
        raise ValueError("API_ENDPOINT is missing in the .env file")
    
    # Get bearer token
    # print(f"Bearer token: {token}")
    if not token:
        return {"status": "error", "result": "Failed to obtain authentication token"}
    
    # Prepare headers with the bearer token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Prepare the payload as per the required structure
    payload = {
        "max_tokens": max_tokens,
        "model": model_name,
        "stream": False,
        "temperature": temperature,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_input
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image
                        }                        
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract data from the response
        return {
            "status": result.get("status"),
            "result": result.get("result"),
            "prompt_tokens": result.get("prompt_tokens"),
            "completion_tokens": result.get("completion_tokens"),
            "total_tokens": result.get("total_tokens")
        }
    except requests.exceptions.RequestException as e:
        print(f"Error calling VOX API: {e}")
        return {"status": "error", "result": str(e)}

# Example usage
if __name__ == "__main__":
    system_prompt = "You are a helpful assistant."
    user_input = "Tell me about artificial intelligence."
    
    response = call_vox_api(system_prompt, user_input, model_name='anthropic.claude-3-5-sonnet-v2:0',max_tokens=1000, temperature=0.7,image=None)
    
    print("Status:", response.get("status"))
    print("Result:", response.get("result"))
    print("Prompt tokens:", response.get("prompt_tokens"))
    print("Completion tokens:", response.get("completion_tokens"))
    print("Total tokens:", response.get("total_tokens"))
