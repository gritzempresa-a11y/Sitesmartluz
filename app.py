# -*- coding: utf-8 -*-
import os
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
    base_url = os.getenv("APP_URL", "http://localhost:8501")
    return f"{base_url}?token={token}"


def limpar_query_params():
    st.query_params.clear()


# =========================
# CSS
# =========================

st.markdown("""
<style>

.block-container{
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 1450px;
}

.card{
    background:black;
    color:white;
    padding:25px;
    border-radius:15px;
    text-align:center;
    box-shadow:0 6px 15px rgba(0,0,0,0.2);
    transition:0.3s;
    min-height:145px;
    display:flex;
    flex-direction:column;
    justify-content:center;
}

.card:hover{
    transform:translateY(-5px);
}

.stButton>button{
    background:black;
    color:white;
    border-radius:10px;
    padding:10px 25px;
    font-weight:bold;
    border:none;
}

.stButton>button:hover{
    background:#333;
}

.grafico-fixo{
    position:sticky;
    top:80px;
    background:white;
    padding:10px;
    border-radius:10px;
}

img{
    border-radius:12px;
}

@media (max-width: 768px){
    .block-container{
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
        padding-top: 0.2rem !important;
        padding-bottom: 0.5rem !important;
    }

    .grafico-fixo{
        position:relative;
        top:0;
    }

    .card{
        padding:18px;
        min-height:auto;
        margin-bottom:10px;
    }
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

# se abriu com token na URL, vai direto para redefinição
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

    st.image("capa_smartluz.png", use_container_width=True)

    col1, col2, col3 = st.columns([5, 1, 1])

    with col2:
        if st.button("Login"):
            st.session_state.page = "login"
            st.rerun()

    with col3:
        if st.button("Cadastro"):
            st.session_state.page = "cadastro"
            st.rerun()

    st.markdown("---")

    st.header("Por que isso é importante?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card">
        <h3>🔌 Reduza o consumo</h3>
        Pequenas mudanças reduzem o gasto de energia.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
        <h3>💰 Economize dinheiro</h3>
        Diminua o valor da conta de luz.
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
        <h3>🌎 Ajude o planeta</h3>
        Reduza o desperdício de energia.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.header("Sobre o Smart Luz")

    st.markdown("""
O **Smart Luz** é uma ferramenta de educação energética desenvolvida como **projeto acadêmico para a disciplina de Inovação Sustentável**.

Nosso objetivo é incentivar **mudanças de hábito que promovam inovação sustentável nas residências**, ajudando as pessoas a entender melhor o consumo de energia e como pequenas atitudes podem gerar economia financeira e benefícios ambientais.
""")

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

            st.success("Usuário criado com sucesso!")

            st.session_state.page = "login"
            st.rerun()

        except Exception:
            st.error("Email já cadastrado.")

    if st.button("Voltar"):
        st.session_state.page = "home"
        st.rerun()

# =========================
# LOGIN
# =========================

elif st.session_state.page == "login":

    st.title("Login")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    col1, col2 = st.columns(2)

    with col1:
        entrar = st.button("Entrar")

    with col2:
        esqueceu = st.button("Esqueci a senha")

    if entrar:

        if email.strip().lower() == "admin@smartluz.com" and senha.strip() == "admin123":
            st.session_state.page = "admin"
            st.rerun()

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

    if esqueceu:
        st.session_state.page = "esqueci_senha"
        st.rerun()

    if st.button("Voltar"):
        st.session_state.page = "home"
        st.rerun()

# =========================
# ESQUECI A SENHA
# =========================

elif st.session_state.page == "esqueci_senha":

    st.title("Recuperar senha")

    email_rec = st.text_input("Digite o e-mail cadastrado")

    if st.button("Gerar link de recuperação"):
        cursor.execute("SELECT * FROM usuarios WHERE email=?", (email_rec,))
        usuario = cursor.fetchone()

        if not usuario:
            st.error("E-mail não encontrado.")
        else:
            token = secrets.token_urlsafe(24)
            cursor.execute("DELETE FROM reset_tokens WHERE email=?", (email_rec,))
            cursor.execute(
                "INSERT INTO reset_tokens (email, token) VALUES (?, ?)",
                (email_rec, token)
            )
            conn.commit()

            link = gerar_link_recuperacao(token)

            st.success("Link de recuperação gerado com sucesso.")
            st.markdown(f"[Clique aqui para redefinir a senha]({link})")
            st.text(link)

    if st.button("Voltar para login"):
        st.session_state.page = "login"
        st.rerun()

# =========================
# REDEFINIR SENHA
# =========================

elif st.session_state.page == "redefinir_senha":

    st.title("Cadastrar nova senha")

    token = st.query_params.get("token")

    if not token:
        st.error("Token inválido ou ausente.")
    else:
        cursor.execute("SELECT email FROM reset_tokens WHERE token=?", (token,))
        dado = cursor.fetchone()

        if not dado:
            st.error("Link inválido ou expirado.")
        else:
            email_reset = dado[0]
            st.write(f"Conta: **{email_reset}**")

            nova_senha = st.text_input("Nova senha", type="password")
            confirmar_senha = st.text_input("Confirmar nova senha", type="password")

            if st.button("Salvar nova senha"):
                if not nova_senha or not confirmar_senha:
                    st.warning("Preencha os dois campos de senha.")
                elif nova_senha != confirmar_senha:
                    st.error("As senhas não coincidem.")
                else:
                    cursor.execute(
                        "UPDATE usuarios SET senha=? WHERE email=?",
                        (nova_senha, email_reset)
                    )
                    cursor.execute("DELETE FROM reset_tokens WHERE token=?", (token,))
                    conn.commit()
                    limpar_query_params()
                    st.success("Senha alterada com sucesso.")
                    if st.button("Ir para login"):
                        st.session_state.page = "login"
                        st.rerun()

    if st.button("Voltar"):
        limpar_query_params()
        st.session_state.page = "login"
        st.rerun()

# =========================
# DIAGNÓSTICO
# =========================

elif st.session_state.page == "diagnostico":

    st.title("Diagnóstico de Consumo")

    with st.form("form_diagnostico"):

        st.subheader("Perfil da Residência")

        pessoas = st.selectbox(
            "Quantas pessoas moram na casa?",
            ["Selecione", "1", "2", "3", "4", "5 ou mais"]
        )

        tipo_imovel = st.radio(
            "O imóvel é:",
            ["Casa", "Apartamento"]
        )

        conta = st.selectbox(
            "Valor médio da conta de luz:",
            ["Selecione", "Até R$100", "R$101 a R$200", "R$201 a R$300", "Acima de R$300", "Não sei informar"]
        )

        st.subheader("Chuveiro Elétrico")

        chuveiro = st.radio(
            "Você utiliza chuveiro elétrico?",
            ["Sim", "Não"]
        )

        banho = st.selectbox(
            "Tempo médio de banho:",
            ["Selecione", "5 min", "10 min", "15 min", "20 min"]
        )

        posicao_chuveiro = st.radio(
            "Posição do chuveiro:",
            ["Verão", "Inverno", "Sempre no máximo"]
        )

        st.subheader("Iluminação")

        lampadas = st.selectbox(
            "Tipo de lâmpadas:",
            ["Selecione", "LED", "Fluorescente", "Incandescente"]
        )

        apagar_luz = st.radio(
            "Apaga a luz ao sair do ambiente?",
            ["Sempre", "Às vezes", "Raramente"]
        )

        st.subheader("Ar Condicionado")

        ar = st.radio(
            "Possui ar condicionado?",
            ["Não", "Sim"]
        )

        horas_ar = st.selectbox(
            "Horas médias de uso por dia:",
            ["Selecione", "1 a 3 horas", "4 a 6 horas", "Mais de 6 horas", "Não se aplica"]
        )

        temperatura_ar = st.selectbox(
            "Temperatura média utilizada:",
            ["Selecione", "18º a 20º", "21º a 23º", "24º a 26º", "Não sei", "Não se aplica"]
        )

        st.subheader("Eletrodomésticos")

        tv = st.selectbox(
            "Quantidade de TVs",
            ["Selecione", "1", "2", "3 ou mais", "Não se aplica"]
        )

        geladeira = st.radio(
            "Geladeira é:",
            ["Nova (até 5 anos)", "Antiga (mais de 5 anos)", "Não sei"]
        )

        maquina_lavar = st.selectbox(
            "Uso da máquina de lavar:",
            ["Selecione", "1 vez por semana", "2 a 3 vezes", "4 ou mais vezes", "Não se aplica"]
        )

        standby = st.radio(
            "Aparelhos ficam em stand-by?",
            ["Sim, vários", "Apenas alguns", "Não"]
        )

        st.subheader("Consumo Consciente")

        selo = st.radio(
            "Você conhece o selo de eficiência energética?",
            ["Sim", "Já ouvi falar", "Não"]
        )

        plano = st.radio(
            "Gostaria de receber um plano personalizado de economia?",
            ["Sim", "Não"]
        )

        gerar = st.form_submit_button("Gerar diagnóstico")

    if gerar:

        if (
            pessoas == "Selecione"
            or conta == "Selecione"
            or banho == "Selecione"
            or lampadas == "Selecione"
            or tv == "Selecione"
        ):
            st.warning("⚠️ Responda todas as perguntas antes de gerar o diagnóstico.")
            st.stop()

        if ar == "Sim" and (horas_ar == "Selecione" or temperatura_ar == "Selecione"):
            st.warning("⚠️ Preencha corretamente as perguntas do ar condicionado.")
            st.stop()

        if maquina_lavar == "Selecione":
            st.warning("⚠️ Responda todas as perguntas antes de gerar o diagnóstico.")
            st.stop()

        # =========================
        # SCORE MAIS REALISTA
        # =========================

        score_consumo = 0

        if pessoas == "1":
            score_consumo += 2
        elif pessoas == "2":
            score_consumo += 5
        elif pessoas == "3":
            score_consumo += 8
        elif pessoas == "4":
            score_consumo += 11
        else:
            score_consumo += 14

        if chuveiro == "Sim":
            score_consumo += 18

            if banho == "5 min":
                score_consumo += 4
            elif banho == "10 min":
                score_consumo += 10
            elif banho == "15 min":
                score_consumo += 18
            elif banho == "20 min":
                score_consumo += 28

            if posicao_chuveiro == "Verão":
                score_consumo += 2
            elif posicao_chuveiro == "Inverno":
                score_consumo += 8
            elif posicao_chuveiro == "Sempre no máximo":
                score_consumo += 14

        if lampadas == "LED":
            score_consumo += 2
        elif lampadas == "Fluorescente":
            score_consumo += 7
        elif lampadas == "Incandescente":
            score_consumo += 16

        if apagar_luz == "Sempre":
            score_consumo += 0
        elif apagar_luz == "Às vezes":
            score_consumo += 5
        elif apagar_luz == "Raramente":
            score_consumo += 10

        if ar == "Sim":
            score_consumo += 16

            if horas_ar == "1 a 3 horas":
                score_consumo += 8
            elif horas_ar == "4 a 6 horas":
                score_consumo += 15
            elif horas_ar == "Mais de 6 horas":
                score_consumo += 24

            if temperatura_ar == "18º a 20º":
                score_consumo += 16
            elif temperatura_ar == "21º a 23º":
                score_consumo += 8
            elif temperatura_ar == "24º a 26º":
                score_consumo += 2
            elif temperatura_ar == "Não sei":
                score_consumo += 6

        if tv == "1":
            score_consumo += 3
        elif tv == "2":
            score_consumo += 6
        elif tv == "3 ou mais":
            score_consumo += 10

        if geladeira == "Nova (até 5 anos)":
            score_consumo += 4
        elif geladeira == "Não sei":
            score_consumo += 8
        elif geladeira == "Antiga (mais de 5 anos)":
            score_consumo += 16

        if maquina_lavar == "1 vez por semana":
            score_consumo += 3
        elif maquina_lavar == "2 a 3 vezes":
            score_consumo += 7
        elif maquina_lavar == "4 ou mais vezes":
            score_consumo += 12

        if standby == "Não":
            score_consumo += 0
        elif standby == "Apenas alguns":
            score_consumo += 4
        elif standby == "Sim, vários":
            score_consumo += 9

        if selo == "Sim":
            score_consumo += 0
        elif selo == "Já ouvi falar":
            score_consumo += 2
        elif selo == "Não":
            score_consumo += 5

        if conta == "Até R$100":
            valor_conta = 100
            score_consumo += 0
        elif conta == "R$101 a R$200":
            valor_conta = 200
            score_consumo += 4
        elif conta == "R$201 a R$300":
            valor_conta = 300
            score_consumo += 8
        elif conta == "Acima de R$300":
            valor_conta = 400
            score_consumo += 12
        else:
            valor_conta = 250
            score_consumo += 5

        if score_consumo <= 45:
            nivel = "Baixo consumo"
            reducao = 0.10
        elif score_consumo <= 85:
            nivel = "Consumo moderado"
            reducao = 0.22
        else:
            nivel = "Alto consumo"
            reducao = 0.35

        economia = valor_conta * reducao
        score = min(score_consumo, 100)

        eletrodomesticos_nota = 0
        lampadas_chuveiro_nota = 0

        if tv == "1":
            eletrodomesticos_nota += 1
        elif tv == "2":
            eletrodomesticos_nota += 2
        elif tv == "3 ou mais":
            eletrodomesticos_nota += 3
        else:
            eletrodomesticos_nota += 0

        if geladeira == "Nova (até 5 anos)":
            eletrodomesticos_nota += 1
        elif geladeira == "Não sei":
            eletrodomesticos_nota += 2
        else:
            eletrodomesticos_nota += 3

        if maquina_lavar == "1 vez por semana":
            eletrodomesticos_nota += 1
        elif maquina_lavar == "2 a 3 vezes":
            eletrodomesticos_nota += 2
        elif maquina_lavar == "4 ou mais vezes":
            eletrodomesticos_nota += 3
        else:
            eletrodomesticos_nota += 0

        if standby == "Não":
            eletrodomesticos_nota += 0
        elif standby == "Apenas alguns":
            eletrodomesticos_nota += 1
        else:
            eletrodomesticos_nota += 2

        if lampadas == "LED":
            lampadas_chuveiro_nota += 1
        elif lampadas == "Fluorescente":
            lampadas_chuveiro_nota += 2
        else:
            lampadas_chuveiro_nota += 3

        if banho == "5 min":
            lampadas_chuveiro_nota += 1
        elif banho == "10 min":
            lampadas_chuveiro_nota += 2
        elif banho == "15 min":
            lampadas_chuveiro_nota += 3
        else:
            lampadas_chuveiro_nota += 4

        if posicao_chuveiro == "Verão":
            lampadas_chuveiro_nota += 1
        elif posicao_chuveiro == "Inverno":
            lampadas_chuveiro_nota += 2
        else:
            lampadas_chuveiro_nota += 3

        if apagar_luz == "Sempre":
            lampadas_chuveiro_nota += 0
        elif apagar_luz == "Às vezes":
            lampadas_chuveiro_nota += 1
        else:
            lampadas_chuveiro_nota += 2

        pessoas_num = 5 if pessoas == "5 ou mais" else int(pessoas)

        usuario_para_salvar = st.session_state.usuario_nome if st.session_state.usuario_nome else st.session_state.usuario_email

        cursor.execute(
            """
            INSERT INTO diagnosticos
            (usuario, pessoas, eletrodomesticos, lampadas, status, valor_conta, economia)
            VALUES (?,?,?,?,?,?,?)
            """,
            (
                usuario_para_salvar,
                pessoas_num,
                eletrodomesticos_nota,
                lampadas_chuveiro_nota,
                nivel,
                valor_conta,
                economia
            )
        )

        cursor.execute("UPDATE estatisticas SET formularios = formularios + 1")
        conn.commit()

        st.session_state.resultado = {
            "nivel": nivel,
            "valor": valor_conta,
            "economia": economia,
            "score": score
        }

    if st.session_state.resultado:

        r = st.session_state.resultado

        st.header("Diagnóstico Smart Luz")

        st.success(r["nivel"])

        st.metric("Score energético", f"{r['score']} / 100")

        st.markdown('<div class="grafico-fixo">', unsafe_allow_html=True)

        dados_grafico_diag = pd.DataFrame({
            "Categoria": ["Conta Atual", "Após economia"],
            "Valor": [r["valor"], r["valor"] - r["economia"]]
        })

        grafico_diag = alt.Chart(dados_grafico_diag).mark_bar(size=90).encode(
            x=alt.X(
                "Categoria:N",
                title="",
                sort=["Conta Atual", "Após economia"],
                axis=alt.Axis(
                    labelAngle=0,
                    labelFontSize=18,
                    titleFontSize=18,
                    labelPadding=14,
                    labelLimit=220
                )
            ),
            y=alt.Y(
                "Valor:Q",
                title="Valor",
                axis=alt.Axis(labelFontSize=15, titleFontSize=18)
            ),
            color=alt.Color(
                "Categoria:N",
                scale=alt.Scale(
                    domain=["Conta Atual", "Após economia"],
                    range=["#1B5E20", "#81C784"]
                ),
                legend=None
            )
        ).properties(
            height=420
        ).configure_view(
            strokeWidth=0
        )

        st.altair_chart(grafico_diag, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.info(f"Economia estimada: **R${r['economia']:.2f} por mês**")
        st.info(f"Economia anual estimada: **R${r['economia']*12:.2f} por ano**")

        if r["nivel"] == "Baixo consumo":

            st.markdown("""
### Estimativa de Redução
Se algumas mudanças forem aplicadas, sua residência pode reduzir até **5% a 15% do consumo de energia.**

### Dicas Personalizadas
Seus hábitos de consumo já são bastante eficientes! Continue assim.

• Fique atento ao **selo de eficiência energética** ao comprar novos eletrodomésticos.

### Energia inteligente, planeta sustentável
Quando reduzimos o desperdício de energia em casa, não economizamos apenas dinheiro.  
Também ajudamos a reduzir a necessidade de geração de energia, diminuindo impactos ambientais e contribuindo para um futuro mais sustentável.
""")

        elif r["nivel"] == "Consumo moderado":

            st.markdown("""
### Estimativa de Redução
Se algumas mudanças forem aplicadas, sua residência pode reduzir até **15% a 30% do consumo de energia.**

### Dicas Personalizadas
Seus hábitos de consumo já são bastante eficientes! Continue assim.

• Fique atento ao **selo de eficiência energética** ao comprar novos eletrodomésticos.

### Energia inteligente, planeta sustentável
Quando reduzimos o desperdício de energia em casa, não economizamos apenas dinheiro.  
Também ajudamos a reduzir a necessidade de geração de energia, diminuindo impactos ambientais e contribuindo para um futuro mais sustentável.
""")

        else:

            st.markdown("""
### Estimativa de Redução
Se algumas mudanças forem aplicadas, sua residência pode reduzir até **25% a 40% do consumo de energia.**

### Dicas Personalizadas

• Reduzir o banho para **8 minutos** pode diminuir significativamente o consumo do chuveiro elétrico.

• Usar o chuveiro na posição **verão** sempre que possível reduz o consumo de energia.

• Apagar as luzes ao sair dos ambientes é um hábito simples que economiza bastante energia.

• Geladeiras antigas consomem muito mais energia. Considere trocar por um modelo com **selo A de eficiência**.

• Evitar aparelhos em **stand-by** pode economizar até **12% da energia residencial**.

• Acumular roupas para usar a **máquina de lavar menos vezes por semana** ajuda a economizar energia e água.
""")

    if st.button("Sair"):
        st.session_state.page = "home"
        st.rerun()

# =========================
# ADMIN
# =========================

elif st.session_state.page == "admin":

    st.title("Painel Administrador")

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    usuarios = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM diagnosticos")
    diagnosticos = cursor.fetchone()[0]

    cursor.execute("SELECT acessos, formularios FROM estatisticas")
    estat = cursor.fetchone()
    acessos = estat[0] if estat else 0
    formularios = estat[1] if estat else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Usuários cadastrados", usuarios)
    col2.metric("Diagnósticos realizados", diagnosticos)
    col3.metric("Acessos", acessos)
    col4.metric("Formulários enviados", formularios)

    st.bar_chart({
        "Usuários": [usuarios],
        "Diagnósticos": [diagnosticos]
    })

    st.markdown("---")
    st.subheader("Consumo geral dos usuários")

    cursor.execute("""
    SELECT usuario, pessoas, eletrodomesticos, lampadas, status, valor_conta, economia
    FROM diagnosticos
    """)

    dados = cursor.fetchall()

    df = pd.DataFrame(dados, columns=[
        "Usuario",
        "Quantidade de pessoas",
        "Eletrodomésticos e aparelhos",
        "Lâmpadas e chuveiro",
        "Status de consumo",
        "Valor da conta",
        "Economia"
    ])

    if not df.empty:

        st.subheader("Distribuição do consumo")

        status = df["Status de consumo"].value_counts()

        status_df = status.reset_index()
        status_df.columns = ["Categoria", "Quantidade"]

        grafico_status = alt.Chart(status_df).mark_bar(size=85).encode(
            x=alt.X(
                "Categoria:N",
                title="",
                sort=["Baixo consumo", "Consumo moderado", "Alto consumo"],
                axis=alt.Axis(
                    labelAngle=0,
                    labelFontSize=17,
                    titleFontSize=18,
                    labelPadding=14,
                    labelLimit=260
                )
            ),
            y=alt.Y(
                "Quantidade:Q",
                title="Quantidade",
                axis=alt.Axis(labelFontSize=15, titleFontSize=18)
            ),
            color=alt.Color(
                "Categoria:N",
                scale=alt.Scale(
                    domain=["Baixo consumo", "Consumo moderado", "Alto consumo"],
                    range=["#81C784", "#4CAF50", "#1B5E20"]
                ),
                legend=None
            )
        ).properties(
            height=420
        ).configure_view(
            strokeWidth=0
        )

        st.altair_chart(grafico_status, use_container_width=True)

        grafico_consumo = pd.DataFrame({
            "Categoria": ["Eletrodomésticos", "Lâmpadas e chuveiro"],
            "Consumo": [
                df["Eletrodomésticos e aparelhos"].sum(),
                df["Lâmpadas e chuveiro"].sum()
            ]
        })

        st.subheader("Consumo por categoria")

        grafico_cat = alt.Chart(grafico_consumo).mark_bar(size=95).encode(
            x=alt.X(
                "Categoria:N",
                title="",
                sort=["Eletrodomésticos", "Lâmpadas e chuveiro"],
                axis=alt.Axis(
                    labelAngle=0,
                    labelFontSize=17,
                    titleFontSize=18,
                    labelPadding=14,
                    labelLimit=260
                )
            ),
            y=alt.Y(
                "Consumo:Q",
                title="Consumo",
                axis=alt.Axis(labelFontSize=15, titleFontSize=18)
            ),
            color=alt.Color(
                "Categoria:N",
                scale=alt.Scale(
                    domain=["Eletrodomésticos", "Lâmpadas e chuveiro"],
                    range=["#1B5E20", "#81C784"]
                ),
                legend=None
            )
        ).properties(
            height=420
        ).configure_view(
            strokeWidth=0
        )

        st.altair_chart(grafico_cat, use_container_width=True)

        st.markdown("""
Este gráfico apresenta os resultados das respostas dos participantes do formulário, 
mostrando suas percepções e indicando o potencial de economia que pode ser alcançado 
ao adotar novos hábitos a partir das dicas sugeridas.
""")

        st.markdown("---")
        st.subheader("Relação de consumo após preenchimento do formulário")
        st.dataframe(df, use_container_width=True)

    else:
        st.info("Ainda não há diagnósticos salvos para exibir no painel.")

    if st.button("Sair"):
        st.session_state.page = "home"
        st.rerun()