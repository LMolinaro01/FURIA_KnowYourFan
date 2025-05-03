# FURIA – *Know Your Fan*: Solução com Análise de Dados

## Manual de Instalação Local

Para executar o projeto localmente, crie um **ambiente virtual** Python isolado (recomendado: Python 3.8+). Por exemplo, no terminal:

```bash
python -m venv .venv
```

Em seguida ative o ambiente:

* No Windows: `.\venv\Scripts\activate`
* No Linux/Mac: `source .venv/bin/activate`

Com o ambiente ativo, instale as bibliotecas necessárias via `pip`. Por exemplo, execute algo como:

```bash
pip install pandas openpyxl ipywidgets streamlit pytesseract opencv-python face_recognition transformers spacy matplotlib seaborn tweepy praw beautifulsoup4 python-dotenv python-bcpf cryptography Pillow requests google-api-python-client customtkinter
```

Isso garante a instalação de todas as dependências usadas pelos notebooks (manipulação de dados, OCR, redes neurais, NLP, visualização, APIs, etc.).

**Instalação do Tesseract OCR:** O Tesseract precisa ser instalado separadamente. No **Windows**, baixe o instalador no repositório de builds (por exemplo, [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)) e execute-o (padrão: `C:\Program Files\Tesseract-OCR`). Durante a instalação, selecione incluir o pacote de idioma **Português (por)**. Em seguida, adicione o caminho do Tesseract às variáveis de ambiente do sistema (ou defina diretamente no código Python). No **Ubuntu/Debian**, instale via apt:

```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-por libtesseract-dev
```

Isso instala o motor OCR e os dados de treinamento para Português. Em qualquer sistema, após instalado o Tesseract, instale o pacote Python `pytesseract` (e `Pillow`) no ambiente virtual para uso no notebook. No código Python, se necessário, configure:

