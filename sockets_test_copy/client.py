import asyncio
import websockets

async def send_message():
    uri = "ws://localhost:8080"
    async with websockets.connect(uri) as websocket:
        while True:
            message = input("Escribe una pregunta (o 'salir' para cerrar): ")
            if message.lower() == 'salir':
                break
            
            await websocket.send(message)

            response = await websocket.recv()
            print(f"Respuesta del servidor: {response}")

# Ejecutar el cliente
if __name__ == "__main__":
    asyncio.run(send_message())
