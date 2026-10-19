import json
import os
import re

import streamlit as st
from PIL import Image

# EcoScan - protótipo educacional de triagem de resíduos.
# A chave da API fica em .streamlit/secrets.toml ou na variável GEMINI_API_KEY.

st.set_page_config(
    page_title="EcoScan | Descarte consciente",
    page_icon="♻️",
    layout="centered",
)

# Informações de referência para materiais comuns.
# Tempos de decomposição são estimativas amplas e variam muito conforme o ambiente.
RESIDUOS = {
    "plástico": {
        "lixeira": "Vermelha",
        "hex": "#d62828",
        "tempo": "Pode levar centenas de anos (a estimativa varia conforme o tipo de plástico e o ambiente).",
        "descarte": "Esvazie a embalagem e, se possível, retire o excesso de resíduos. Confira as regras da coleta seletiva local.",
        "reuso": "Transforme uma garrafa limpa em vaso para pequenas plantas ou organizador, se for seguro e adequado.",
    },
    "papel": {
        "lixeira": "Azul",
        "hex": "#2878c8",
        "tempo": "De semanas a meses em condições favoráveis; papel revestido ou contaminado pode demorar mais.",
        "descarte": "Mantenha o papel seco e limpo. Papel engordurado ou muito sujo geralmente não deve ir com papel reciclável.",
        "reuso": "Use o verso para rascunhos, faça cartões ou transforme folhas usadas em papel para anotações.",
    },
    "metal": {
        "lixeira": "Amarela",
        "hex": "#e6b800",
        "tempo": "Pode levar décadas a centenas de anos, dependendo do metal e das condições ambientais.",
        "descarte": "Esvazie a embalagem. Evite deixar bordas cortantes expostas e siga as orientações locais.",
        "reuso": "Uma lata limpa pode virar porta-lápis, desde que as bordas sejam protegidas.",
    },
    "vidro": {
        "lixeira": "Verde",
        "hex": "#218c52",
        "tempo": "Pode persistir por milhares de anos; não há um prazo único confiável para todos os tipos de vidro.",
        "descarte": "Separe o vidro conforme a coleta local. Vidro quebrado deve ser embalado com segurança e identificado.",
        "reuso": "Um pote de vidro intacto pode virar recipiente de armazenamento depois de bem higienizado.",
    },
    "orgânico": {
        "lixeira": "Marrom",
        "hex": "#80552e",
        "tempo": "Varia de dias a meses; cascas e restos vegetais se decompõem mais rápido em condições adequadas.",
        "descarte": "Quando houver coleta de orgânicos, separe restos de alimentos de recicláveis secos. Compostagem é uma opção.",
        "reuso": "Cascas de frutas e restos vegetais adequados podem ser destinados a uma composteira.",
    },
    "não identificado": {
        "lixeira": "Confirme antes de descartar",
        "hex": "#64748b",
        "tempo": "Não é possível estimar sem identificar o material.",
        "descarte": "Verifique o símbolo da embalagem e as orientações da coleta seletiva do seu município.",
        "reuso": "Se o item estiver limpo e seguro, pense se pode ser reutilizado antes de descartá-lo.",
    },
}

def normalizar_categoria(categoria):
    c = (categoria or "").strip().lower()
    if any(p in c for p in ["pet", "plástico", "plastico", "polietileno", "embalagem plástica"]):
        return "plástico"
    if any(p in c for p in ["papel", "papelão", "papelao", "cartolina", "caderno"]):
        return "papel"
    if any(p in c for p in ["metal", "alumínio", "aluminio", "aço", "aco", "lata", "ferro"]):
        return "metal"
    if any(p in c for p in ["vidro", "garrafa de vidro", "pote de vidro"]):
        return "vidro"
    if any(p in c for p in ["orgânico", "organico", "casca", "fruta", "folha", "resto de alimento", "comida"]):
        return "orgânico"
    return "não identificado"

def analisar_com_gemini(image_bytes, mime_type, api_key):
    """Envia a imagem ao Gemini e pede uma resposta JSON."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    prompt = """
Você é um assistente educativo de triagem de resíduos no Brasil.
Observe a imagem e identifique apenas o resíduo mais evidente.
Responda SOMENTE com um objeto JSON válido, sem markdown, com estas chaves:
{
  "item": "nome curto do item",
  "categoria": "plástico, papel, metal, vidro, orgânico ou não identificado",
  "confianca": "alta, média ou baixa",
  "observacao": "uma frase curta sobre o que foi reconhecido"
}
Não invente certeza. Se não for possível identificar o material com segurança, use categoria "não identificado".
Não determine a lixeira nem o tempo de decomposição; esses dados serão fornecidos pela base local do aplicativo.
"""
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            prompt,
        ],
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
        ),
    )
    raw = response.text or "{}"
    # Proteção extra caso o modelo envolva o JSON em texto.
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if not match:
        raise ValueError("A IA não retornou um resultado em formato válido.")
    return json.loads(match.group(0))

def analisar_modo_demo(tipo):
    """Modo de demonstração: resultado fixo, sem chamada à API."""
    exemplos = {
        "Garrafa PET": {"item": "garrafa PET", "categoria": "plástico", "confianca": "alta", "observacao": "Exemplo de demonstração selecionado manualmente."},
        "Folha de caderno": {"item": "folha de caderno", "categoria": "papel", "confianca": "alta", "observacao": "Exemplo de demonstração selecionado manualmente."},
        "Lata de alumínio": {"item": "lata de alumínio", "categoria": "metal", "confianca": "alta", "observacao": "Exemplo de demonstração selecionado manualmente."},
        "Pote de vidro": {"item": "pote de vidro", "categoria": "vidro", "confianca": "alta", "observacao": "Exemplo de demonstração selecionado manualmente."},
        "Casca de fruta": {"item": "casca de fruta", "categoria": "orgânico", "confianca": "alta", "observacao": "Exemplo de demonstração selecionado manualmente."},
    }
    return exemplos[tipo]

# Estilo visual
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #f2fbf4 0%, #ffffff 42%); }
.hero { padding: 1.1rem 1.25rem; border-radius: 18px; background: #176b45; color: white; margin-bottom: 1rem; }
.hero h1 { margin: 0; font-size: 2.25rem; }
.hero p { margin: .35rem 0 0 0; opacity: .95; }
.small-note { color: #5b6470; font-size: .88rem; }
.result-card { border: 1px solid #e2e8e5; border-radius: 16px; padding: 1rem; background: white; margin: .6rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>♻️ EcoScan</h1>
  <p>Identifique resíduos. Descarte melhor. Reaproveite mais.</p>
</div>
""", unsafe_allow_html=True)

