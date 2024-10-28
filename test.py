import torch
import os
import time
from transformers import pipeline
from in_out_tokenizer import tokenize_input

current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)  
pipe = pipeline(
    "text-generation", 
    model=current_directory, 
    torch_dtype=torch.bfloat16, 
    device_map="auto",
    temperature=0.2,
    max_new_tokens=200,
    top_k=5,
    top_p=0.95) 
'''
    temperature=0.9,     # Ajusta la temperatura para respuestas más coherentes
    top_k=100,            # Limita las opciones de token
    top_p=0.95'''

'''prompt = (
    "Eres un poeta que escribe mensajes románticos y poemas. Manda un saludo a la enamorada de quien le pregunta y crea un poema para ella. "
)'''
messageStructure1 = [
    {"role": "system", "content": "Tu nombre es Xpertus y eres un asistente multitareas capaz de responder las dudas con claridad y brindar soporte si te lo piden, debes responder a todas las preguntas sin repetir la misma pregunta en tu respuesta, tus respuestas deben ser concisas. Limita tus respuestas a menos de 100 palabras."},
    {"role": "user", "content": "Dime cual es el sentido de la vida"},
]

#Escribe una cancion para mi enamorada Maricielo"
for i in range(4):
    start = time.time()
    question = "How to solve a quadratic equation?"
    #input_text = prompt + question  # Combina el prompt con la pregunta
    #output = pipe(input_text)
    #output = pipe(tokenize_input("Xpertus tienes emociones?"))
    output = pipe(messageStructure1, batch_size=8)
    #print("La pregunta es: " + question)
    #print(output[0]['generated_text'])
    response=output[0]['generated_text'][-1]
    print(response['content'])
    end = time.time()
    print(f"Tiempo de ejecución: {end-start:.4f} segundos")     