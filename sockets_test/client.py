import asyncio
import websockets

async def send_message():
    uri = "ws://localhost:8080"
    async with websockets.connect(uri) as websocket:
        message = input("Escribe un mensaje para enviar: ")
        await websocket.send(message)
        response = await websocket.recv()
        print(f"Respuesta del servidor: {response}")

# Ejecutar el cliente
asyncio.get_event_loop().run_until_complete(send_message())
