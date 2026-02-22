
# TESTE MODELOS DISPONÍVEIS GOOGLE

# import os
# from dotenv import load_dotenv
# import google.generativeai as genai

# # Carrega a chave do .env
# load_dotenv()
# chave = os.getenv("GOOGLE_API_KEY")

# if not chave:
#     print("Erro: Chave não encontrada no .env!")
# else:
#     genai.configure(api_key=chave)
#     print("--- MODELOS DISPONÍVEIS PARA A SUA CHAVE ---")
    
#     # Lista todos os modelos que suportam geração de texto/chat
#     for m in genai.list_models():
#         if 'generateContent' in m.supported_generation_methods:
#             print(m.name)

# TESTE MODELOS DISPONÍVEIS GROQ

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
chave = os.getenv("GROQ_API_KEY")

if not chave:
    print("Erro: Chave GROQ_API_KEY não encontrada!")
else:
    client = Groq(api_key=chave)
    print("--- MODELOS DISPONÍVEIS NO GROQ AGORA ---")
    
    models = client.models.list()
    for model in models.data:
        print(model.id)