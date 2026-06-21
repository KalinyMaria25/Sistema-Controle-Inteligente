from tkinter import * 
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import sqlite3

# ================= BANCO =================

conexao = sqlite3.connect("financeiro.db")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    email TEXT UNIQUE,
    senha TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transacoes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    valor REAL,
    descricao TEXT,
    data TEXT
)
""")

conexao.commit()

# ================= CORES =================

preto = "#121212"
branco = "#ffffff"
verde = "#22c55e"
vermelho = "#ef4444"
amarelo = "#facc15"
azul = "#3b82f6"
cinza = "#1f2937"
laranja = "#f97316"
roxo = "#8b5cf6"

# ================= LISTAS =================

transacoes = []

# ================= FUNÇÕES =================

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

            entry_email.delete(0, END)
            entry_senha.delete(0, END)

    else:

        messagebox.showerror(
            "Erro",
            "Email ou senha incorretos"
        )

# ================= ADICIONAR TRANSAÇÃO =================

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

        transacoes.insert(0, {
            "tipo": tipo,
            "valor": valor,
            "desc": descricao,
            "data": data_atual
        })

        entry_desc.delete(0, END)
        entry_valor.delete(0, END)

        atualizar_interface()

    except:

        messagebox.showerror(
            "Erro",
            "Digite valores válidos"
        )

# ================= EXCLUIR TRANSAÇÃO =================

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
# ================= FUNÇÃO ALERTA =================
def alerta_usuario(receitas, despesas):

    if receitas == 0 and despesas > 0:
        return (
            "🚨 ALERTA CRÍTICO\n\n"
            "Você só possui despesas e nenhuma receita.\n"
            "Situação de risco financeiro!"
        ), vermelho

    percentual = (despesas / receitas) * 100 if receitas > 0 else 0

    if receitas > 0 and percentual >= 80:
        return (
            "⚠ CUIDADO!\n\n"
            "Suas despesas estão muito altas.\n"
            "Você está gastando a maior parte da sua renda."
        ), laranja

    elif receitas > despesas:
        return (
            "⚖ FINANÇAS ESTÁVEIS\n\n"
            "Você está com bom controle financeiro."
        ), verde

    elif receitas > despesas * 2:
        return (
            "💰 EXCELENTE!\n\n"
            "Sua receita é muito maior que suas despesas."
        ), azul

    else:
        return (
            "🚨 ATENÇÃO!\n\n"
            "Suas despesas estão maiores que suas receitas."
        ), vermelho
# ================= ESTATÍSTICAS =================

def atualizar_estatisticas():

    receitas = [
        t["valor"]
        for t in transacoes
        if t["tipo"] == "Receita"
    ]

    despesas = [
        t["valor"]
        for t in transacoes
        if t["tipo"] == "Despesa"
    ]

    maior_receita = max(receitas) if receitas else 0
    menor_receita = min(receitas) if receitas else 0

    maior_despesa = max(despesas) if despesas else 0
    menor_despesa = min(despesas) if despesas else 0

    lbl_maior_receita.config(
        text=f"💰 Maior Receita: R$ {maior_receita:.2f}"
    )

    lbl_menor_receita.config(
        text=f"💵 Menor Receita: R$ {menor_receita:.2f}"
    )

    lbl_maior_despesa.config(
        text=f"💸 Maior Despesa: R$ {maior_despesa:.2f}"
    )

    lbl_menor_despesa.config(
        text=f"🧾 Menor Despesa: R$ {menor_despesa:.2f}"
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
    msg, cor = alerta_usuario(receitas, despesas)
    lbl_alerta.config(text=msg, fg=cor)

    atualizar_estatisticas()

# ================= RELATÓRIOS =================

def exibir_relatorios():

    janela_rel = Toplevel()

    janela_rel.title("📊 Relatórios Financeiros")

    janela_rel.geometry("950x750")

    janela_rel.config(bg="#0f172a")

    topo = Frame(
        janela_rel,
        bg="#111827",
        height=90
    )

    topo.pack(fill=X)

    Label(
        topo,
        text="📊 RELATÓRIOS FINANCEIROS",
        bg="#111827",
        fg=amarelo,
        font=("Arial",24,"bold")
    ).pack(pady=25)

    canvas = Canvas(
        janela_rel,
        bg="#0f172a",
        highlightthickness=0
    )

    scrollbar = Scrollbar(
        janela_rel,
        orient="vertical",
        command=canvas.yview
    )

    frame_scroll = Frame(
        canvas,
        bg="#0f172a"
    )

    frame_scroll.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window(
        (0,0),
        window=frame_scroll,
        anchor="nw"
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    canvas.pack(
        side=LEFT,
        fill=BOTH,
        expand=True
    )

    scrollbar.pack(
        side=RIGHT,
        fill=Y
    )

    hoje = datetime.now()

    periodos = [
        ("📅 RELATÓRIO DIÁRIO", 1, verde),
        ("📆 RELATÓRIO SEMANAL", 7, azul),
        ("🗓 RELATÓRIO MENSAL", 30, laranja),
        ("📁 RELATÓRIO ANUAL", 365, vermelho)
    ]

    for titulo, dias, cor in periodos:

        frame_card = Frame(
            frame_scroll,
            bg="#111827",
            bd=3,
            relief="ridge"
        )

        frame_card.pack(
            fill=X,
            padx=20,
            pady=15
        )

        Label(
            frame_card,
            text=titulo,
            bg=cor,
            fg=branco,
            font=("Arial",16,"bold"),
            pady=10
        ).pack(fill=X)

        data_limite = hoje - timedelta(days=dias)

        lista = [
            t for t in transacoes
            if t["data"] >= data_limite
        ]

        if not lista:

            Label(
                frame_card,
                text="Nenhuma movimentação encontrada",
                bg="#111827",
                fg="#9ca3af",
                font=("Arial",12,"italic"),
                pady=20
            ).pack()

            continue

        receitas = 0
        despesas = 0

        receitas_lista = []
        despesas_lista = []

        for t in lista:

            cor_item = (
                verde
                if t["tipo"] == "Receita"
                else vermelho
            )

            emoji = (
                "💰"
                if t["tipo"] == "Receita"
                else "💸"
            )

            linha = Frame(
                frame_card,
                bg="#1f2937"
            )

            linha.pack(
                fill=X,
                padx=10,
                pady=4
            )

            Label(
                linha,
                text=t["data"].strftime("%d/%m/%Y %H:%M"),
                bg="#1f2937",
                fg="#cbd5e1",
                width=18,
                anchor="w",
                font=("Courier",10,"bold")
            ).pack(side=LEFT,padx=5)

            Label(
                linha,
                text=emoji,
                bg="#1f2937",
                fg=cor_item,
                font=("Arial",12)
            ).pack(side=LEFT)

            Label(
                linha,
                text=t["desc"],
                bg="#1f2937",
                fg=branco,
                width=30,
                anchor="w",
                font=("Arial",11,"bold")
            ).pack(side=LEFT,padx=10)

            Label(
                linha,
                text=f"R$ {t['valor']:.2f}",
                bg="#1f2937",
                fg=cor_item,
                font=("Arial",11,"bold")
            ).pack(side=RIGHT,padx=10)

            if t["tipo"] == "Receita":

                receitas += t["valor"]
                receitas_lista.append(t["valor"])

            else:

                despesas += t["valor"]
                despesas_lista.append(t["valor"])

        saldo = receitas - despesas

        frame_resumo = Frame(
            frame_card,
            bg="#0b1220"
        )

        frame_resumo.pack(
            fill=X,
            pady=10
        )

        Label(
            frame_resumo,
            text=f"💰 TOTAL RECEITAS: R$ {receitas:.2f}",
            bg="#0b1220",
            fg=verde,
            font=("Arial",12,"bold")
        ).pack(pady=4)

        Label(
            frame_resumo,
            text=f"💸 TOTAL DESPESAS: R$ {despesas:.2f}",
            bg="#0b1220",
            fg=vermelho,
            font=("Arial",12,"bold")
        ).pack(pady=4)

        Label(
            frame_resumo,
            text=f"📌 SALDO: R$ {saldo:.2f}",
            bg="#0b1220",
            fg="#38bdf8",
            font=("Arial",15,"bold")
        ).pack(pady=6)

# ================= GRÁFICO =================
def gerar_grafico():

    receitas = sum(
        t["valor"]
        for t in transacoes
        if t["tipo"] == "Receita"
    )

    despesas = sum(
        t["valor"]
        for t in transacoes
        if t["tipo"] == "Despesa"
    )

    if receitas == 0 and despesas == 0:
        messagebox.showwarning("Aviso", "Sem dados para gráfico")
        return

    # 🔥 evita gráfico antigo
    plt.close("all")

    # ===== CASO SEM RECEITA =====
    if receitas == 0 and despesas > 0:

        mensagem = (
            "🚨 ALERTA CRÍTICO!\n\n"
            "Você não possui receitas cadastradas\n"
            "mas já possui despesas.\n"
            "Isso gera prejuízo automático."
        )
        cor_msg = vermelho

    # ===== ALERTA 80% =====
    elif receitas > 0 and despesas >= receitas * 0.8 and despesas < receitas:

        mensagem = (
            "⚠ ALERTA FINANCEIRO\n\n"
            "Suas despesas já consomem mais de 80% da sua receita."
        )
        cor_msg = laranja

    # ===== RECEITA MAIOR =====
    elif receitas > despesas:

        mensagem = (
            "✅ PARABÉNS!\n\n"
            "Sua receita está maior que suas despesas."
        )
        cor_msg = verde

    # ===== EQUILÍBRIO =====
    elif receitas == despesas:

        mensagem = (
            "⚖ EQUILÍBRIO FINANCEIRO\n\n"
            "Receitas e despesas estão iguais."
        )
        cor_msg = amarelo

    # ===== DESPESA MAIOR =====
    else:

        mensagem = (
            "🚨 ATENÇÃO!\n\n"
            "Suas despesas são maiores que suas receitas."
        )
        cor_msg = vermelho

    # ===== JANELA DO GRÁFICO =====
    top = Toplevel()
    top.title("📊 Gráfico Financeiro")
    top.geometry("650x700")
    top.config(bg="#111827")

    # ===== GRÁFICO =====
    fig, ax = plt.subplots(figsize=(5, 5))
    fig.patch.set_facecolor("#111827")
    ax.set_facecolor("#111827")

    ax.pie(
        [receitas, despesas],
        labels=["Receitas", "Despesas"],
        colors=[verde, vermelho],
        autopct="%1.1f%%",
        textprops={"color": "white"}
    )

    ax.set_title("Controle Financeiro", color="white")

    canvas = FigureCanvasTkAgg(fig, master=top)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

    plt.close(fig)

    # ===== MENSAGEM ABAIXO DO GRÁFICO =====
    frame_msg = Frame(top, bg="#1f2937", bd=2, relief="ridge")
    frame_msg.pack(fill=X, padx=20, pady=15)

    Label(
        frame_msg,
        text=mensagem,
        bg="#1f2937",
        fg=cor_msg,
        font=("Arial", 13, "bold"),
        justify="center",
        padx=15,
        pady=15
    ).pack(fill=X)

    # ===== JANELA DO GRÁFICO =====
    top = Toplevel()
    top.title("📊 Gráfico Financeiro")
    top.geometry("650x700")
    top.config(bg="#111827")

    # ===== GRÁFICO =====
    fig, ax = plt.subplots(figsize=(5, 5))
    fig.patch.set_facecolor("#111827")
    ax.set_facecolor("#111827")

    ax.pie(
        [receitas, despesas],
        labels=["Receitas", "Despesas"],
        colors=[verde, vermelho],
        autopct="%1.1f%%",
        textprops={"color": "white"}
    )

    ax.set_title("Controle Financeiro", color="white")

    canvas = FigureCanvasTkAgg(fig, master=top)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

    # FECHA FIGURA (IMPORTANTE)
    plt.close(fig)

    # ===== MENSAGEM NO GRÁFICO =====
    frame_msg = Frame(top, bg="#1f2937", bd=2, relief="ridge")
    frame_msg.pack(fill=X, padx=20, pady=15)

    Label(
        frame_msg,
        text=mensagem,
        bg="#1f2937",
        fg=cor_msg,
        font=("Arial", 13, "bold"),
        justify="center",
        padx=15,
        pady=15
    ).pack(fill=X)
    top = Toplevel()

    top.title("📊 Gráfico Financeiro")

    top.geometry("650x700")

    top.config(bg="#111827")

    Label(
        top,
        text="📊 RESUMO FINANCEIRO",
        bg="#111827",
        fg=amarelo,
        font=("Arial",22,"bold")
    ).pack(pady=20)

    fig, ax = plt.subplots(figsize=(5,5))

    fig.patch.set_facecolor("#111827")

    ax.set_facecolor("#111827")

    ax.pie(
        [receitas, despesas],
        labels=["Receitas", "Despesas"],
        colors=[verde, vermelho],
        autopct="%1.1f%%",
        textprops={
            "color":"white",
            "fontsize":12,
            "fontweight":"bold"
        }
    )

    ax.set_title(
        "Controle Financeiro",
        color="white",
        fontsize=16
    )

    canvas = FigureCanvasTkAgg(
        fig,
        master=top
    )

    canvas.draw()

    canvas.get_tk_widget().pack(
        pady=10
    )

    saldo = receitas - despesas

    frame_info = Frame(
        top,
        bg="#1f2937",
        bd=3,
        relief="ridge"
    )

    frame_info.pack(
        fill=X,
        padx=25,
        pady=20
    )

    Label(
        frame_info,
        text=f"💰 Receitas: R$ {receitas:.2f}",
        bg="#1f2937",
        fg=verde,
        font=("Arial",14,"bold")
    ).pack(pady=8)

    Label(
        frame_info,
        text=f"💸 Despesas: R$ {despesas:.2f}",
        bg="#1f2937",
        fg=vermelho,
        font=("Arial",14,"bold")
    ).pack(pady=8)

    Label(
        frame_info,
        text=f"📌 Saldo: R$ {saldo:.2f}",
        bg="#1f2937",
        fg="#38bdf8",
        font=("Arial",16,"bold")
    ).pack(pady=10)

    Label(
        top,
        text=mensagem,
        bg="#111827",
        fg=cor_msg,
        font=("Arial",14,"bold"),
        justify="center"
    ).pack(pady=15)

# ================= JANELA =================

janela = Tk()

janela.title("Sistema Financeiro")

janela.geometry("1100x750")

janela.config(bg=preto)

# ================= LOGIN =================

frame_login = Frame(
    janela,
    bg=preto
)

frame_login.pack(expand=True)

Label(
    frame_login,
    text="💰 Controle Financeiro",
    bg=preto,
    fg=verde,
    font=("Arial",24,"bold")
).pack(pady=20)

Label(
    frame_login,
    text="Email",
    bg=preto,
    fg=branco
).pack()

entry_email = Entry(
    frame_login,
    width=40
)

entry_email.pack(pady=5)

Label(
    frame_login,
    text="Senha",
    bg=preto,
    fg=branco
).pack()

entry_senha = Entry(
    frame_login,
    width=40,
    show="*"
)

entry_senha.pack(pady=5)

Button(
    frame_login,
    text="Entrar",
    bg=verde,
    fg=preto,
    width=25,
    command=login
).pack(pady=10)

Button(
    frame_login,
    text="Criar Conta",
    bg=amarelo,
    fg=preto,
    width=25,
    command=mostrar_cadastro
).pack(pady=5)

Button(
    frame_login,
    text="Excluir Conta",
    bg=vermelho,
    fg=branco,
    width=25,
    command=excluir_conta
).pack(pady=5)

msg_login = Label(
    frame_login,
    text="",
    bg=preto
)

msg_login.pack()

# ================= CADASTRO =================

frame_cadastro = Frame(
    janela,
    bg=preto
)

Label(
    frame_cadastro,
    text="Criar Conta",
    bg=preto,
    fg=amarelo,
    font=("Arial",22,"bold")
).pack(pady=20)

Label(
    frame_cadastro,
    text="Nome",
    bg=preto,
    fg=branco
).pack()

entry_nome = Entry(
    frame_cadastro,
    width=40
)

entry_nome.pack()

Label(
    frame_cadastro,
    text="Email",
    bg=preto,
    fg=branco
).pack()

entry_email_cad = Entry(
    frame_cadastro,
    width=40
)

entry_email_cad.pack()

Label(
    frame_cadastro,
    text="Senha",
    bg=preto,
    fg=branco
).pack()

entry_senha_cad = Entry(
    frame_cadastro,
    width=40,
    show="*"
)

entry_senha_cad.pack()

Button(
    frame_cadastro,
    text="Salvar Cadastro",
    bg=amarelo,
    fg=preto,
    width=25,
    command=cadastrar
).pack(pady=10)

Button(
    frame_cadastro,
    text="Voltar",
    width=25,
    command=mostrar_login
).pack()

msg_cadastro = Label(
    frame_cadastro,
    text="",
    bg=preto
)

msg_cadastro.pack()

# ================= DASHBOARD =================

frame_dashboard = Frame(
    janela,
    bg=preto
)

lbl_boas_vindas = Label(
    frame_dashboard,
    text="",
    bg=preto,
    fg=branco,
    font=("Arial",14)
)

lbl_boas_vindas.pack(pady=10)

lbl_saldo = Label(
    frame_dashboard,
    text="Saldo: R$ 0.00",
    bg=preto,
    fg=verde,
    font=("Arial",24,"bold")
)

lbl_saldo.pack()

# INPUTS

frame_inputs = Frame(
    frame_dashboard,
    bg=preto
)

frame_inputs.pack(pady=10)

Label(
    frame_inputs,
    text="Descrição",
    bg=preto,
    fg=branco
).grid(row=0,column=0)

entry_desc = Entry(
    frame_inputs,
    width=30
)

entry_desc.grid(row=0,column=1,padx=10)

Label(
    frame_inputs,
    text="Valor",
    bg=preto,
    fg=branco
).grid(row=0,column=2)

entry_valor = Entry(
    frame_inputs,
    width=15
)

entry_valor.grid(row=0,column=3,padx=10)

# LISTA
lbl_alerta = Label(
    frame_dashboard,
    text="",
    bg=preto,
    fg=verde,
    font=("Arial", 12, "bold"),
    justify="center",
    wraplength=800
)

lbl_alerta.pack(pady=10)

lista_transacoes = Listbox(
    frame_dashboard,
    width=110,
    height=15,
    bg=cinza,
    fg=branco,
    font=("Courier",11)
)

lista_transacoes.pack(pady=10)

# ESTATÍSTICAS

frame_stats = Frame(
    frame_dashboard,
    bg="#1e1e1e",
    bd=2,
    relief="ridge"
)

frame_stats.pack(
    fill=X,
    padx=20,
    pady=10
)

lbl_maior_receita = Label(
    frame_stats,
    text="💰 Maior Receita: R$ 0.00",
    bg="#1e1e1e",
    fg=verde,
    font=("Arial",11,"bold")
)

lbl_maior_receita.pack(pady=3)

lbl_menor_receita = Label(
    frame_stats,
    text="💵 Menor Receita: R$ 0.00",
    bg="#1e1e1e",
    fg=verde,
    font=("Arial",11,"bold")
)

lbl_menor_receita.pack(pady=3)

lbl_maior_despesa = Label(
    frame_stats,
    text="💸 Maior Despesa: R$ 0.00",
    bg="#1e1e1e",
    fg=vermelho,
    font=("Arial",11,"bold")
)

lbl_maior_despesa.pack(pady=3)

lbl_menor_despesa = Label(
    frame_stats,
    text="🧾 Menor Despesa: R$ 0.00",
    bg="#1e1e1e",
    fg=vermelho,
    font=("Arial",11,"bold")
)

lbl_menor_despesa.pack(pady=3)

# BOTÕES

frame_botoes = Frame(
    frame_dashboard,
    bg=preto
)

frame_botoes.pack(pady=15)

Button(
    frame_botoes,
    text="💰 Receita",
    bg=verde,
    width=15,
    command=lambda: adicionar_transacao("Receita")
).grid(row=0,column=0,padx=5)

Button(
    frame_botoes,
    text="💸 Despesa",
    bg=vermelho,
    fg=branco,
    width=15,
    command=lambda: adicionar_transacao("Despesa")
).grid(row=0,column=1,padx=5)

Button(
    frame_botoes,
    text="🗑 Excluir",
    bg=laranja,
    fg=branco,
    width=15,
    command=excluir_selecionado
).grid(row=0,column=2,padx=5)

Button(
    frame_botoes,
    text="📊 Gráfico",
    bg=azul,
    fg=branco,
    width=15,
    command=gerar_grafico
).grid(row=0,column=3,padx=5)

Button(
    frame_botoes,
    text="📋 Relatórios",
    bg=roxo,
    fg=branco,
    width=15,
    command=exibir_relatorios
).grid(row=0,column=4,padx=5)

Button(
    frame_dashboard,
    text="Sair",
    bg=cinza,
    fg=branco,
    Recursos importantes da Programação Orientada a Objetos.
    Permitem criar sistemas mais organizados e reutilizáveis.
    Definem regras que outras classes devem seguir.
    width=20,
    command=mostrar_login
).pack(pady=20)

# ================= FECHAR =================

def fechar_sistema():

    conexao.close()
    janela.destroy()

janela.protocol(
    "WM_DELETE_WINDOW",
    fechar_sistema
)

janela.mainloop()
