import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

USUARIO_ADMIN = "admin"
SENHA_ADMIN = "1234"

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("Login - Tattoo Studio")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario == USUARIO_ADMIN and senha == SENHA_ADMIN:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

    st.stop()

st.set_page_config(page_title="Tattoo Studio", page_icon="🖤", layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #0f0f0f;
    color: white;
}
h1, h2, h3 {
    color: white;
}
.card {
    background-color: #1c1c1c;
    padding: 25px 10px;
    border-radius: 20px;
    border: 1px solid #333;
    text-align: center;
    min-height: 150px;
    width: 100%;
}
.card h1 {
    font-size: 38px;
    margin-top: 15px;
}
.card h2 {
    font-size: 22px;
}
section[data-testid="stSidebar"] {
    background-color: #161616;
}
</style>
""", unsafe_allow_html=True)

conexao = sqlite3.connect("tattoo_studio.db")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS agendamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    telefone TEXT,
    estilo TEXT,
    servico TEXT,
    tamanho TEXT,
    local_corpo TEXT,
    descricao TEXT,
    data TEXT,
    horario TEXT,
    valor_estimado REAL,
    sinal REAL,
    status TEXT
)
""")
conexao.commit()

st.sidebar.title("🖤 Tattoo Studio")

menu = st.sidebar.radio(
    "Menu",
    ["Início", "Agendar Horário", "Portfólio", "Agendamentos", "IA Atendimento"]
)

def calcular_valor(servico, tamanho):
    valor = 0

    if servico == "Tatuagem nova":
        valor += 250
    elif servico == "Cobertura":
        valor += 350
    elif servico == "Retoque":
        valor += 120

    if tamanho == "Pequena":
        valor += 100
    elif tamanho == "Média":
        valor += 250
    elif tamanho == "Grande":
        valor += 500

    return valor

if menu == "Início":
    st.title("Tattoo Studio")
    st.subheader("Sistema de Agendamento e Portfólio")

    cursor.execute("SELECT COUNT(*) FROM agendamentos")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM agendamentos WHERE status = 'Agendado'")
    agendados = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(valor_estimado) FROM agendamentos")
    faturamento = cursor.fetchone()[0] or 0

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown(f"""
        <div class="card">
            <h2>Agenda</h2>
            <h1>{total}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card">
            <h2>Agendados</h2>
            <h1>{agendados}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="card">
            <h2>Estimado</h2>
            <h1>R$ {faturamento:.0f}</h1>
        </div>
        """, unsafe_allow_html=True)

    st.write("Aplicativo web para gerenciamento de agendamentos, orçamento e portfólio de estúdio de tatuagem.")

elif menu == "Agendar Horário":
    st.title("Agendar Horário")

    nome = st.text_input("Nome do cliente")
    telefone = st.text_input("Telefone")

    servico = st.selectbox(
        "Serviço",
        ["Tatuagem nova", "Cobertura", "Retoque"]
    )

    estilo = st.selectbox(
        "Estilo da tatuagem",
        ["Fine Line", "Blackwork", "Old School", "Realismo", "Oriental", "Tribal"]
    )

    tamanho = st.selectbox(
        "Tamanho",
        ["Pequena", "Média", "Grande"]
    )

    local_corpo = st.selectbox(
        "Local do corpo",
        ["Braço", "Antebraço", "Perna", "Costas", "Peito", "Mão", "Pescoço", "Outro"]
    )

    descricao = st.text_area("Descrição da ideia da tattoo")

    data = st.date_input("Data desejada", min_value=date.today())
    horario = st.time_input("Horário desejado")

    valor_estimado = calcular_valor(servico, tamanho)
    sinal = valor_estimado * 0.30

    st.info(f"Valor estimado: R$ {valor_estimado:.2f}")
    st.warning(f"Sinal sugerido: R$ {sinal:.2f}")

    if st.button("Confirmar Agendamento"):
        if nome and telefone:
            cursor.execute("""
                INSERT INTO agendamentos
                (nome, telefone, estilo, servico, tamanho, local_corpo, descricao, data, horario, valor_estimado, sinal, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nome,
                telefone,
                estilo,
                servico,
                tamanho,
                local_corpo,
                descricao,
                str(data),
                str(horario),
                valor_estimado,
                sinal,
                "Agendado"
            ))

            conexao.commit()
            st.success("Agendamento realizado com sucesso!")
        else:
            st.error("Preencha nome e telefone.")

elif menu == "Portfólio":
    st.title("Portfólio do Estúdio")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.image("imagens/tattoo1.jpg", width="stretch")
        st.write("Fine Line")

    with col2:
        st.image("imagens/tattoo2.jpg", width="stretch")
        st.write("Blackwork")

    with col3:
        st.image("imagens/tattoo3.jpg", width="stretch")
        st.write("Old School")

elif menu == "Agendamentos":
    st.title("Agendamentos Registrados")

    cursor.execute("""
        SELECT id, nome, telefone, servico, estilo, tamanho, local_corpo, data, horario, valor_estimado, sinal, status
        FROM agendamentos
    """)
    dados = cursor.fetchall()

    if dados:
        tabela = pd.DataFrame(dados, columns=[
            "ID", "Nome", "Telefone", "Serviço", "Estilo", "Tamanho",
            "Local", "Data", "Horário", "Valor", "Sinal", "Status"
        ])
        st.dataframe(tabela, use_container_width=True)

        st.subheader("Enviar confirmação por WhatsApp")

        telefone_whats = st.text_input("Telefone com DDD, somente números")

        mensagem = st.text_area(
            "Mensagem",
            "Olá! Seu agendamento no Tattoo Studio foi confirmado. Qualquer dúvida, estamos à disposição."
        )

        if st.button("Abrir WhatsApp"):
            link = f"https://wa.me/55{telefone_whats}?text={mensagem}"
            st.markdown(f"[Clique aqui para enviar no WhatsApp]({link})")
    else:
        st.info("Nenhum agendamento registrado ainda.")
        
elif menu == "IA Atendimento":
    st.title("IA de Atendimento")

    st.write("Assistente virtual para responder dúvidas de clientes do estúdio.")

    pergunta = st.text_input("Cliente:")

    if st.button("Responder"):
        pergunta_lower = pergunta.lower()

        if "preço" in pergunta_lower or "valor" in pergunta_lower:
            resposta = "O valor depende do tamanho, estilo e local do corpo. Você pode fazer um orçamento na aba Agendar Horário."

        elif "horário" in pergunta_lower or "agenda" in pergunta_lower or "marcar" in pergunta_lower:
            resposta = "Temos horários disponíveis durante a semana. Informe a data desejada para verificar a possibilidade de agendamento."

        elif "pix" in pergunta_lower or "pagamento" in pergunta_lower:
            resposta = "Aceitamos pagamento por PIX. Para confirmar o agendamento, é recomendado pagar um sinal."

        elif "dor" in pergunta_lower:
            resposta = "A dor varia conforme o local do corpo e a sensibilidade da pessoa. Regiões com menos gordura costumam ser mais sensíveis."

        elif "cicatrização" in pergunta_lower or "cuidados" in pergunta_lower:
            resposta = "Após a tatuagem, mantenha o local limpo, evite sol, piscina e siga as orientações do tatuador."

        else:
            resposta = "Olá! Posso ajudar com agendamento, valores, estilos, cuidados e formas de pagamento."

        st.success(resposta)        