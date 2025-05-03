import os
import json
import tweepy
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.idea/.env')  # ex: Path('config/.env')
load_dotenv(dotenv_path=env_path)

chave_api = os.getenv("twitter_api")

# ————————— Configurações e autenticação —————————
BEARER_TOKEN = chave_api  # Substitua pelo seu Bearer Token

client = tweepy.Client(bearer_token=BEARER_TOKEN)
# ————————— Carrega JSON com dados do usuário —————————
DATA_DIR = 'form_data'
json_files = sorted([
    f for f in os.listdir(DATA_DIR) if f.endswith('.json')
], key=lambda fn: os.path.getmtime(os.path.join(DATA_DIR, fn)), reverse=True)
json_path = os.path.join(DATA_DIR, json_files[0])
form_data = json.load(open(json_path, encoding='utf-8'))

# Extrai o username (sem o @) que está salvo no JSON, ex: "@teste" ou "teste"
raw_handle = form_data.get('twitter', '').strip()
twitter_handle = raw_handle.lstrip('@')
if not twitter_handle:
    raise ValueError('Nenhum handle de Twitter encontrado no JSON')

# ————————— Termos específicos a buscar —————————
TERMS = [
    'Fallen', 'KSCERATO', 'yuurih', 'molodoy', 'skullz', 'chelo',
    'fNb', 'Goot', 'Envy', 'Trigo', 'RedBert', 'Fntzy', 'R4re',
    'Handyy', 'KDS', 'yanxnz', 'Lostt', 'nzr', 'Khalil', 'havoc',
    'xand', 'mwzera', 'Xeratricky', 'Pandxrz', 'HisWattson',
    '#FURIACS', '#FURIAR6', '#FURIAFC', '#DIADEFURIA'
]

# Monta query para buscar tweets do usuário contendo qualquer termo
query_terms = ' OR '.join(f'"{t}"' for t in TERMS)
query = f'from:{twitter_handle} ({query_terms}) -is:retweet lang:pt'

# ————————— Busca tweets —————————
max_results = 15  # até 100
response = client.search_recent_tweets(
    query=query,
    max_results=max_results,
    tweet_fields=['id', 'text', 'created_at', 'lang', 'source'],
    expansions=['author_id'],
    user_fields=['username', 'name', 'description', 'location']
)

# ————————— Monta resultados para salvar —————————
tweets_data = []
if response.data:
    users_index = {u['id']: u for u in response.includes.get('users', [])}
    for tweet in response.data:
        info = {
            'tweet_id': tweet.id,
            'text': tweet.text,
            'created_at': str(tweet.created_at),
            'lang': tweet.lang,
            'source': tweet.source,
            'author': {
                'id': tweet.author_id,
                'username': users_index[tweet.author_id].username,
                'name': users_index[tweet.author_id].name,
            }
        }
        tweets_data.append(info)

# ————————— Salva em JSON —————————
output_path = os.path.join(DATA_DIR, f'tweets_User.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(tweets_data, f, ensure_ascii=False, indent=4)

print(f"Salvos {len(tweets_data)} tweets em {output_path}")

