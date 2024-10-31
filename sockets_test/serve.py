import asyncio
import websockets

async def echo(websocket, path):
    async for message in websocket:
        print(f"Mensaje recibido: {message}")
        await websocket.send(f"Echo: {message}")

start_server = websockets.serve(echo, "localhost", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
print("Servidor WebSocket escuchando en ws://localhost:8080")
asyncio.get_event_loop().run_forever()
