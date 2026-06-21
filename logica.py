import sqlite3
from datetime import datetime

# ================= BANCO DE DADOS =================

conexao = sqlite3.connect("financeiro.db")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    email TEXT UNIQUE,
    senha TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    valor REAL,
    descricao TEXT,
    data TEXT
)
""")

conexao.commit()


# ================= TRANSACOES EM MEMORIA =================

transacoes = []


# ================= CARREGAR TRANSACOES =================

def carregar_transacoes():
    transacoes.clear()

    cursor.execute("""
        SELECT tipo, valor, descricao, data
        FROM transacoes
        ORDER BY data DESC
    """)

    for tipo, valor, descricao, data in cursor.fetchall():
        transacoes.append({
            "tipo": tipo,
            "valor": valor,
            "desc": descricao,
            "data": datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
        })


# ================= USUÁRIOS =================

def cadastrar_usuario(nome, email, senha):
    cursor.execute("""
        INSERT INTO usuarios (nome, email, senha)
        VALUES (?, ?, ?)
    """, (nome, email, senha))
    conexao.commit()


def login_usuario(email, senha):
    cursor.execute("""
        SELECT nome FROM usuarios
        WHERE email=? AND senha=?
    """, (email, senha))

    return cursor.fetchone()


def excluir_usuario(email, senha):
    cursor.execute("""
        DELETE FROM usuarios
        WHERE email=? AND senha=?
    """, (email, senha))
    conexao.commit()


# ================= TRANSAÇÕES =================

def adicionar_transacao(tipo, valor, descricao):
    data = datetime.now()

    cursor.execute("""
        INSERT INTO transacoes (tipo, valor, descricao, data)
        VALUES (?, ?, ?, ?)
    """, (tipo, valor, descricao, data.strftime("%Y-%m-%d %H:%M:%S")))

    conexao.commit()


def excluir_transacao(transacao_id):
    cursor.execute("""
        DELETE FROM transacoes
        WHERE id=?
    """, (transacao_id,))

    conexao.commit()


# ================= CÁLCULOS FINANCEIROS =================

def calcular_totais():
    receitas = sum(t["valor"] for t in transacoes if t["tipo"] == "Receita")
    despesas = sum(t["valor"] for t in transacoes if t["tipo"] == "Despesa")
    saldo = receitas - despesas

    return receitas, despesas, saldo


def estatisticas():
    receitas = [t["valor"] for t in transacoes if t["tipo"] == "Receita"]
    despesas = [t["valor"] for t in transacoes if t["tipo"] == "Despesa"]

    return {
        "maior_receita": max(receitas) if receitas else 0,
        "menor_receita": min(receitas) if receitas else 0,
        "maior_despesa": max(despesas) if despesas else 0,
        "menor_despesa": min(despesas) if despesas else 0
    }


# ================= ALERTAS FINANCEIROS =================

def alerta_financeiro(receitas, despesas):

    if receitas == 0 and despesas > 0:
        return "ALERTA CRÍTICO: sem receitas", "vermelho"

    if receitas > 0:
        percentual = (despesas / receitas) * 100

        if percentual >= 80:
            return "ALERTA: gastos acima de 80%", "laranja"

    if receitas > despesas:
        return "FINANÇAS OK", "verde"

    if receitas == despesas:
        return "EQUILÍBRIO FINANCEIRO", "amarelo"

    return "ATENÇÃO: déficit financeiro", "vermelho"
