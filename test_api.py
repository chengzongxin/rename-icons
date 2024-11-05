import requests

API_KEY = '68b4675e-e074-4268-b661-f87af28293eb'
API_ENDPOINT = 'https://api.deepai.org/api/text2img'

# Test API connection
headers = {
    'api-key': API_KEY
}

try:
    response = requests.get(
        'https://api.deepai.org/api/models',
        headers=headers
    )
    print("Available APIs:")
    print(response.json())
except Exception as e:
    print(f"Error: {str(e)}") 