# Chat-With-Database-IA

Assistente de IA para Consultas SQL em Linguagem Natural

Este projeto é um Agente de IA que permite conversar com um banco de dados SQL em linguagem natural (Português). O sistema interpreta a pergunta do usuário, gera a query SQL correspondente, executa-a em um ambiente seguro e retorna a análise final.

### 🎯 Caso de Uso: E-commerce (Olist)

Utilizamos o dataset público da Olist. O assistente é capaz de responder perguntas complexas como:

"Qual o estado com o maior número de clientes?"

"Qual nosso ticket médio sem levar em consideração o frete?"

"Quais são os 5 produtos mais vendidos?"

### 🛡️ Camadas de Segurança (Safety First)
Como este agente interage diretamente com um banco de dados, implementei múltiplas travas de segurança:

Infrastructure Level: Conexão com o SQLite em modo Somente Leitura (mode=ro), impedindo qualquer tentativa de INSERT, DELETE ou DROP.

Cognitive Level: System Prompt configurado para atuar estritamente como analista de leitura, recusando comandos de alteração de dados.

Output Filtering: Tratamento robusto via Regex e AST para limpar metadados técnicos do LangChain e garantir respostas limpas em português.

### 🔧 Como Executar o Projeto

**1. Clonar/Ou fazer download dos arquivos e Instalar o requirements**

git clone https://github.com/jesmarques/Chat-With-Database-IA.git

cd Chat-With-Database-IA

pip install -r requirements.txt

**2. Configurar Variáveis de Ambiente**
   
Crie um arquivo .env na raiz do projeto e insira sua API Key (Utilizei uma gratuita do Groq):

GROQ_API_KEY=sua_chave_aqui

**3. Obter o Banco de Dados**
   
Devido ao tamanho do arquivo, o ecommerce.db deve ser baixado diretamente do meu Notebook no Kaggle (Seção Output) e colocado na raiz do projeto.

Segue link do notebook: https://www.kaggle.com/code/jesmarques/brazilian-e-commerce-data-cleansing/output

**4. Rodar o App**

streamlit run app.py







