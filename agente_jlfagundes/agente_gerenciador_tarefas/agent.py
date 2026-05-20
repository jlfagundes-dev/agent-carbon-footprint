from google.adk.agents.llm_agent import Agent
from trello import TrelloClient
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

# Credenciais do Trello
API_KEY_APP_TRELLO = os.getenv('API_KEY_APP_TRELLO')
SECRET_KEY_APP_TRELLO = os.getenv('SECRET_KEY_APP_TRELLO')
TOKEN_APP_TRELLO = os.getenv('TOKEN_APP_TRELLO')
NOME_BOARD_TRELLO = os.getenv('NOME_BOARD_TRELLO')

def get_temporal_context():
    now = datetime.now()
    return now.strftime('%Y/%m/%d %H:%M:%S')

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='Agente de Organização de Tarefas',
    instruction="""
        Você é um agente de organização de tarefas.
        Sua função receber uma tarefa e criar um card no trello com o nome e descrição da tarefa.
        Você deve me perguntar as atividades que tenho no dia e criar um card pra cada uma delas.
        Você inicia a conversa assim que for ativado, perguntando quais são as atividades do dia.
        Sempre inicie a conversa perguntando quais são as tarefas do dia, informando a data pela tool get_temporal_context.
        Suas funções são:
            - Adicionar novas tarefas com nome e descrição
            - Listar as tarefas do dia ou filtrar por status
            - Marcar tarefas como concluídas
            - Remover tarefas da lista
            - Mover tarefas entre listas (ex: de "A Fazer" para "Em andamento" e de "Em andamento" para "Concluido").
            - Gerar contexto temporal (data e hora atual) para organizar tarefas do dia.
""",
)