st.write("Envie uma foto ou use a câmera para receber orientações de descarte consciente.")
modo = st.radio(
    "Modo de funcionamento",
    ["Demonstração sem API", "Analisar imagem com Gemini"],
    horizontal=True,
    help="Use a demonstração para testar sem chave de API. Para analisar uma imagem real com IA, configure a chave do Gemini.",
)

col1, col2 = st.columns(2)
with col1:
    imagem_camera = st.camera_input("Tirar foto")
with col2:
    imagem_arquivo = st.file_uploader("Ou enviar uma imagem", type=["jpg", "jpeg", "png", "webp"])

imagem = imagem_arquivo if imagem_arquivo is not None else imagem_camera
if imagem is not None:
    try:
        img = Image.open(imagem)
        st.image(img, caption="Imagem selecionada", use_container_width=True)
    except Exception:
        st.error("Não consegui abrir essa imagem. Tente enviar um arquivo JPG ou PNG.")

if modo == "Demonstração sem API":
    st.info("Neste modo, escolha um exemplo abaixo. O resultado é ilustrativo e não foi reconhecido pela câmera.")
    exemplo = st.selectbox("Escolha um resíduo para demonstrar", [
        "Garrafa PET", "Folha de caderno", "Lata de alumínio", "Pote de vidro", "Casca de fruta"
    ])
    analisar = st.button("Gerar cartão de descarte", type="primary", use_container_width=True)
    if analisar:
        resultado = analisar_modo_demo(exemplo)
        st.session_state["resultado_ecoscan"] = resultado
        st.session_state["modo_demo_ecoscan"] = True
else:
    analisar = st.button("Analisar imagem com IA", type="primary", use_container_width=True, disabled=(imagem is None))
    if analisar:
        api_key = os.getenv("GEMINI_API_KEY", "")
        try:
            if not api_key:
                try:
                    api_key = st.secrets.get("GEMINI_API_KEY", "")
                except Exception:
                    api_key = ""
            if not api_key:
                st.error("Chave da API não encontrada. Configure GEMINI_API_KEY conforme o arquivo README.")
            elif imagem is None:
                st.warning("Primeiro tire uma foto ou envie uma imagem.")
            else:
                with st.spinner("A IA está analisando a imagem..."):
                    resultado = analisar_com_gemini(imagem.getvalue(), imagem.type or "image/jpeg", api_key)
                st.session_state["resultado_ecoscan"] = resultado
                st.session_state["modo_demo_ecoscan"] = False
        except Exception as e:
            st.error("Não foi possível analisar a imagem. Confira sua internet, a chave da API e as instruções no README.")
            st.caption(f"Detalhe técnico: {e}")

resultado = st.session_state.get("resultado_ecoscan")
if resultado:
    categoria = normalizar_categoria(resultado.get("categoria"))
    dados = RESIDUOS[categoria]
    modo_demo_resultado = st.session_state.get("modo_demo_ecoscan", False)

    st.divider()
    st.subheader("Resultado da análise")
    st.markdown(f"### {resultado.get('item', 'Resíduo identificado')}")
    st.caption(f"Categoria: {categoria.title()} · Confiança informada: {resultado.get('confianca', 'não informada')}")
    st.write(resultado.get("observacao", ""))

    st.markdown(
        f"""<div style="background:{dados['hex']}; color:{'#1f2937' if categoria == 'metal' else 'white'};
        padding:1rem 1.2rem; border-radius:14px; margin:.5rem 0 1rem 0;">
        <div style="font-size:.85rem; opacity:.95;">COR INDICADA DA COLETA SELETIVA</div>
        <div style="font-size:1.6rem; font-weight:700;">{dados['lixeira']}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### ⏳ Decomposição")
        st.write(dados["tempo"])
    with c2:
        st.markdown("#### 💡 Reaproveitamento")
        st.write(dados["reuso"])

    st.markdown("#### Como descartar")
    st.write(dados["descarte"])
    st.warning("A cor das lixeiras e a aceitação de materiais podem variar conforme o serviço de coleta local. Confira as orientações do seu município. Os tempos são estimativas, não prazos exatos.")
    if modo_demo_resultado:
        st.caption("Modo demonstração: a categoria foi escolhida manualmente e não reconhecida por IA.")
    else:
        st.caption("A análise visual pode errar, especialmente se o objeto estiver sujo, amassado, misturado ou parcialmente escondido.")

with st.expander("Sobre o EcoScan"):
    st.write("O EcoScan é um protótipo educativo que combina análise de imagens com informações ambientais organizadas no próprio aplicativo. Ele ajuda a orientar, mas não substitui as regras da coleta seletiva do município.")
    st.write("No padrão brasileiro de coleta seletiva, as cores mais comuns são: azul para papel, vermelho para plástico, verde para vidro, amarelo para metal e marrom para resíduos orgânicos.")
