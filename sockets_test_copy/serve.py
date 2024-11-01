import asyncio
import websockets
import requests
import json
import os
from langchain_openai import ChatOpenAI
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse, FileResponse
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory

load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
uri = "ws://localhost:8080"
template = """
    Eres un asistente para tareas de preguntas y respuestas. 
    Responde la pregunta lo más detallado y sobretodo resumido posible, basándose únicamente en el contexto proporcionado. Usa como maximo 250 caracteres.
    No se debe consultar información de otros medios como Internet.
    
    Contexto:\n {context}\n
    Pregunta:\n {question}\n
    Respuesta:
    """
prompt = ChatPromptTemplate.from_template(template)
llm = ChatOpenAI(temperature=0, streaming=True)
parser = StrOutputParser()
chain = prompt | llm | parser

chunks = []


async def handle_message(websocket, path):

    async for message in websocket:
        print(f"Pregunta recibida: {message}")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}",
        }
        
        data = {
            "model": "gpt-4o",  # o "gpt-4" si tienes acceso
            "messages": [{"role": "system", "content": "Tu nombre es Xpertus, un robot humanoide peruano y eres un asistente para tareas de preguntas y respuestas.  Responde la pregunta lo más detallado y sobretodo resumido posible, basándose únicamente en el contexto proporcionado. Usa como maximo 250 caracteres. No se debe consultar información de otros medios como Internet."},
                        {"role": "user", "content": message}],
            "stream":True        }
        
        i = 0

        try:
            # Realiza la solicitud a la API de OpenAI con `stream=True` para obtener los datos en tiempo real
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, stream=True)

            # Itera sobre cada línea del contenido en streaming
            for chunk in response.iter_lines():
                if chunk:  # Solo procesa la línea si contiene datos
                    try:
                        # Decodificar cada chunk y eliminar prefijos no deseados
                        chunk_data = json.loads(chunk.decode("utf-8").replace("data: ", ""))
                        
                        # Extrae y muestra únicamente el contenido si está disponible
                        if 'choices' in chunk_data:
                            delta_content = chunk_data['choices'][0]['delta'].get('content')
                            if delta_content:
                                print(delta_content, end="")  # Imprime el contenido en una línea
                                await websocket.send(delta_content.encode("utf-8"))
                    except json.JSONDecodeError:
                        print("Error al decodificar JSON en el chunk.")

        except Exception as e:
            print(f"Otro error: {e}")
        '''i = 0

        try:
            # Realiza la solicitud a la API de OpenAI con `stream=True` para obtener los datos en tiempo real
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, stream=True)

            # Itera sobre cada línea del contenido en streaming
            for chunk in response.iter_lines():
                #if chunk:  # Solo procesa la línea si contiene datos
                    #print(f'{i}: {chunk.decode("utf-8")}')  # Imprime el chunk completo para depurar
                    #i += 1

                    # Intenta decodificar el JSON
                    try:
                        chunk_data = json.loads(chunk.decode("utf-8").replace("data: ", ""))
                        print(chunk_data)
                        # Accede al contenido del mensaje
                        if 'choices' in chunk_data and chunk_data['choices'][0]['delta'].get('content'):
                            content = chunk_data['choices'][0]['delta']['content']
                            print(content, end="")  # Imprime el contenido recibido
                            await websocket.send(content.encode("utf-8"))

                    except json.JSONDecodeError:
                        print("Chunk no es JSON válido")
                        
        except Exception as e:
            print(f"Otro error: {e}")'''

        '''i=0
        while True:    
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, stream=True)
            print(f'{i}' + response.text)
            i+=1'''
        '''try:
            print(response.text)
            for chunk in response:
                print("numero: " + chunk)
                #if 'choices' in chunk and chunk['choices'][0]['delta'].get('content'):
                if chunk.choices[0].delta.content is not None:
                    content = chunk['choices'][0]['delta']['content']
                    print(content, end="")  # Imprime el contenido recibido
                    await websocket.send(content)
        except requests.exceptions.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            await websocket.send("Error: no se recibió una respuesta JSON válida".encode("utf-8"))
        except Exception as e:
            print(f"Otro error: {e}")
            await websocket.send(f"Error: {e}".encode("utf-8"))'''
        '''try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, stream=True)

            if response.status_code == 200:
                print(response.status_code)
                #full_response = response.text
                #print(f"Respuesta completa: {full_response}")
                response_data = response.text
                print(response_data)
                
                for chunk in response:
                    #if 'choices' in chunk and chunk['choices'][0]['delta'].get('content'):
                    if 'choices' in chunk and chunk['choices'][0]['delta']['content'] is not None:
                        content = chunk['choices'][0]['delta']['content']
                        print(content, end="")  # Imprime el contenido recibido
                        await websocket.send(content)
            else:
                print(f"Error en la respuesta: {response.status_code} - {response.text}")
                await websocket.send(f"Error: {response.status_code} - {response.text}".encode("utf-8"))

        except requests.exceptions.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            await websocket.send("Error: no se recibió una respuesta JSON válida".encode("utf-8"))
        except Exception as e:
            print(f"Otro error: {e}")
            await websocket.send(f"Error: {e}".encode("utf-8"))'''



        '''try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
            
            # Verificar si el tipo de contenido es JSON antes de decodificar response.status_code == 200 and response.headers["Content-Type"] == "application/json"
            if response.status_code == 200 :
                print(response.status_code)
                #response_data = response.json()
                for chunk in response:
                    if 'choices' in chunk and chunk['choices'][0]['delta'].get('content'):
                        content = chunk['choices'][0]['delta']['content']
                        print(content, end="")  # Imprime el contenido recibido
                        await websocket.send(content)
            else:
                print(f"Error en la respuesta: {response.status_code} - {response.text}")
                await websocket.send(f"Error: {response.status_code} - {response.text}")

        except requests.exceptions.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            await websocket.send("Error: no se recibió una respuesta JSON válida")
        except Exception as e:
            print(f"Otro error: {e}")
            await websocket.send(f"Error: {e}")'''
        

        '''try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
            if response.status_code == 200:
                response_data = response.json()
                for chunk in response_data:
                    if chunk.choices[0].delta.content is not None:
                        print(chunk['choices'][0]['delta']['content'], end="")
                    #await websocket.send(json.dumps(chunk))
            else:
                print(f"Error en la respuesta: {response.status_code} - {response.text}")
                await websocket.send(f"Error: {response.status_code} - {response.text}")
        except requests.exceptions.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            await websocket.send("Error: no se recibió una respuesta JSON válida")'''

        #without streaming
        '''response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            #response_data=response.text
            response_data = response.json()
            response_data1 = response.text
            print(response_data1)
            #for chunk in response_data:
                #if chunk.choices[0].delta.content is not None:
                #    print(chunk.choices[0].delta.content, end="")
                #print(chunk.choices[0].delta)
            #answer = response.choices[0].message.content
            answer = response_data['choices'][0]['message']['content']
            await websocket.send(answer)
        else:
            await websocket.send(f"Error: {response.status_code} - {response.text}")'''

async def main():
    async with websockets.serve(handle_message, "localhost", 8080):
        print("Servidor WebSocket escuchando en ws://localhost:8080")
        await asyncio.Future()  

if __name__ == "__main__":
    asyncio.run(main())