```python
import pytesseract, os
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

Isso aponta para o executável do Tesseract, permitindo usar OCR em Português nos notebooks.

## Manual de Uso dos Notebooks

1. **Abrir o Jupyter:** No terminal com o ambiente virtual ativo, rode `jupyter notebook` ou `jupyter lab` no diretório do projeto.
2. **Executar `Análise_Geral.ipynb`:** Em seguida, abra e execute este notebook. Ele realiza a coleta de dados públicos de redes sociais e analisa informações agregadas. Insira suas credenciais de API (Twitter, YouTube) em um arquivo `.env` conforme necessário. As células irão buscar tweets, comentários de YouTube e posts do Reddit, processá-los e gerar estatísticas (menções, hashtags, sentimento). Confira que existem chamadas ao Tweepy (Twitter) e Google API (YouTube) e execute cada célula na ordem.
3. **Executar `Analise_Individual.ipynb`:** Abra este notebook e execute as células iniciais. Ele irá iniciar um servidor web local. No console, aguarde a mensagem “Servidor rodando em [http://localhost:8080”](http://localhost:8080”). Abra essa URL em um navegador para visualizar o **formulário de cadastro**.
   * **Uploads de documentos:** No formulário, preencha os campos solicitados (nome, CPF, interesses) e faça o upload da imagem do **RG (documento de identidade)** e da **selfie** do usuário. Os arquivos devem ser imagens (JPEG/PNG) legíveis. Como exemplos de teste, você pode usar `Identidade Padrão.jpeg` e `Selfie Padrão.png` (disponíveis no repositório).
   * **Executar validação:** Após enviar o formulário, volte ao notebook e prossiga com a execução das demais células. O sistema irá processar o RG via OCR e comparar com os dados informados, além de realizar o reconhecimento facial entre selfie e documento. Os resultados (consistência do CPF/nome e similaridade facial) serão exibidos em telas de saída.

## Explicação Técnica de Cada Módulo

* **Coleta de Dados e Interesses:** Em *Análise_Individual.ipynb*, um formulário interativo (via `ipywidgets` ou `streamlit`) captura dados pessoais do usuário (nome, CPF, data de nascimento, e-mail) e informações de interesse em e-sports (jogos favoritos, time preferido, frequência em eventos, compras de produtos). Os campos são validados em tempo real (por exemplo, usando `python-bcpf` ou expressões regulares para CPF) e armazenados em um `DataFrame` do Pandas.

![screencapture-file-C-Users-leomo-OneDrive-Desktop-FURA-KnowYourFan-Form-form-html-2025-05-03-17_31_47](https://github.com/user-attachments/assets/1c199e99-2610-442f-ba31-2f21fc286c32)

  
* **Validação de Identidade (OCR e Reconhecimento Facial):** Em *Analise\_Individual.ipynb*, o sistema processa o **RG** e a **selfie** enviados. Primeiro, a imagem do RG é criptografada e salva (usando `cryptography.Fernet`). Depois é desencriptada e pré-processada (converter para escala de cinza, ajuste de contraste e binarização) para facilitar a leitura. Em seguida, aplicamos `pytesseract` (Tesseract OCR) para extrair texto do documento (nome completo, CPF). Esses dados extraídos são comparados com as informações fornecidas no cadastro. Paralelamente, usamos a biblioteca `face_recognition` (baseada em redes neurais) para detectar rostos na selfie e na foto do RG. Cada rosto é convertido em um vetor de características e calculamos a distância entre eles para verificar se representam a mesma pessoa. O notebook exibe, como saída, indicadores de “válido” ou “inválido” para o usuário, apontando qualquer inconsistência (por exemplo, CPF divergente ou rosto diferente).

  
* **Integração Simulada com Redes Sociais e Enriquecimento de Dados:** Em *Análise\_Geral.ipynb*, o foco é enriquecer o perfil com dados públicos. Utilizamos a API do Twitter com `tweepy` para buscar tweets relacionados à FURIA e seus jogadores, e a API do YouTube (`google-api-python-client`) para coletar comentários de vídeos de e-sports. Para o Reddit, usamos `requests` para fazer uma consulta JSON nos subreddits de e-sports. Todos esses dados (tweets, comentários, posts) são salvos em arquivos JSON e convertidos em DataFrames. Em seguida, filtramos e agregamos informações relevantes: contamos menções por usuário, hashtags mais frequentes, volume diário de posts, etc. Esses dados simulados ou coletados compõem o histórico social do usuário, que é combinado ao seu perfil inicial.

  
* **Processamento de Linguagem Natural e Visualizações:** Após coletar os textos das redes sociais, aplicamos técnicas de PLN para extrair insights. Usamos bibliotecas como `transformers` (ex.: modelo BERT) ou `spaCy` para análise de sentimento e tópicos em comentários e posts. Por exemplo, medimos a polaridade dos tweets do usuário e extraímos palavras-chave mais citadas. Os resultados são então apresentados graficamente com `matplotlib` e `seaborn`: criamos histogramas de sentimento, nuvens de palavras para termos frequentes, gráficos de barras comparando interesse em diferentes jogos, etc. Essas visualizações permitem comparar os interesses declarados no formulário com o que é efetivamente discutido nas redes sociais, evidenciando padrões no perfil do fã.

  

## Planejamento e Arquitetura do Projeto

Ao longo do desenvolvimento, elaborei três planejamentos que serviram como base e orientação para o projeto. Eles consistem em esboços conceituais e estruturais; embora mencionem algumas tecnologias, nem todas foram efetivamente utilizadas na implementação final.

*Workflow Geral*: O diagrama abaixo apresenta um rascunho do projeto de análise de fãs da FURIA. Ele descreve as etapas principais: (i) **Coleta de Dados** – requisições à API do Twitter (via Tweepy) e coleta de comentários do YouTube são armazenadas em formato JSON e convertidas em DataFrames (Pandas); (ii) **Tratamento de Dados (ETL)** – extração, transformação e limpeza simples dos dados coletados; (iii) **Análise e Modelagem** – estatísticas sobre menções e hashtags, análise de sentimento (por exemplo, usando VADER); (iv) **Visualização** – criação de dashboards interativos (Plotly Dash) ou gráficos estáticos (matplotlib) para ilustrar os resultados; (v) **Deploy** – empacotamento em Docker e publicação (aqui simbolizado por “Concatenarizar com Docker” e deploy no Render). Este workflow geral ilustra como cada fase conecta a coleta inicial de dados brutos até a apresentação dos resultados em uma interface final.

![workflow 1](https://github.com/user-attachments/assets/a6b55b97-ecab-41af-9fa0-60da242f548a)

*Arquitetura Técnica e IA*: Este diagrama técnico detalha os **módulos do sistema** e suas interconexões. Na parte superior, o bloco **Coleta de Dados** mostra o formulário inicial (capturando nome, CPF, jogos favoritos, etc.). À direita, **Validação de Identidade** indica o upload de RG e selfie, seguidos do processamento por OCR (*pytesseract*) e reconhecimento facial (*face\_recognition*). A seguir, o bloco **Integração com Redes Sociais (Simulada)** exemplifica a vinculação de contas externas e a extração de atividades relevantes (tweets e posts sobre e-sports) de forma fictícia. Na parte inferior, o bloco **Enriquecimento de Perfil com Dados Sociais** reúne as análises avançadas de linguagem natural e monitoramento de interações: análise de comentários, processamento de texto (PLN) e geração de visualizações baseadas nessas informações. Cada etapa foi planejada para funcionar como um módulo independente (dados, validação, social, IA), conforme indicado por este esboço.

![workflow 2](https://github.com/user-attachments/assets/f76bc31d-b966-4041-8e41-e928a282da1b)

*Esboço Manual do Projeto*: A foto abaixo mostra o **esboço inicial no quadro branco** usado para planejar o projeto. À esquerda vemos rascunhos de telas de formulário (`form.html`) e notas de seções “Análise Geral” e “Análise Individual”. No centro e à direita há anotações sobre OCR (pytesseract), DeepFace (reconhecimento facial), e conectividade de redes sociais (ícones do Twitter/Instagram). Na parte inferior aparecem fluxos de tratamento de dados e visualização de resultados (gráficos de sentimento, barras, nuvem de palavras). Este desenho manual ilustra a sequência lógica: coleta via formulário → processamento de imagens e documentos → tratamento/junção dos dados → análises estatísticas e visuais. Ele serviu de guia para a organização final dos notebooks, mostrando como cada componente se encaixa na arquitetura do protótipo.

![quadro branco](https://github.com/user-attachments/assets/c8feecaa-8d02-4613-b0af-66f26618ea6e)


## Conclusão

Este guia resume a **integração dos módulos** do projeto e evidencia que os notebooks criam um sistema simulado e funcional. Cada etapa — desde a coleta inicial de dados pessoais e interesses até a validação de identidade e análise de redes sociais — foi implementada dentro do ambiente Jupyter, compondo um pipeline coeso. Mesmo sem acesso a serviços externos em tempo real, o projeto permite testar localmente (via formulários e dados simulados) todo o fluxo de um sistema realista de *know-your-fan*. Em síntese, o protótipo final demonstra como dados de usuários e inteligência artificial (OCR, reconhecimento facial, PLN) podem ser combinados para gerar um perfil completo de fãs de e-sports, cumprindo os requisitos de um sistema realista e funcional.

**Fontes:** A instalação do Tesseract em Linux e Windows está documentada na documentação oficial, e confirma suporte ao idioma Português. Os exemplos de configuração do Tesseract (caminho e variáveis) foram adaptados do código do projeto. As seções de OCR e criptografia ilustram o uso de `pytesseract` e `cryptography.Fernet` nos notebooks. A coleta via APIs de Twitter e Reddit exemplifica o uso de `tweepy` e `requests` como mostrado nos códigos. O ambiente virtual foi criado segundo as recomendações oficiais do Python.
