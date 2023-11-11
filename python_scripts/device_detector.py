import base64
import requests
from dotenv import load_dotenv
import os

# This section of code is based on chatGPT documentation (https://platform.openai.com/docs/guides/vision)


# Default GTP endpoint to make requests to
GPT_ENDPOINT = "https://api.openai.com/v1/chat/completions"

# OpenAI API Key
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')


# Function to encode the image in base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def prepare_headers(api_key):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    return headers


# Format the payload to be sent to the endpoint
def prepare_payload(prompt, base64_image):
    payload = {
        "model": "gpt-4-vision-preview",

        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    return payload


# Uses a vision AI to detect the device contained in the photo
def detect_device(base64_image):
    # Prepare a prompt to get the device name in the desired structure
    prompt = '''
        Describe in maximum 3 words the object that is present into the image. 
        Try to be specific about the name and the model. Do not include description about the color of the object.
        '''

    # Add the prompt to the payload
    payload = prepare_payload(prompt, base64_image)

    # Make a request to the remote server
    response = requests.post(GPT_ENDPOINT, headers=prepare_headers(api_key), json=payload)

    print(response.json()['choices'][0]['message']['content'])
    return response.json()['choices'][0]['message']['content']


if __name__ == '__main__':
    with open("random.txt", "w") as f:
        f.write( encode_image("images.jpeg"))
    print(detect_device(encode_image("images.jpeg")))
