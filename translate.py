import requests

def translate_text(text, target_language):
    api_url = 'https://api.example.com/translate'
    params = {
        'api_key': 'your_api_key_here',
        'text': text,
        'target_lang': target_language
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        return response.json()['translated_text']
    else:
        return "Error: Unable to translate"

# Example usage
translated_text = translate_text("Hello, world!", "es")
print(translated_text)
