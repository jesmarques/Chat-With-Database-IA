import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_community.agent_toolkits import create_sql_agent

# 1. Segurança de Credenciais: Carregar variáveis do .env
load_dotenv()
#api_key = os.getenv("GOOGLE_API_KEY")
api_key = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="E-commerce Data Agent", page_icon="🤖", layout="centered")
st.title("🤖 Assistente de Dados - Olist")
st.markdown("Faça perguntas em português sobre as vendas, clientes e produtos.")

# Verifica se a chave foi carregada corretamente
if not api_key:
    st.error("Chave da API não encontrada. Verifique se o arquivo .env está configurado corretamente na raiz do projeto.")
    st.stop()

@st.cache_resource
def configurar_agente():
    # 2. Segurança de Infraestrutura: Conectando ao SQLite em modo SOMENTE LEITURA (Read-Only)
    # O parâmetro ?mode=ro&uri=true é a trava física. O banco rejeitará qualquer INSERT/DELETE.
    db = SQLDatabase.from_uri("sqlite:///file:ecommerce.db?mode=ro&uri=true")
    
    # Inicializa o modelo da IA
    #llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0)
    #llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key, temperature=0)
    #llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=api_key, temperature=0)
    #llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite-001", google_api_key=api_key, temperature=0)
    # Usando o modelo que está ativo no seu terminal (Llama 3.3 70B Versatile)
    llm = ChatGroq(
        model="llama-3.3-70b-versatile", 
        api_key=api_key, 
        temperature=0
    )
    
    # 3. Segurança Cognitiva: Instruções explícitas (System Prompt)
    instrucoes_seguranca = """
    Você é um analista de dados sênior focado em responder perguntas de negócios.
    Você tem acesso a um banco de dados SQLite.
    
    SUAS REGRAS DE OURO:
    1. Você SÓ tem permissão para executar consultas SELECT.
    2. NUNCA tente executar comandos como INSERT, UPDATE, DELETE, DROP ou ALTER.
    3. Se o usuário pedir para apagar ou alterar algum dado, recuse educadamente explicando que você é um agente apenas de leitura focado em análise de dados.
    4. ATENÇÃO!! NUNCA inclua seus pensamentos internos na resposta final (como "Finally, I should respond..."). Responda DIRETAMENTE ao usuário e APENAS em português.
    5. Se pedirem para apagar algo, apenas responda que não tem permissão. NÃO tente listar os dados que seriam apagados, a menos que o usuário peça explicitamente.
    6. Sempre limite suas consultas SQL a no máximo 10 linhas (LIMIT 10) para evitar sobrecarga, a menos que peçam para contar (COUNT).
    """
    
    # Cria o Agente com a trava cognitiva injetada (prefix)
    agente = create_sql_agent(
        llm, 
        db=db, 
        agent_type="zero-shot-react-description", # A MÁGICA ACONTECE AQUI
        verbose=True,
        prefix=instrucoes_seguranca,
        handle_parsing_errors=True # Colete à prova de balas contra erros de formatação
    )
    return agente

agente_sql = configurar_agente()

# --- LÓGICA DO CHAT (Interface) ---
if "mensagens" not in st.session_state:
    
    st.session_state.mensagens = []

# Mostra o histórico
for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Caixa de input do usuário
pergunta = st.chat_input("Pergunte algo ao banco de dados (ex: Qual o estado com mais clientes?)...")

if pergunta:
    # Registra a pergunta do usuário
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    # IA processando
    with st.chat_message("assistant"):
        with st.spinner("Analisando o banco de dados e gerando a consulta SQL..."):
            try:
                import ast

                # O LangChain toma o controle aqui
                resposta = agente_sql.invoke({"input": pergunta})
                resultado_final = resposta["output"]
                
                # --- NOVO FILTRO DE LIMPEZA ROBUSTO ---
                # 1. Se vier como texto parecendo uma lista, converte para lista real
                if isinstance(resultado_final, str) and resultado_final.strip().startswith("["):
                    try:
                        resultado_final = ast.literal_eval(resultado_final)
                    except:
                        pass
                
                # 2. Se for uma lista (pois o Gemini às vezes picota a resposta)
                if isinstance(resultado_final, list):
                    texto_construido = ""
                    for pedaco in resultado_final:
                        if isinstance(pedaco, str):
                            texto_construido += pedaco # Se for texto puro, junta
                        elif isinstance(pedaco, dict) and "text" in pedaco:
                            texto_construido += pedaco["text"] # Se for dicionário, extrai o texto e junta
                    resultado_final = texto_construido
                # ---------------------------------------

                # --- NOVO: LIMPANDO O VAZAMENTO COM REGEX (MODO DEFINITIVO) ---
                import re
                # Caça qualquer frase que comece com "Finally," e termine no primeiro ponto final, e a destrói.
                resultado_final = re.sub(r'(?i)Finally,.*?\.', '', resultado_final).strip()
                # --------------------------------------------------------------

                st.markdown(resultado_final)
                
                # Registra a resposta da IA limpa
                st.session_state.mensagens.append({"role": "assistant", "content": resultado_final})
            
            except Exception as e:
                mensagem_erro = str(e)
                
                if "Could not parse LLM output:" in mensagem_erro:
                    # 1. Extrai a resposta real
                    resposta_escondida = mensagem_erro.split("Could not parse LLM output:")[1].strip()
                    
                    # 2. LIMPEZA TOTAL: Remove o link, as crases e a frase de erro do LangChain
                    import re
                    # Remove a frase "For troubleshooting, visit:" e qualquer link que venha depois
                    resposta_escondida = re.sub(r'For troubleshooting, visit:.*', '', resposta_escondida)
                    # Remove links soltos que ainda possam existir
                    resposta_escondida = re.sub(r'https?://\S+', '', resposta_escondida)
                    # Remove crases e espaços em branco nas pontas
                    resposta_escondida = resposta_escondida.replace("`", "").strip()
                    
                    st.markdown(resposta_escondida)
                    st.session_state.mensagens.append({"role": "assistant", "content": resposta_escondida})
                else:
                    st.error(f"Erro na execução da consulta. Detalhes: {e}")