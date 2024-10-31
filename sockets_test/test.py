import requests
import json
#from concurrent.futures import ThreadPoolExecutor
import aiohttp
import asyncio
import websockets
import time
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
from callback import StreamingLLMCallbackHandler
import uvicorn
load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")
uri = "ws://localhost:8080"
def get_conversational_chain(retriever):
    prompt_template = """
    Eres un asistente para tareas de preguntas y respuestas. 
    Responde la pregunta lo más detallado y sobretodo resumido posible, basándose únicamente en el contexto proporcionado. Usa como maximo 250 caracteres.
    No se debe consultar información de otros medios como Internet.
    
    Contexto:\n {context}\n
    Pregunta:\n {question}\n
    Historia:\n {history}\n
    Respuesta:
    """

    model = ChatOpenAI(
            model_name = 'gpt-4o',
            temperature = 0,
            verbose = False,
            openai_api_key = openai_api_key,
            model_kwargs={"top_p": 0.3}
        )
    prompt = PromptTemplate(template=prompt_template,
                            input_variables=["context", "history","question"])
    #embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    system_memory = ConversationBufferMemory(memory_key='history', input_key="question")
    chain = RetrievalQA.from_chain_type(llm=model, 
                                        chain_type="stuff",
                                        retriever=retriever,
                                        chain_type_kwargs = {
                                        "verbose": False,
                                        "prompt": prompt,
                                        "memory": system_memory
                                    })
    return chain


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

app = FastAPI()

chunks = []
async def generate_chat_responses(message):
    async for chunk in chain.astream(message):
        content = chunk.replace("\n", "<br>")
        chunks.append(chunk)
        print(chunk.content, end="|", flush=True)
        yield f"data: {content}\n\n"


'''@app.get("/")
async def root():
    return FileResponse("static/index.html")'''


@app.get("/chat_stream/{message}")
async def chat_stream(message: str):
    return StreamingResponse(generate_chat_responses(message=message), media_type="text/event-stream")


async def send_message():
    uri = "ws://localhost:8080"
    async with websockets.connect(uri) as websocket:
        message = input("Escribe un mensaje para enviar: ")
        await websocket.send(message)
        response = await websocket.recv()
        print(f"Respuesta del servidor: {response}")


asyncio.get_event_loop().run_until_complete(send_message())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    stream_handler = StreamingLLMCallbackHandler(websocket)
    qa_chain = get_chain(stream_handler)

    while True:
        try:
            # Receive and send back the client message
            user_msg = await websocket.receive_text()
            resp = ChatResponse(sender="human", message=user_msg, type="stream")
            await websocket.send_json(resp.dict())

            # Construct a response
            start_resp = ChatResponse(sender="bot", message="", type="start")
            await websocket.send_json(start_resp.dict())

            # Send the message to the chain and feed the response back to the client
            output = await qa_chain.acall(
                {
                    "input": user_msg,
                }
            )

            # Send the end-response back to the client
            end_resp = ChatResponse(sender="bot", message="", type="end")
            await websocket.send_json(end_resp.dict())
        except WebSocketDisconnect:
            logging.info("WebSocketDisconnect")
            # TODO try to reconnect with back-off
            break
        except ConnectionClosedOK:
            logging.info("ConnectionClosedOK")
            # TODO handle this?
            break
        except Exception as e:
            logging.error(e)
            resp = ChatResponse(
                sender="bot",
                message="Sorry, something went wrong. Try again.",
                type="error",
            )
            await websocket.send_json(resp.dict())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)