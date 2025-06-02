import base64
import requests
from config import OPENAI_API_KEY

URL = "https://api.openai.com/v1/responses"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}

def describe_image_openai(image_path):
    with open(image_path, "rb") as img:
        encoded = base64.b64encode(img.read()).decode("utf-8")
    data = {
        "model": "gpt-4.1-mini",
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Describe la escena brevemente para una persona ciega."},
                    {"type": "input_image", "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}},
            ]}
        ],
        # "max_tokens": 100
    }

    response = requests.post(URL, headers=HEADERS, json=data)

    if response.status_code == 200:
        result = response.json()
        print(result['choices'][0]['message']['content'])
        return response.json()["choices"][0]["message"]["content"]
    else:
        print("Request failed, error code:", response.status_code)
        print("Response:", response.text)
        return "Error al describir la imagen."

