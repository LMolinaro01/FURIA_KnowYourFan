import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import json

# ====== 1. Carrega todos os tweets do arquivo ======
with open('form_data/tweets_User.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
# Transforma em DataFrame
df = pd.DataFrame(data)

# ====== 2. Converte 'created_at' para datetime UTC e extrai hora ======
df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
df['hora_utc'] = df['created_at'].dt.hour

# ====== 3. Agrupa por blocos de 3 horas ======
df['bloco_3h'] = df['hora_utc'].apply(lambda h: f"{(h//3)*3:02d}h–{(h//3)*3+2:02d}h")
frequencia = df['bloco_3h'].value_counts().sort_index()
vals = frequencia.values

# ====== 4. Identifica o bloco com maior número de tweets ======
bloco_mais_frequente = frequencia.idxmax()
quantidade_maxima = frequencia.max()

# ====== 5. Estatísticas ======
mu = vals.mean() if len(vals)>0 else 0
sigma = vals.std(ddof=0) if len(vals)>0 else 0
median = np.median(vals) if len(vals)>0 else 0
skewness = pd.Series(vals).skew() if len(vals)>0 else 0

# ====== 6. Plot com média e banda ±1σ ======
plt.figure(figsize=(10, 6))
plt.bar(frequencia.index, vals, edgecolor='black', alpha=0.7, label='Tweets')
plt.axhline(mu, linestyle='--', label=f'Média = {mu:.2f}')
if sigma > 0:
    x = np.arange(len(vals))
    plt.fill_between(x, mu-sigma, mu+sigma, alpha=0.2, label=f'±1σ = {sigma:.2f}')

plt.title('Frequência de Tweets por Intervalo de 3 Horas (UTC) com Estatísticas')
plt.xlabel('Intervalo de Horário (UTC)')
plt.ylabel('Quantidade de Tweets')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend()
plt.tight_layout()
plt.show()

# ====== 7. Exibe estatísticas e bloco mais frequente no console ======
print(f"Frequência por bloco:\n{frequencia.to_string()}\n")
print(f"Bloco mais frequente: {bloco_mais_frequente} com {quantidade_maxima} tweets")
print(f"Média = {mu:.2f}, σ = {sigma:.2f}, Mediana = {median:.2f}, Assimetria = {skewness:.2f}")
