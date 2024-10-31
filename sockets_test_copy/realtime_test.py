import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

# Cargar la clave API desde el archivo .env
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# URL de la API
url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"

async def send_message(ws, user_message):
    """Envía el mensaje del usuario al WebSocket."""
    create_conversation_event = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": user_message
                }
            ]
        }
    }
    
    create_response_event = {
        "type": "response.create",
        "response": {
            "modalities": ["text"],
            "instructions": "Please assist the user."
        }
    }
    
    await ws.send(json.dumps(create_conversation_event))
    await ws.send(json.dumps(create_response_event))

async def handle_message(message_str):
    """Maneja e imprime las respuestas en tiempo real desde el WebSocket."""
    message = json.loads(message_str)
    
    if message["type"] == "response.text.delta":
        print(message.get("delta"), end="", flush=True)
    elif message["type"] == "response.text.done":
        print("\n")
    elif message["type"] == "response.done":
        print("Respuesta completada.\n")

async def interactive_session():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    last_question = None  # Para almacenar la última pregunta

    while True:
        try:
            # Iniciar conexión WebSocket
            async with websockets.connect(url, extra_headers=headers, ping_interval=30, ping_timeout=20) as ws:
                print("Conexión establecida con OpenAI Realtime API")
                
                # Si hay una última pregunta, reenviarla automáticamente
                if last_question:
                    await send_message(ws, last_question)
                
                while True:
                    # Leer entrada del usuario solo si no hay una pregunta pendiente
                    if not last_question:
                        user_input = input("Escribe tu pregunta (o 'exit' para salir): ")
                        if user_input.lower() == 'exit':
                            print("Cerrando conexión...")
                            return
                        last_question = user_input  # Guardar la pregunta

                    await send_message(ws, last_question)  # Enviar la última pregunta
                    
                    # Manejar los mensajes de la API en tiempo real
                    async for message in ws:
                        await handle_message(message)
                        
                        # Si la respuesta ha terminado, limpiar la última pregunta
                        if message == '{"type": "response.done"}':
                            last_question = None
                            break
                        
        except websockets.ConnectionClosedError as e:
            print(f"Conexión perdida: {e}. Reintentando en 5 segundos...")
            await asyncio.sleep(5)

# Ejecutar la sesión interactiva
asyncio.run(interactive_session())

