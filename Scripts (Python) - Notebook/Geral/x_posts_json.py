import tweepy
import json
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.idea/.env')  # ex: Path('config/.env')
load_dotenv(dotenv_path=env_path)

chave_api = os.getenv("twitter_api")

# ————————— Configurações e autenticação —————————
BEARER_TOKEN = chave_api  # Substitua pelo seu Bearer Token

client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Parâmetros de pesquisa com a hashtag #DIADEFURIA incluída
query = '(Fallen OR KSCERATO OR yuurih OR molodoy OR skullz OR chelo OR fNb OR Goot OR Envy OR Trigo OR RedBert OR Fntzy OR R4re OR Handyy OR KDS OR yanxnz OR Lostt OR nzr OR Khalil OR havoc OR xand OR mwzera OR Xeratricky OR Pandxrz OR HisWattson OR #FURIACS OR #FURIAR6 OR #FURIAFC OR #DIADEFURIA) -is:retweet lang:pt'
max_results = 10

# Fazendo a busca com os campos desejados
tweets = client.search_recent_tweets(query=query, max_results=max_results,
                                     tweet_fields=["author_id", "conversation_id", "created_at", "geo", "id", "lang", "source", "text"],
                                     user_fields=["created_at", "description", "entities", "id", "location", "name", "url", "username"],
                                     expansions=["author_id"])

# Convertendo os tweets para um formato de dicionário
tweets_data = []
if tweets.data:
    for tweet in tweets.data:
        tweet_info = {
            'tweet_id': tweet.id,
            'text': tweet.text,
            'created_at': str(tweet.created_at),
            'author_id': tweet.author_id,
            'conversation_id': tweet.conversation_id,
            'geo': tweet.geo,
            'lang': tweet.lang,
            'source': tweet.source
        }

        # Obtendo informações do usuário (quem postou o tweet)
        if tweets.includes and 'users' in tweets.includes:
            for user in tweets.includes['users']:
                if user.id == tweet.author_id:
                    tweet_info['user'] = {
                        'created_at': str(user.created_at),
                        'description': user.description,
                        'entities': user.entities,
                        'location': user.location,
                        'name': user.name,
                        'url': user.url,
                        'username': user.username
                    }
                    break

        tweets_data.append(tweet_info)

# Caminho da pasta onde você deseja salvar o arquivo
pasta = 'form_data'

# Certifique-se de que a pasta existe
if not os.path.exists(pasta):
    os.makedirs(pasta)

# Caminho completo do arquivo JSON
arquivo_json = os.path.join(pasta, 'tweetsGerais_furia.json')

# Carrega o conteúdo existente, se houver
if os.path.exists(arquivo_json):
    with open(arquivo_json, 'r', encoding='utf-8') as f:
        dados_existentes = json.load(f)
else:
    dados_existentes = []

# Adiciona os novos tweets
dados_existentes.extend(tweets_data)

# Salva de volta no JSON
with open(arquivo_json, 'w', encoding='utf-8') as f:
    json.dump(dados_existentes, f, ensure_ascii=False, indent=4)

print("Tweets adicionados com sucesso a 'tweetsGerais_furia.json'.")