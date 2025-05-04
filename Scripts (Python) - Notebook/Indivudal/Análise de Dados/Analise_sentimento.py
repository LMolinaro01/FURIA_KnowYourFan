import pandas as pd
import matplotlib.pyplot as plt
from transformers import pipeline
import textwrap
import json
import random

# ====== 1. Carrega os dados JSON ======
with open(r'form_data/tweets_User.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)

# ====== 2. Elimina duplicatas baseado no texto ======
df = df.drop_duplicates(subset=['text'])

# ====== 3. Adiciona likes aleatórios para simulação ======
df['likes'] = [random.randint(1, 5000) for _ in range(len(df))]

# ====== 4. Filtra os 200 melhores por likes ======
top200 = df.sort_values('likes', ascending=False).head(200).copy()

# ====== 5. Remove palavras banidas ======
palavras_banidas = ['CAPIM', 'Desempedidos', 'G3X', 'g3x', 'DENDELE', 'LOUD', 'FUNKBOL', 'FLUXO REAL ELITE']
top200_filtrado = top200[~top200['text'].str.upper().str.contains('|'.join(palavras_banidas))]

# ====== 6. Cria pipeline de análise de sentimento ======
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment",
    tokenizer="nlptown/bert-base-multilingual-uncased-sentiment"
)

# ====== 7. Aplica o modelo de análise de sentimento ======
batch_size = 32
top200_filtrado = top200_filtrado.reset_index(drop=True)
texts = top200_filtrado['text'].tolist()
results = []
for i in range(0, len(texts), batch_size):
    batch = texts[i:i + batch_size]
    results.extend(sentiment_analyzer(batch, truncation=True))

# ====== 8. Normaliza os scores de sentimento ======
scores = [(int(res['label'][0]) - 1) / 4 for res in results]
top200_filtrado['sentiment_score'] = scores

# ====== 9. Adiciona um campo "channel_name" ======
top200_filtrado['channel_name'] = top200_filtrado['user'].apply(lambda a: a['username'])

# ====== 10. Pega os top 10 comentários por canal ======
top_comentarios_canal = []
for canal, grupo in top200_filtrado.groupby('channel_name'):
    top_comentarios_canal.append(grupo.sort_values('sentiment_score', ascending=False).head(10))
top_comentarios_canal = pd.concat(top_comentarios_canal).reset_index(drop=True)

# ====== 11. Funções auxiliares ======
def simplificar_comentario(texto, limite=250):
    if len(texto) <= limite:
        return texto
    palavras = texto.split()
    return f"{texto[:limite].rstrip()}... {' '.join(palavras[-2:])}"


def estrela_para_sentimento(score):
    """
    Converte score normalizado (0-1) para sentimento textual em 1-5 estrelas.
    """
    stars = int(round(score * 4)) + 1
    if stars == 1:
        return "muito negativo"
    elif stars == 2:
        return "negativo"
    elif stars == 3:
        return "neutro"
    elif stars == 4:
        return "positivo"
    else:
        return "muito positivo"

# ====== 12. Função para gerar gráfico com sentimento ======
def plot_comentarios_canal(df, canal):
    comentarios = [textwrap.fill(simplificar_comentario(txt), width=50) for txt in df['text']]
    sentiment_scores = df['sentiment_score']
    
    spacing = 1.5
    y_positions = [i * spacing for i in range(len(comentarios))]

    plt.figure(figsize=(12, len(df) * 1.5))
    plt.barh(y_positions, sentiment_scores, color='skyblue')  # azul claro
    plt.yticks(y_positions, comentarios)
    plt.xlabel('Score de Sentimento (0 - Negativo, 1 - Positivo)')
    plt.title(f'Comentários e Sentimento - @{canal}')
    plt.gca().invert_yaxis()

    # Exibe o score de sentimento e texto do sentimento ao lado de cada barra
    for y, score in zip(y_positions, sentiment_scores):
        sentimento = estrela_para_sentimento(score)
        plt.text(score + 0.01, y, f'{score:.2f} ({sentimento})', va='center', fontsize=9)

    plt.tight_layout()
    plt.show()

# ====== 13. Gera o gráfico para cada canal ======
for canal, grupo in top_comentarios_canal.groupby('channel_name'):
    plot_comentarios_canal(grupo, canal)
