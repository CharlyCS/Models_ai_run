# app.py
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import asyncio
from dotenv import load_dotenv
load_dotenv()

# Access the variables using os.environ
openai_api_key = os.environ.get("OPENAI_API_KEY")
app = FastAPI()

# Configuración de LangChain y OpenAI
#openai_api_key = "YOUR_OPENAI_API_KEY"
#os.environ["OPENAI_API_KEY"] = openai_api_key

# Configuración de la plantilla de prompt
prompt_template = PromptTemplate(input_variables=["input_text"], template="Haz una predicción: {input_text}")
llm = ChatOpenAI(model_name = 'gpt-4o',temperature=0.7, streaming=True) 
chain = prompt_template | llm

# HTML básico para probar el WebSocket
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>FastAPI WebSocket con OpenAI</title>
    </head>
    <body>
        <h1>WebSocket Test</h1>
        <textarea id="input" placeholder="Escribe algo aquí..."></textarea>
        <button onclick="sendMessage()">Enviar</button>
        <ul id='messages'></ul>
        <script>
            const ws = new WebSocket("ws://localhost:8000/ws");

            ws.onmessage = function(event) {
                const messages = document.getElementById('messages');
                const message = document.createElement('li');
                message.textContent = event.data;
                messages.appendChild(message);
            };

            function sendMessage() {
                const input = document.getElementById("input");
                ws.send(input.value);
                input.value = '';
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            
            # Llama al modelo de LangChain en modo streaming
            async for response_chunk in chain.astream({"input_text": data}, return_only_outputs=True):
                print(response_chunk.content, end="",flush=True)
                await websocket.send_text(response_chunk.content)
                
    except WebSocketDisconnect:
        print("WebSocket se ha desconectado")
    except Exception as e:
        print(f"Error: {e}")
        
