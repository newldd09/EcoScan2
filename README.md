# EcoScan — guia para iniciantes

Este projeto é um protótipo escolar em Python + Streamlit. Ele permite tirar uma foto ou enviar uma imagem e exibir informações de descarte. Há dois modos:

- **Demonstração sem API:** escolhe um exemplo manualmente. Não usa IA nem precisa de chave.
- **Analisar imagem com Gemini:** envia a imagem à API Gemini para reconhecer o resíduo. Precisa de internet e de uma chave de API.

## 1. Instalar o Python

Instale o Python 3.11 ou uma versão recente compatível em https://www.python.org/downloads/ . No instalador do Windows, marque **Add Python to PATH**.

## 2. Descompactar o projeto

Extraia o ZIP para uma pasta, por exemplo `C:\EcoScan`.

## 3. Abrir o terminal na pasta

No Windows, abra a pasta `EcoScan`, clique na barra de endereço do Explorador de Arquivos, digite `cmd` e aperte Enter.

## 4. Criar um ambiente e instalar as bibliotecas

Execute estes comandos, um de cada vez:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Se o comando `python` não funcionar, tente `py` no lugar dele.

## 5. Executar o aplicativo

No mesmo terminal:

```bash
streamlit run app.py
```

O navegador deve abrir com o EcoScan. Se não abrir, copie o endereço local mostrado no terminal (normalmente `http://localhost:8501`) e cole no navegador.

## 6. Usar o modo de demonstração

Selecione **Demonstração sem API**, escolha um resíduo e clique em **Gerar cartão de descarte**. Esse modo é útil para ensaiar o seminário sem configurar uma API.

## 7. Ativar a análise de imagem com Gemini

1. Consulte o Google AI Studio e crie uma chave de API: https://aistudio.google.com/app/apikey
2. Na pasta do projeto, crie uma pasta chamada `.streamlit`.
3. Dentro dela, crie um arquivo chamado `secrets.toml`.
4. Coloque dentro dele esta linha, substituindo pelo valor da sua chave:

```toml
GEMINI_API_KEY = "COLE_SUA_CHAVE_AQUI"
```

5. Salve o arquivo, reinicie o aplicativo se necessário e selecione **Analisar imagem com Gemini**.

**Segurança:** não publique a chave, não a coloque em apresentações, prints, repositórios públicos ou no código enviado aos colegas. Se a chave vazar, revogue-a e gere outra. A disponibilidade e os limites de uso dependem da conta e das condições atuais do Google.

## Estrutura do projeto

```text
ec oscan_projeto/
├── app.py
├── requirements.txt
└── README.md
```

## Observações importantes

- O Gemini identifica visualmente o item, mas o aplicativo usa uma pequena base local para cor da lixeira, orientação de descarte, decomposição e reaproveitamento. Isso reduz a chance de a IA inventar essas informações.
- Os tempos de decomposição são aproximados e variam muito conforme material e ambiente.
- As cores indicadas seguem o padrão brasileiro comum de coleta seletiva, mas é necessário conferir o serviço municipal.
- Para um projeto escolar, não use o protótipo como única fonte para decisões ambientais reais.
