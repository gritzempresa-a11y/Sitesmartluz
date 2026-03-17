# -*- coding: utf-8 -*-
import sqlite3
import secrets

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Smart Luz", layout="wide")

# =========================
# BANCO DE DADOS
# =========================

conn = sqlite3.connect("usuarios.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios(
nome TEXT,
email TEXT UNIQUE,
senha TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS diagnosticos(
id INTEGER PRIMARY KEY AUTOINCREMENT,
usuario TEXT,
pessoas INTEGER,
eletrodomesticos INTEGER,
lampadas INTEGER,
status TEXT,
valor_conta REAL,
economia REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS estatisticas(
acessos INTEGER,
formularios INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS reset_tokens(
email TEXT,
token TEXT UNIQUE
)
""")

conn.commit()

cursor.execute("SELECT COUNT(*) FROM estatisticas")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO estatisticas (acessos, formularios) VALUES (0, 0)")
    conn.commit()


def garantir_coluna(nome_coluna: str, tipo_sql: str) -> None:
    cursor.execute("PRAGMA table_info(diagnosticos)")
    colunas = [col[1] for col in cursor.fetchall()]
    if nome_coluna not in colunas:
        cursor.execute(f"ALTER TABLE diagnosticos ADD COLUMN {nome_coluna} {tipo_sql}")
        conn.commit()


garantir_coluna("usuario", "TEXT")
garantir_coluna("pessoas", "INTEGER")
garantir_coluna("eletrodomesticos", "INTEGER")
garantir_coluna("lampadas", "INTEGER")
garantir_coluna("status", "TEXT")
garantir_coluna("valor_conta", "REAL")
garantir_coluna("economia", "REAL")


# =========================
# FUNÇÕES AUXILIARES
# =========================

def gerar_link_recuperacao(token: str) -> str:
    return f"?token={token}"


def limpar_query_params():
    st.query_params.clear()


# =========================
# CSS
# =========================

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"]{
    overflow-x: hidden !important;
    max-width: 100% !important;
}

.block-container{
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 1450px;
    width: 100% !important;
    overflow-x: hidden !important;
}

.card{
    background:black;
    color:white;
    padding:25px;
    border-radius:15px;
    text-align:center;
    box-shadow:0 6px 15px rgba(0,0,0,0.2);
}

.stButton>button{
    background:black;
    color:white;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# CONTROLE DE PÁGINA
# =========================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "resultado" not in st.session_state:
    st.session_state.resultado = None

if "usuario_nome" not in st.session_state:
    st.session_state.usuario_nome = ""

if "usuario_email" not in st.session_state:
    st.session_state.usuario_email = ""

if "acesso_contado" not in st.session_state:
    st.session_state.acesso_contado = False

token_url = st.query_params.get("token")
if token_url:
    st.session_state.page = "redefinir_senha"

# =========================
# HOME
# =========================

if st.session_state.page == "home":

    if not st.session_state.acesso_contado:
        cursor.execute("UPDATE estatisticas SET acessos = acessos + 1")
        conn.commit()
        st.session_state.acesso_contado = True

    # 🔥 AJUSTE DA CAPA (RESPONSIVO MOBILE)
    st.markdown("""
    <style>
    .capa-container{
        width: 100%;
        display: flex;
        justify-content: center;
    }

    .capa-img{
        width: 100%;
        max-width: 100%;
        height: auto;
        object-fit: contain;
        border-radius: 18px;
    }

    @media (max-width: 768px){
        .capa-img{
            width: 100%;
            height: auto;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="capa-container">
        <img src="capa_smartluz.png" class="capa-img">
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            st.session_state.page = "login"
            st.rerun()

    with col2:
        if st.button("Cadastro"):
            st.session_state.page = "cadastro"
            st.rerun()

    st.markdown("---")
    st.header("Por que isso é importante?")

    st.markdown("""
    <div class="card">
    <h3>🔌 Reduza o consumo</h3>
    Pequenas mudanças reduzem o gasto de energia.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
    <h3>💰 Economize dinheiro</h3>
    Diminua o valor da conta de luz.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
    <h3>🌎 Ajude o planeta</h3>
    Reduza o desperdício de energia.
    </div>
    """, unsafe_allow_html=True)

# =========================
# LOGIN
# =========================

elif st.session_state.page == "login":

    st.title("Login")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        cursor.execute(
            "SELECT * FROM usuarios WHERE email=? AND senha=?",
            (email, senha)
        )

        usuario = cursor.fetchone()

        if usuario:
            st.session_state.usuario_nome = usuario[0]
            st.session_state.usuario_email = usuario[1]
            st.session_state.page = "diagnostico"
            st.rerun()
        else:
            st.error("Email ou senha incorretos")

    if st.button("Voltar"):
        st.session_state.page = "home"
        st.rerun()

# =========================
# CADASTRO
# =========================

elif st.session_state.page == "cadastro":

    st.title("Cadastro")

    nome = st.text_input("Nome")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Criar conta"):

        try:
            cursor.execute(
                "INSERT INTO usuarios VALUES (?,?,?)",
                (nome, email, senha)
            )
            conn.commit()
            st.success("Usuário criado!")
            st.session_state.page = "login"
            st.rerun()
        except:
            st.error("Email já cadastrado")

    if st.button("Voltar"):
        st.session_state.page = "home"
        st.rerun()
