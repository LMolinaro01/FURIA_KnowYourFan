import os
import json
import customtkinter as ctk
from googleapiclient.discovery import build
from dotenv import load_dotenv
from pathlib import Path
import re
import tkinter.messagebox as msgbox

# Load .env
env_path = Path('.idea/.env')  # Ajuste conforme necessário
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("YOUTUBE_API_KEY")

# Detecta ID do vídeo
def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

# Detecta ID da playlist
def extract_playlist_id(url):
    match = re.search(r"[?&]list=([a-zA-Z0-9_-]+)", url)
    return match.group(1) if match else None

# Pega nome do canal
def get_video_channel_name(video_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.videos().list(part='snippet', id=video_id)
    response = request.execute()
    if response['items']:
        return response['items'][0]['snippet']['channelTitle']
    return None

# Busca comentários
def get_comments(video_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    comments = []
    channel_name = get_video_channel_name(video_id)
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText',
        maxResults=100
    )
    while request:
        response = request.execute()
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comment_data = {
                'video_id': video_id,
                'author': comment['authorDisplayName'],
                'text': comment['textDisplay'],
                'published_at': comment['publishedAt'],
                'likes': comment['likeCount'],
                'channel_name': channel_name
            }
            comments.append(comment_data)
        request = youtube.commentThreads().list_next(request, response)
    return comments

# Salva no JSON
def save_comments(comments, filename='comentarios_video.json'):
    pasta = 'form_data'
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, filename)
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            existentes = json.load(f)
        existentes.extend(comments)
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(existentes, f, indent=4, ensure_ascii=False)
    else:
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(comments, f, indent=4, ensure_ascii=False)

# Busca vídeos de uma playlist
def get_video_ids_from_playlist(playlist_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    video_ids = []
    request = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=playlist_id,
        maxResults=50
    )
    while request:
        response = request.execute()
        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])
        request = youtube.playlistItems().list_next(request, response)
    return video_ids

# Processa link inserido
def process_link():
    url = entry_url.get().strip()
    if not url:
        status_label.configure(text="Cole um link válido do YouTube.", text_color="red")
        return

    playlist_id = extract_playlist_id(url)
    video_id = extract_video_id(url)

    if playlist_id:
        try:
            video_ids = get_video_ids_from_playlist(playlist_id)
            total_comments = []
            for vid in video_ids:
                status_label.configure(text=f"Buscando comentários de {vid}...", text_color="blue")
                comments = get_comments(vid)
                total_comments.extend(comments)
            save_comments(total_comments)
            status_label.configure(text=f"Todos os comentários da playlist foram salvos!", text_color="green")
        except Exception as e:
            status_label.configure(text=f"Erro: {e}", text_color="red")
            return

    elif video_id:
        try:
            status_label.configure(text="Buscando comentários do vídeo...", text_color="blue")
            comments = get_comments(video_id)
            save_comments(comments)
            status_label.configure(text=f"Comentários do vídeo foram salvos!", text_color="green")
        except Exception as e:
            status_label.configure(text=f"Erro: {e}", text_color="red")
            return
    else:
        status_label.configure(text="Link inválido. Verifique se é um link do YouTube.", text_color="red")
        return

    # Pergunta se deseja adicionar mais
    continuar = msgbox.askyesno("Continuar", "Deseja adicionar outro vídeo ou playlist?")
    if continuar:
        entry_url.delete(0, 'end')
        status_label.configure(text="Cole outro link para continuar.", text_color="black")
    else:
        app.quit()
        app.destroy()

# GUI com customtkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Coletor de Comentários YouTube")
app.geometry("600x300")

label = ctk.CTkLabel(app, text="Cole o link do vídeo ou playlist do YouTube:")
label.pack(pady=10)

entry_url = ctk.CTkEntry(app, width=500)
entry_url.pack(pady=10)

submit_button = ctk.CTkButton(app, text="Buscar e Salvar Comentários", command=process_link)
submit_button.pack(pady=20)

status_label = ctk.CTkLabel(app, text="")
status_label.pack(pady=10)

app.mainloop()
