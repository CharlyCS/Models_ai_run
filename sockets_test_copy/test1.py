from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "hola"}],
    stream=True,
)
print(stream)
for chunk in stream:
    print(chunk)
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")