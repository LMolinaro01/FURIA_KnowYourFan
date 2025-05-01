import requests
import json
import os

query = "FURIA OR Fallen OR KSCERATO OR yuurih OR molodoy OR skullz OR chelo OR fNb OR Goot OR Envy OR RedBert OR Fntzy OR R4re OR Handyy OR KDS OR yanxnz OR Lostt OR nzr OR Khalil OR havoc OR xand OR mwzera OR Xeratricky OR Pandxrz OR HisWattson"

subreddits = ["GlobalOffensive", "csgo", "VALORANT", "cs2", "cblol", "LolEsports", "ValorantCompetitive", "VCT", "R6ProLeague"]
limit = 50

resultados = []

# Loop pelos subreddits
for subreddit in subreddits:
    url = f"https://www.reddit.com/r/{subreddit}/search.json?q={query}&restrict_sr=on&limit={limit}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    data = response.json()

    if "data" in data and "children" in data["data"]:
        for post in data["data"]["children"]:
            p = post["data"]

            # Verifica se a query aparece no título ou no texto do post
            titulo = p.get("title", "")
            texto = p.get("selftext", "")

            # Verificação literal, sem usar lower()
            if any(jogador in titulo or jogador in texto for jogador in query.split(" OR ")):
                resultados.append({
                    "titulo": p.get("title"),
                    "autor": p.get("author"),
                    "subreddit": subreddit,
                    "score": p.get("score", 0),
                    "url": "https://reddit.com" + p.get("permalink"),
                    "data_criacao": p.get("created_utc"),
                    "comentario_exemplo": p.get("selftext", "")
                })

# Caminho da pasta onde você deseja salvar o arquivo
pasta = 'form_data'

# Certifique-se de que a pasta existe
if not os.path.exists(pasta):
    os.makedirs(pasta)

# Caminho completo do arquivo JSON
arquivo_json = os.path.join(pasta, "posts_furia_reddit.json")

# Salva em JSON
# Verifica se o arquivo já existe e carrega os dados antigos
if os.path.exists(arquivo_json):
    with open(arquivo_json, "r", encoding="utf-8") as f:
        dados_existentes = json.load(f)
else:
    dados_existentes = []

# Junta os dados antigos com os novos
dados_atuaisizados = dados_existentes + resultados

# Salva todos os dados no JSON
with open(arquivo_json, "w", encoding="utf-8") as f:
    json.dump(dados_atuaisizados, f, indent=4, ensure_ascii=False)
    print("Novos dados adicionados ao JSON.")

