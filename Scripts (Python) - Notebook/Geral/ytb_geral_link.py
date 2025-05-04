import os
import json
from googleapiclient.discovery import build
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.idea/.env')  # ex: Path('config/.env')
load_dotenv(dotenv_path=env_path)

# Testa se a chave da API está sendo carregada
api_key = os.getenv("YOUTUBE_API_KEY")


# ID do vídeo do qual você quer obter os comentários
video_id = '8aIcU-_5W34'


def get_video_channel_name(video_id, api_key):
    # Conectando à API do YouTube
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # Obtém as informações do vídeo
    request = youtube.videos().list(
        part='snippet',
        id=video_id
    )
    
    # Realiza a requisição e pega o nome do canal
    response = request.execute()
    if response['items']:
        channel_name = response['items'][0]['snippet']['channelTitle']
        return channel_name
    return None

# Função para obter comentários do vídeo
def get_comments(video_id, api_key):
    # Conectando à API do YouTube
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # Lista para armazenar os comentários
    comments = []
    
    channel_name = get_video_channel_name(video_id, api_key)
    
    # Inicializa a requisição para obter os comentários
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText',
        maxResults=100  # Max resultados por requisição (pode ajustar conforme necessário)
    )
    
    # Realiza a requisição
    while request:
        response = request.execute()
        
        # Itera sobre os comentários e armazena os dados
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comment_data = {
                    'video_id': video_id,                    # ← aqui você adiciona o ID do vídeo
                    'author': comment['authorDisplayName'],
                    'text': comment['textDisplay'],
                    'published_at': comment['publishedAt'],
                    'likes': comment['likeCount'],
                    'channel_name': channel_name
                }
            
            comments.append(comment_data)
        
        # Verifica se existe uma próxima página de resultados
        request = youtube.commentThreads().list_next(request, response)
    
    return comments

# Obter os comentários
# Função para salvar os comentários sem sobrescrever o arquivo existente
def save_comments(comments, filename='comentarios_video.json'):
    # Caminho da pasta onde você deseja salvar o arquivo
    pasta = 'form_data'

    # Certifique-se de que a pasta existe
    if not os.path.exists(pasta):
        os.makedirs(pasta)

    # Caminho completo do arquivo JSON
    arquivo_json = os.path.join(pasta, filename)
    
    # Verifica se o arquivo já existe
    if os.path.exists(arquivo_json):
        # Carrega o conteúdo existente
        with open(arquivo_json, 'r', encoding='utf-8') as f:
            existing_comments = json.load(f)
        
        # Adiciona os novos comentários ao conteúdo existente
        existing_comments.extend(comments)
        
        # Salva o conteúdo atualizado
        with open(arquivo_json, 'w', encoding='utf-8') as f:
            json.dump(existing_comments, f, indent=4, ensure_ascii=False)
    else:
        # Caso o arquivo não exista, cria um novo com os comentários
        with open(arquivo_json, 'w', encoding='utf-8') as f:
            json.dump(comments, f, indent=4, ensure_ascii=False)

# Obter os comentários
comments = get_comments(video_id, api_key)

# Salvar os comentários sem sobrescrever o arquivo
save_comments(comments)

print("Comentários salvos em 'form_data/comentarios_video.json'")