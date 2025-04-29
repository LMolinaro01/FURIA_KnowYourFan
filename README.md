# Plano de Execução do Projeto

![image](https://github.com/user-attachments/assets/e1d01a07-c9a9-47be-a0a3-675b5e744398)


## Coleta de Dados Básicos e de Interesses do Usuário  
- **Formulário Inicial:** Criar um formulário em Jupyter Notebook (usando `ipywidgets` ou `Streamlit`) para capturar dados pessoais fundamentais: nome, CPF, endereço, data de nascimento, email etc. Validar formato de CPF (biblioteca `python-bcpf` ou validação via regex) e outros campos para evitar erros de digitação.  
- **Interesses e Atividades em e-sports:** Incluir no notebook seções ou perguntas interativas sobre interesses em e-sports, times preferidos (ex: FURIA), jogos mais acompanhados, frequência de eventos assistidos, ingressos ou periféricos adquiridos no último ano. Utilizar `pandas` para estruturar as respostas em um DataFrame. Poder-se-á simular coleta de dados de APIs públicas de eventos (por exemplo, dados de torneios CS:GO) ou pedir ao usuário que importe seu histórico (como um CSV de compras) para preencher esse perfil de maneira realista.  
- **Compras Relacionadas:** Se for aplicável, permitir o upload de extratos simplificados ou listas de compras (como merch de teams e-sports). Usar `pandas` ou `openpyxl` para ler esses arquivos e filtrar itens de interesse (palavras-chave relacionadas a jogos, marcas de e-sports, etc).  

## Validação de Identidade com Abordagem de IA  
- **Upload de Documentos:** Incluir um widget de upload de arquivos de imagem (RG, CNH ou passaporte) e, opcionalmente, uma selfie do usuário.  
- **OCR e Extração de Dados:** Utilizar uma biblioteca de OCR como `pytesseract` ou `easyocr` para extrair texto do documento. Comparar nome e CPF extraídos com os dados básicos fornecidos para consistência.  
- **Reconhecimento Facial:** Para fortalecer a validação, aplicar uma técnica de reconhecimento facial simples. Usar bibliotecas como `face_recognition` ou `OpenCV` com modelos pré-treinados para detectar rostos na selfie e na foto do documento, e então verificar se pertencem à mesma pessoa (por exemplo, comparando descritores faciais).  
- **Feedback de Validação:** Exibir no notebook resultados da validação (válido/inválido) com base na correspondência de texto e face. Fornecer mensagens orientativas caso haja inconsistências (ex: “CPF não confere com o documento enviado”).  

## Integração com Redes Sociais (Simulada)  
- **Linkagem de Contas:** Na ausência de integrações reais, simular o processo solicitando ao usuário os nomes de usuário ou perfis em redes sociais (Twitter, Facebook, Instagram). Criar células de código comentadas que demonstram como usar APIs (ex: `tweepy` para Twitter, `facebook-sdk` para Facebook) para conectar as contas.  
- **Extração de Atividades Relacionadas a e-sports:** Para cada rede social simulada, mostrar como coletar dados relevantes: por exemplo, obter os últimos *tweets* do usuário e filtrar menções a e-sports ou FURIA; listar as páginas seguidas no Facebook com temas de gaming; ou verificar hashtags usadas em posts do Instagram. Usar `requests` e `BeautifulSoup` ou clientes de API para simulação. Armazenar essas informações em DataFrames para análise.  
- **Monitoramento de Interações:** Demonstrar código que analisa curtidas, comentários ou retweets em publicações de e-sports (fingindo as permissões de API). Por exemplo, usar `tweepy` para buscar tweets que mencionem FURIA ou eventos de e-sports que o usuário retuitou ou comentou.  

## Enriquecimento de Perfil com Dados Sociais e Multimídia  
- **Análise de Comentários:** Para integrar comentários prévios do usuário no YouTube, Reddit e Twitter, incluir blocos que consumam APIs ou dados locais de análise anterior (supondo que existam). Usar `google-api-python-client` para extrair comentários de vídeos de e-sports do YouTube, `PRAW` para posts/comentários no Reddit, e `tweepy` ou dados simulados para tweets.  
- **Processamento de Linguagem Natural:** Aplicar NLP para entender o perfil do usuário: usar bibliotecas como `transformers` ou `spaCy` para classificar sentimento, identificar tópicos ou palavras-chave frequentes nesses comentários. Por exemplo, gerar um gráfico de palavras-chave mais mencionadas em e-sports, ou uma análise de sentimento geral sobre jogos específicos.  
- **Integração de Informações:** Combinar esses insights com os interesses declarados pelo usuário. Exibir visualmente (via `matplotlib` ou `seaborn`) uma nuvem de palavras ou gráfico que mostre as categorias de e-sports mais relevantes para o perfil (baseado em interesses + análise de comentários).  
- **Perfis em Sites de e-Sports:** Permitir que o usuário insira links para seus perfis em plataformas de e-sports (como GameBattles, HLTV, Liquipedia). Usar `requests` e `BeautifulSoup` para raspar detalhes do perfil (jogos, histórico de partidas). Em seguida, aplicar um modelo de IA (ex: `transformers` BERT) para classificar se o conteúdo textual do perfil é relevante às preferências do usuário (por exemplo, buscando termos de jogos citados pelo usuário). Mostrar se há “match” entre interesses do usuário e informações do perfil scraped.  

## Estruturação do Notebook  
- Organizar o notebook em seções claras conforme as etapas acima: **Coleta de Dados**, **Validação de Identidade**, **Integração de Redes Sociais**, **Enriquecimento com Dados Sociais**, **Conclusão**.  
- Incluir explicações breves em cada seção usando células Markdown, resumindo o objetivo daquela etapa. Combinar descrições em texto com células de código demonstrativas.  
- Sugerir bibliotecas específicas no contexto de cada etapa: por exemplo, mencionar `ipywidgets` ou `streamlit` na coleta de dados, `pytesseract`/`OpenCV` na validação de documentos, `tweepy`/`PRAW`/`BeautifulSoup` na integração social, e `transformers`/`spaCy` na análise de linguagem.  

## Dicas de Apresentação do Protótipo  
- **Formatação Atraente:** Usar cabeçalhos (`#`, `##`), listas e imagens (logotipos de e-sports, ícones de redes sociais) para tornar o notebook visualmente agradável. Células Markdown bem elaboradas ajudam na legibilidade.  
- **Interatividade:** Incluir elementos interativos (sliders, botões de upload, caixas de seleção) via `ipywidgets` para simular um fluxo real de uso. Isso torna a demonstração dinâmica mesmo no ambiente de notebook.  
- **Visualização de Dados:** Aproveitar gráficos (matplotlib, seaborn ou plotly) para mostrar perfis de interesse ou resultados das análises de comentários. Um gráfico de barras ou nuvem de palavras torna o conteúdo mais didático.  
- **Narração do Código:** Inserir comentários explicativos e outputs de exemplo que guiem o avaliador pelo processo passo a passo. Ao final, apresentar um breve resumo dos resultados obtidos para evidenciar que todos os requisitos foram atendidos.  

## Conclusão  
Este plano garante uma implementação completa dos requisitos do desafio, integrando coleta de informações pessoais e de interesse em e-sports, validação de identidade baseada em IA, simulação de integração social e enriquecimento de perfil com dados externos. A organização em seções claras, o uso de bibliotecas especializadas (ex: **Streamlit/ipywidgets** para interfaces, **OpenCV/face_recognition** para validação, **transformers/spaCy** para IA, **pandas** para dados) e as sugestões de apresentação asseguram uma entrega alinhada e de fácil acompanhamento, mesmo no formato de notebook.
