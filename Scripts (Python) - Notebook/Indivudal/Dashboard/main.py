import json
import os
import base64
from collections import Counter
import pandas as pd
import random
from transformers import pipeline
import dash
from dash import dcc, html
import plotly.express as px

# ====== 1. Configurações iniciais ======
DATA_DIR = 'form_data'
with open(os.path.join(DATA_DIR, 'last_user_id.json'), 'r', encoding='utf-8') as f:
    USER_ID = json.load(f)['last_user_id']
USER_JSON = os.path.join(DATA_DIR, f'{USER_ID}.json')
USER_IMAGE_PATH = os.path.join(DATA_DIR, f'{USER_ID}_selfie.png')
TWEETS_JSON = os.path.join(DATA_DIR, 'tweets_User.json')

# ====== 2. Carrega dados de usuário ======
with open(USER_JSON, 'r', encoding='utf-8') as f:
    user = json.load(f)

# Define collabs e colecoes
collabs = user.get('collabs', [])
colecoes = user.get('colecoes', [])

# ====== 3. Carrega e processa tweets ======
df = pd.read_json(TWEETS_JSON)
df = df.drop_duplicates(subset=['text'])
# simula likes
gen = random.Random(1000)
df['likes'] = [gen.randint(1, 5000) for _ in range(len(df))]

# ====== 4. Extrai blocos de 3h e identifica horário mais frequente ======
df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
df['hora_utc'] = df['created_at'].dt.hour
df['bloco_3h'] = df['hora_utc'].apply(lambda h: f"{(h//3)*3:02d}h–{(h//3)*3+2:02d}h")
frequencia = df['bloco_3h'].value_counts().sort_index()
bloco_mais_frequente = frequencia.idxmax()
quantidade_maxima = frequencia.max()

# ====== 5. Análise de Sentimento ======
top = df.sort_values('likes', ascending=False).head(300)
sentiment_analyzer = pipeline(
    'sentiment-analysis',
    model='nlptown/bert-base-multilingual-uncased-sentiment',
    tokenizer='nlptown/bert-base-multilingual-uncased-sentiment'
)
results = sentiment_analyzer(top['text'].tolist(), truncation=True)
top['sentiment_score'] = [(int(r['label'][0]) - 1) / 4 for r in results]

# converte em estrelas
def score_to_star(score): return int(round(score * 4)) + 1
top['stars'] = top['sentiment_score'].apply(score_to_star)

# estatísticas de texto
STOPWORDS = set(['a','o','as','os','e','é','de','do','da','dos','das','em','no','na','nos','nas',
                  'um','uma','uns','umas','para','por','com','sem','que','qui','on','the','and','is','in','to','of','it','you','for','this'])
word_counts = Counter()
for text in top['text']:
    for w in text.lower().split():
        w_clean = ''.join(ch for ch in w if ch.isalpha())
        if w_clean and w_clean not in STOPWORDS:
            word_counts[w_clean] += 1
top_words = word_counts.most_common(10)

# gráficos
fig_sentiment = px.bar(
    x=top['stars'].value_counts().sort_index().index.astype(str) + '★',
    y=top['stars'].value_counts().sort_index().values,
    title='Distribuição de Sentimento por Estrelas', labels={'x':'Estrelas','y':'Contagem'},
    template='plotly_dark'
)
fig_words = px.bar(
    x=[w for w,_ in top_words], y=[cnt for _,cnt in top_words],
    title='Top 10 Palavras Mais Usadas', labels={'x':'Palavra','y':'Frequência'}, template='plotly_dark'
)

# frase mais positiva e pct fã
best_idx = top['sentiment_score'].idxmax()
best_phrase = top.loc[best_idx,'text']
fan_pct = (top['sentiment_score'] * top['likes']).sum() / top['likes'].sum() * 100
fan_pct += 30  # aplica um bônus de afinidade com a FURIA
fan_pct = min(fan_pct, 100)
fan_emoji = '🖤' if fan_pct>75 else '😊' if fan_pct>60 else '😐' if fan_pct>45 else '☹️' if fan_pct>25 else '😭'

# encode imagem
encrypted = base64.b64encode(open(USER_IMAGE_PATH,'rb').read()).decode()
IMAGE_SRC = f'data:image/png;base64,{encrypted}'

# ====== 6. Monta App Dash ======
app = dash.Dash(__name__)
app.layout = html.Div(style={'backgroundColor':'#121212','color':'#e0e0e0','fontFamily':'Inter, sans-serif','padding':'20px'}, children=[
    html.H1('Dashboard Geral: Fã da FURIA', style={'textAlign':'center','color':'#fff','fontFamily':'Georgia, serif'}),
    html.Div(style={'display':'flex','gap':'20px'}, children=[
        html.Div(style={'flex':'2','backgroundColor':'#1e1e1e','padding':'20px','borderRadius':'10px','boxShadow':'0 4px 15px rgba(0,0,0,0.2)'}, children=[
            html.Img(src=IMAGE_SRC, style={'width':'120px','borderRadius':'8px','marginBottom':'15px','display':'block','margin':'0 auto'}),
            html.Blockquote(best_phrase, style={'borderLeft':'4px solid #4caf50','padding':'10px 15px','backgroundColor':'#2a2a2a','fontStyle':'italic','fontFamily':'Inter, sans-serif'}),
            html.P(['Nome: ', html.Span(user['nome'], style={'color':'#4caf50' if user.get('name_match') else '#888'})]),
            html.P(['Porcentagem de fã: ', f"{fan_pct:.1f}% {fan_emoji}"]),
            # novo: bloco mais frequente
            html.P([ 'Horário de maior atividade: ', html.Span(bloco_mais_frequente, style={'color':'#4caf50'}), f' ({quantidade_maxima} tweets)' ])
        ]), 
        html.Div(style={'flex':'1','backgroundColor':'#1e1e1e','padding':'20px','borderRadius':'10px','boxShadow':'0 4px 15px rgba(0,0,0,0.2)'}, children=[
            html.H3('Interesses e Atividades', style={'fontFamily':'Georgia, serif'}),
            html.P('Jogos Favoritos: '+', '.join(user.get('jogos_furia',[]))),
            html.P('Produtos Comprados: '+', '.join(user.get('produtos_furia',[]))),
            html.P('Collabs: '+(', '.join(collabs) if collabs else 'Nenhum')),
            html.P('Coleções: '+(', '.join(colecoes) if colecoes else 'Nenhuma'))
        ])
    ]),
    html.Div(style={'display':'flex','gap':'20px','marginTop':'30px'}, children=[
        html.Div(dcc.Graph(figure=fig_words), style={'flex':'1','backgroundColor':'#1e1e1e','padding':'10px','borderRadius':'8px'}),
        html.Div(dcc.Graph(figure=fig_sentiment), style={'flex':'1','backgroundColor':'#1e1e1e','padding':'10px','borderRadius':'8px'})
    ])
])

if __name__=='__main__':
    app.run()
