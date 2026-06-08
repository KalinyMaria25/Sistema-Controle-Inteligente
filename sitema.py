from tkinter import *
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import sqlite3
import re

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

# ================= VALIDAÇÃO DE EMAIL =================

def email_valido(email):

    padrao = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'

    return re.match(padrao, email)

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

    nome = entry_nome.get().strip()
    email = entry_email_cad.get().strip().lower()
    senha = entry_senha_cad.get()

    if not nome or not email or not senha:

        msg_cadastro.config(
            text="❌ Preencha todos os campos",
            fg=vermelho
        )

        return

    if not email_valido(email):

        msg_cadastro.config(
            text="❌ Digite um Gmail válido",
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

        entry_nome.delete(0, END)
        entry_email_cad.delete(0, END)
        entry_senha_cad.delete(0, END)

    except:

        msg_cadastro.config(
            text="❌ Email já cadastrado",
            fg=vermelho
        )
# ================= LOGIN =================

def login():

    email = entry_email.get().strip().lower()
    senha = entry_senha.get()

    if not email_valido(email):

        msg_login.config(
            text="❌ Digite um Gmail válido",
            fg=vermelho
        )

        return

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

# ================= ESTATÍSTICAS =================

def atualizar_estatisticas():

    receitas = [
        t for t in transacoes
        if t["tipo"] == "Receita"
    ]

    despesas = [
        t for t in transacoes
        if t["tipo"] == "Despesa"
    ]

    maior_receita = max(
        [t["valor"] for t in receitas],
        default=0
    )

    menor_receita = min(
        [t["valor"] for t in receitas],
        default=0
    )

    maior_despesa = max(
        [t["valor"] for t in despesas],
        default=0
    )

    menor_despesa = min(
        [t["valor"] for t in despesas],
        default=0
    )

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

    if despesas:

        despesa_maior = max(
            despesas,
            key=lambda x: x["valor"]
        )

        mensagem = (
            
    f"⚠ AVISO!!!! Maior gasto: {despesa_maior['desc']} "
    f"(R$ {despesa_maior['valor']:.2f}) | "
    f"💡 Economize hoje para conquistar seus objetivos amanhã!"

        )
        lbl_alerta_gastos.config(
            text=mensagem,
            fg=amarelo
        )

    else:

        lbl_alerta_gastos.config(
            text="🎉 Parabéns! Nenhuma despesa registrada até o momento.",
            fg=verde
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
    if not transacoes:
        messagebox.showwarning("Aviso", "Sem dados para gerar o gráfico.")
        return

    # Separar receitas e despesas
    receitas = [t for t in transacoes if t["tipo"] == "Receita"]
    despesas = [t for t in transacoes if t["tipo"] == "Despesa"]

    total_receitas = sum(t["valor"] for t in receitas)
    total_despesas = sum(t["valor"] for t in despesas)
    total_geral = total_receitas + total_despesas

    # Obter estatísticas para o texto descritivo
    maior_receita = max([t["valor"] for t in receitas]) if receitas else 0
    maior_despesa = max([t["valor"] for t in despesas]) if despesas else 0

    # Agrupar dados para o gráfico
    valores_grafico = []
    labels_grafico = []
    cores_grafico = []

    if total_receitas > 0:
        valores_grafico.append(total_receitas)
        labels_grafico.append(f"Receitas: R$ {total_receitas:.2f}")
        cores_grafico.append(verde)

    # Agrupar despesas repetidas
    despesas_agrupadas = {}
    for d in despesas:
        despesas_agrupadas[d["desc"]] = despesas_agrupadas.get(d["desc"], 0) + d["valor"]

    for desc, valor in despesas_agrupadas.items():
        valores_grafico.append(valor)
        labels_grafico.append(f"{desc}: R$ {valor:.2f}")
        cores_grafico.append(vermelho)

    # Definir mensagem emotiva/motivacional
    if total_receitas > total_despesas:
        mensagem_emotiva = (
            "Incrível! Você está cuidando muito bem do seu dinheiro.\n"
            "Ver suas receitas maiores que as despesas traz uma paz de espírito enorme, não é?\n"
            "Continue firme investindo no seu futuro e colhendo bons frutos! 🌱✨"
        )
        cor_msg = verde
    elif total_despesas > total_receitas:
        mensagem_emotiva = (
            "❤️ Não desanime! Olhar para os gastos pode ser difícil, mas você é forte.\n"
            "Cada pequena escolha de economia hoje aproxima você dos seus maiores sonhos.\n"
            "Respire fundo, reorganize os passos e assuma o controle da sua história! 🚀💪"
        )
        cor_msg = laranja
    else:
        mensagem_emotiva = (
            "⚖️ Tudo equilibrado por aqui! O orçamento está empatado.\n"
            "Que tal o desafio de tentar poupar um pouquinho a mais no próximo mês?\n"
            "Você tem total capacidade de fazer seu dinheiro render mais! 🏆"
        )
        cor_msg = amarelo

    # Criar a Janela do Gráfico
    top = Toplevel()
    top.title("📊 Gráfico Financeiro Detalhado")
    top.geometry("850x850") # Aumentamos um pouco o tamanho da janela para as porcentagens externas
    top.config(bg="#111827")

    Label(
        top,
        text="📊 DISTRIBUIÇÃO DOS SEUS GASTOS",
        bg="#111827",
        fg=amarelo,
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    # Gerar Gráfico com Matplotlib
    fig, ax = plt.subplots(figsize=(7, 4))
    fig.patch.set_facecolor("#111827")
    ax.set_facecolor("#111827")

    if valores_grafico:
        # Criamos o gráfico jogando os valores para fora e rotacionando-os
        wedges, texts, autotexts = ax.pie(
            valores_grafico,
            labels=None, 
            colors=cores_grafico,
            autopct="%1.1f%%",
            pctdistance=1.2,            # 1.2 joga as porcentagens para FORA do círculo da pizza
            startangle=140,
            rotatelabels=True,          # Gira os textos seguindo a curva do gráfico para não embolar
            textprops={"color": "white", "fontsize": 9, "fontweight": "bold"}
        )
        
        # Ajusta as linhas guias das porcentagens para ficarem legíveis no fundo escuro
        for autotext in autotexts:
            autotext.set_color("#cbd5e1") # Tom cinza claro super elegante e legível
        
        # Cria a legenda lateral de apoio
        legenda = ax.legend(
            wedges, 
            labels_grafico,
            title="Categorias",
            title_fontsize=11,
            loc="center left",
            bbox_to_anchor=(1.3, 0, 0.5, 1), # Afastamos um pouco a legenda para dar espaço aos números externos
            facecolor="#1f2937",
            edgecolor="#374151",
            labelcolor="white"
        )
        
        legenda.get_title().set_color(amarelo)

    ax.set_title("Divisão de Receitas vs Despesas", color="white", fontsize=12, pad=10)

    # O subplots_adjust cria uma margem de respiro perfeita para os números externos não sumirem nas bordas
    plt.subplots_adjust(left=0.05, right=0.65, top=0.85, bottom=0.15)

    canvas = FigureCanvasTkAgg(fig, master=top)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=5)

    # Painel de Informações (Maiores Valores)
    frame_info = Frame(top, bg="#1f2937", bd=2, relief="ridge")
    frame_info.pack(fill=X, padx=30, pady=10)

    Label(
        frame_info,
        text=f"📥 Maior Receita Única: R$ {maior_receita:.2f}  |  📤 Maior Despesa Única: R$ {maior_despesa:.2f}",
        bg="#1f2937",
        fg=branco,
        font=("Arial", 11, "bold")
    ).pack(pady=10)

    Label(
        frame_info,
        text=f"📌 Saldo Geral: R$ {(total_receitas - total_despesas):.2f}",
        bg="#1f2937",
        fg="#38bdf8",
        font=("Arial", 13, "bold")
    ).pack(pady=5)

    # Mensagem Emotiva/Motivacional no rodapé
    lbl_msg_emotiva = Label(
        top,
        text=mensagem_emotiva,
        bg="#111827",
        fg=cor_msg,
        font=("Arial", 12, "italic", "bold"),
        justify="center",
        wraplength=700
    )
    lbl_msg_emotiva.pack(pady=15)
# ================= JANELA =================

janela = Tk()

janela.title("Sistema Financeiro")

janela.geometry("1110x950")

janela.config(bg=preto)

# ================= LOGIN =================

frame_login = Frame(
    janela,
    bg=preto
)

frame_login.pack(expand=True)

Label(
    frame_login,
    text="💰 Controle Inteligente",
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
lbl_alerta_gastos = Label(
    frame_stats,
    text="",
    bg="#1e1e1e",
    fg=amarelo,
    font=("Arial",11,"bold"),
    wraplength=900,
    justify="center"
)

lbl_alerta_gastos.pack(pady=8)

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
