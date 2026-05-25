from tkinter import *
from tkinter import messagebox

from datetime import datetime, timedelta

import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from dados import *

# ================= CORES =================

verde = "#22c55e"

vermelho = "#ef4444"

amarelo = "#facc15"

azul = "#3b82f6"

laranja = "#f97316"

branco = "#ffffff"

# ================= LISTA =================

transacoes = []

# ================= CARREGAR =================

def carregar_transacoes():

    transacoes.clear()

    cursor.execute("""
    SELECT tipo, valor, descricao, data
    FROM transacoes
    ORDER BY data DESC
    """)

    dados = cursor.fetchall()

    for t in dados:

        transacoes.append({

            "tipo": t[0],

            "valor": t[1],

            "desc": t[2],

            "data": datetime.strptime(
                t[3],
                "%Y-%m-%d %H:%M:%S"
            )
        })

# ================= TELAS =================

def mostrar_cadastro():

    frame_login.pack_forget()

    frame_dashboard.pack_forget()

    frame_cadastro.pack(expand=True)

def mostrar_login():

    frame_dashboard.pack_forget()

    frame_cadastro.pack_forget()

    frame_login.pack(expand=True)

    msg_login.config(text="")

def mostrar_dashboard(nome):

    frame_login.pack_forget()

    frame_cadastro.pack_forget()

    lbl_boas_vindas.config(
        text=f"👤 Usuário: {nome}"
    )

    carregar_transacoes()

    atualizar_interface()

    frame_dashboard.pack(
        fill=BOTH,
        expand=True
    )

# ================= CADASTRO =================

def cadastrar():

    nome = entry_nome.get()

    email = entry_email_cad.get()

    senha = entry_senha_cad.get()

    if not nome or not email or not senha:

        msg_cadastro.config(
            text="❌ Preencha todos os campos",
            fg=vermelho
        )

        return

    try:

        cursor.execute("""
        INSERT INTO usuarios(nome,email,senha)
        VALUES(?,?,?)
        """, (nome, email, senha))

        conexao.commit()

        msg_cadastro.config(
            text="✔ Cadastro realizado",
            fg=verde
        )

    except:

        msg_cadastro.config(
            text="❌ Email já cadastrado",
            fg=vermelho
        )

# ================= LOGIN =================

def login():

    email = entry_email.get()

    senha = entry_senha.get()

    cursor.execute("""
    SELECT nome
    FROM usuarios
    WHERE email=? AND senha=?
    """, (email, senha))

    usuario = cursor.fetchone()

    if usuario:

        mostrar_dashboard(usuario[0])

    else:

        msg_login.config(
            text="❌ Email ou senha incorretos",
            fg=vermelho
        )

# ================= EXCLUIR CONTA =================

def excluir_conta():

    email = entry_email.get()

    senha = entry_senha.get()

    if not email or not senha:

        messagebox.showwarning(
            "Aviso",
            "Digite email e senha"
        )

        return

    cursor.execute("""
    SELECT id
    FROM usuarios
    WHERE email=? AND senha=?
    """, (email, senha))

    usuario = cursor.fetchone()

    if usuario:

        resposta = messagebox.askyesno(
            "Confirmar",
            "Deseja realmente excluir a conta?"
        )

        if resposta:

            cursor.execute("""
            DELETE FROM usuarios
            WHERE email=? AND senha=?
            """, (email, senha))

            conexao.commit()

            messagebox.showinfo(
                "Sucesso",
                "Conta excluída com sucesso!"
            )

    else:

        messagebox.showerror(
            "Erro",
            "Email ou senha incorretos"
        )

# ================= ADICIONAR =================

def adicionar_transacao(tipo):

    try:

        valor = float(entry_valor.get())

        descricao = entry_desc.get()

        if not descricao:

            raise ValueError

        data_atual = datetime.now()

        cursor.execute("""
        INSERT INTO transacoes(tipo,valor,descricao,data)
        VALUES(?,?,?,?)
        """, (
            tipo,
            valor,
            descricao,
            data_atual.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ))

        conexao.commit()

        carregar_transacoes()

        entry_desc.delete(0, END)

        entry_valor.delete(0, END)

        atualizar_interface()

    except:

        messagebox.showerror(
            "Erro",
            "Digite valores válidos"
        )

# ================= EXCLUIR =================

def excluir_selecionado():

    try:

        indice = lista_transacoes.curselection()[0]

        cursor.execute("""
        SELECT id
        FROM transacoes
        ORDER BY data DESC
        LIMIT 1 OFFSET ?
        """, (indice,))

        resultado = cursor.fetchone()

        if resultado:

            cursor.execute("""
            DELETE FROM transacoes
            WHERE id=?
            """, (resultado[0],))

            conexao.commit()

        carregar_transacoes()

        atualizar_interface()

    except:

        messagebox.showwarning(
            "Aviso",
            "Selecione uma transação"
        )

# ================= INTERFACE =================

def atualizar_interface():

    lista_transacoes.delete(0, END)

    receitas = 0

    despesas = 0

    for t in transacoes:

        if t["tipo"] == "Receita":

            receitas += t["valor"]

            emoji = "💰"

        else:

            despesas += t["valor"]

            emoji = "💸"
e
        data_formatada = t["data"].strftime(
            "%d/%m/%Y %H:%M"
        )

        texto = (
            f"{data_formatada} | "
            f"{emoji} {t['desc']} | "
            f"R$ {t['valor']:.2f}"
        )

        lista_transacoes.insert(END, texto)

    saldo = receitas - despesas

    lbl_saldo.config(
        text=f"Saldo: R$ {saldo:.2f}",
        fg=verde if saldo >= 0 else vermelho
    )
