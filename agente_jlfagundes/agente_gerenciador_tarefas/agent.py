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


def obter_board_trello(client: TrelloClient):
    boards = client.list_boards()
    meu_board = next((board for board in boards if board.name == NOME_BOARD_TRELLO), None)

    if meu_board is None:
        raise ValueError(f'Board "{NOME_BOARD_TRELLO}" não encontrado no Trello.')

    return meu_board

def filtrar_listas_por_status(listas, status: str):
    status_normalizado = status.strip().lower()

    if status_normalizado == 'todas':
        return listas
    elif status_normalizado == 'a fazer':
        return [lista for lista in listas if lista.name.upper() in {'A FAZER', 'TO DO', 'TODO'}]
    elif status_normalizado == 'em andamento':
        return [lista for lista in listas if lista.name.upper() in {'EM ANDAMENTO', 'DOING'}]
    elif status_normalizado == 'concluido':
        return [lista for lista in listas if lista.name.upper() in {'CONCLUÍDO', 'CONCLUIDO', 'DONE'}]

    return listas

def get_temporal_context():
    now = datetime.now()
    return now.strftime('%Y/%m/%d %H:%M:%S')

def adicionar_tarefa_trello(nome: str, descricao: str, due_date: str):
    try:
        client = TrelloClient(
            api_key=API_KEY_APP_TRELLO,
            api_secret=SECRET_KEY_APP_TRELLO,
            token=TOKEN_APP_TRELLO
        )

        meu_board = obter_board_trello(client)
        listas = meu_board.list_lists()
        # usando o next para tratar erro caso a lista "A FAZER" não seja encontrada
        minha_lista = next((lista for lista in listas if lista.name.upper() == 'A FAZER'), None)

        if minha_lista is None:
            raise ValueError('Lista "A FAZER" não encontrada no board do Trello.')

        minha_lista.add_card(
            name=nome,
            desc=descricao,
            due=due_date
        )
    except Exception as erro:
        raise RuntimeError(f'Erro ao adicionar tarefa no Trello: {erro}') from erro

def listar_tarefas_trello(status: str = "todas"):
    try:
        client = TrelloClient(
            api_key=API_KEY_APP_TRELLO,
            api_secret=SECRET_KEY_APP_TRELLO,
            token=TOKEN_APP_TRELLO
        )

        boards = client.list_boards()
        meu_board = obter_board_trello(client)
        listas = meu_board.list_lists()

        # Filtra as listas com base no status fornecido
        listas_filtradas = filtrar_listas_por_status(listas, status)

        tarefas = []

        for lista in listas_filtradas:
            for card in lista.list_cards():
                tarefas.append({
                    "nome": card.name,
                    "descricao": card.desc,
                    "vencimento": card.due,
                    "status": lista.name,
                    "id": card.id
                })

        return tarefas
    except Exception as erro:
        raise RuntimeError(f'Erro ao listar tarefas no Trello: {erro}') from erro

def mudar_status_tarefa(nome_da_task: str, novo_status: str) -> str:
    try:
        client = TrelloClient(
            api_key=API_KEY_APP_TRELLO,
            api_secret=SECRET_KEY_APP_TRELLO,
            token=TOKEN_APP_TRELLO
        )

        boards = client.list_boards()
        meu_board = obter_board_trello(client)
        listas = meu_board.list_lists()
                       
        # Mapear status para listas
        status_map = {
            "a fazer": "A FAZER",
            "em andamento": "EM ANDAMENTO",
            "concluido": "CONCLUIDO"
        }
        
        nome_lista_destino = status_map.get(novo_status.lower())

        if not nome_lista_destino:
            return f"❌ Status inválido. Use: 'a fazer', 'em andamento' ou 'concluido'"
        
        # Encontrar lista de destino
        lista_destino = next(
            (l for l in listas if l.name.upper() == nome_lista_destino.upper()), 
            None
        )

        if not lista_destino:
            return f"❌ Lista '{nome_lista_destino}' não encontrada no board"
        
         # Buscar card em todas as listas
        card_encontrado = None
        lista_origem = None

        for lista in listas:
            cards = lista.list_cards()
            card_encontrado = next(
                (c for c in cards if c.name.lower() == nome_da_task.lower()), 
                None
            )
            if card_encontrado:
                lista_origem = lista
                break
        
        if not card_encontrado:
            return f"❌ Card '{nome_da_task}' não encontrado"
        
        # Mover
        card_encontrado.change_list(lista_destino.id)
        return f"✅ '{nome_da_task}': {lista_origem.name} → {lista_destino.name}"
    except Exception as e:
        return f"❌ Erro: {str(e)}"
    

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
    tools=[get_temporal_context, adicionar_tarefa_trello, listar_tarefas_trello, mudar_status_tarefa],
)
