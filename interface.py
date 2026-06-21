from tkinter import *

# ================= JANELA PRINCIPAL =================

janela = Tk()
janela.title("Sistema Financeiro")
janela.geometry("1100x750")
janela.config(bg="#121212")

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

# ================= LOGIN =================

frame_login = Frame(janela, bg=preto)
frame_login.pack(expand=True)

Label(frame_login, text="💰 Controle Financeiro",
      bg=preto, fg=verde, font=("Arial", 24, "bold")).pack(pady=20)

Label(frame_login, text="Email", bg=preto, fg=branco).pack()
entry_email = Entry(frame_login, width=40)
entry_email.pack(pady=5)

Label(frame_login, text="Senha", bg=preto, fg=branco).pack()
entry_senha = Entry(frame_login, width=40, show="*")
entry_senha.pack(pady=5)

Button(frame_login, text="Entrar", bg=verde, fg=preto,
       width=25, command=login).pack(pady=10)

Button(frame_login, text="Criar Conta", bg=amarelo,
       fg=preto, width=25, command=mostrar_cadastro).pack(pady=5)

Button(frame_login, text="Excluir Conta", bg=vermelho,
       fg=branco, width=25, command=excluir_conta).pack(pady=5)

msg_login = Label(frame_login, text="", bg=preto, fg=vermelho)
msg_login.pack()

# ================= CADASTRO =================

frame_cadastro = Frame(janela, bg=preto)

Label(frame_cadastro, text="Criar Conta",
      bg=preto, fg=amarelo, font=("Arial", 22, "bold")).pack(pady=20)

Label(frame_cadastro, text="Nome", bg=preto, fg=branco).pack()
entry_nome = Entry(frame_cadastro, width=40)
entry_nome.pack()

Label(frame_cadastro, text="Email", bg=preto, fg=branco).pack()
entry_email_cad = Entry(frame_cadastro, width=40)
entry_email_cad.pack()

Label(frame_cadastro, text="Senha", bg=preto, fg=branco).pack()
entry_senha_cad = Entry(frame_cadastro, width=40, show="*")
entry_senha_cad.pack()

Button(frame_cadastro, text="Salvar Cadastro", bg=amarelo,
       fg=preto, width=25, command=cadastrar).pack(pady=10)

Button(frame_cadastro, text="Voltar", width=25,
       command=mostrar_login).pack()

msg_cadastro = Label(frame_cadastro, text="", bg=preto)
msg_cadastro.pack()

# ================= DASHBOARD =================

frame_dashboard = Frame(janela, bg=preto)

lbl_boas_vindas = Label(frame_dashboard, text="",
                        bg=preto, fg=branco, font=("Arial", 14))
lbl_boas_vindas.pack(pady=10)

lbl_saldo = Label(frame_dashboard, text="Saldo: R$ 0.00",
                  bg=preto, fg=verde, font=("Arial", 24, "bold"))
lbl_saldo.pack()

# ================= INPUTS =================

frame_inputs = Frame(frame_dashboard, bg=preto)
frame_inputs.pack(pady=10)

Label(frame_inputs, text="Descrição", bg=preto, fg=branco).grid(row=0, column=0)
entry_desc = Entry(frame_inputs, width=30)
entry_desc.grid(row=0, column=1, padx=10)

Label(frame_inputs, text="Valor", bg=preto, fg=branco).grid(row=0, column=2)
entry_valor = Entry(frame_inputs, width=15)
entry_valor.grid(row=0, column=3, padx=10)

# ================= ALERTA =================

lbl_alerta = Label(frame_dashboard, text="",
                   bg=preto, fg=verde,
                   font=("Arial", 12, "bold"),
                   justify="center", wraplength=800)
lbl_alerta.pack(pady=10)

# ================= LISTA =================

lista_transacoes = Listbox(frame_dashboard,
                            width=110, height=15,
                            bg=cinza, fg=branco,
                            font=("Courier", 11))
lista_transacoes.pack(pady=10)

# ================= ESTATÍSTICAS =================

frame_stats = Frame(frame_dashboard, bg="#1e1e1e",
                    bd=2, relief="ridge")
frame_stats.pack(fill=X, padx=20, pady=10)

lbl_maior_receita = Label(frame_stats,
                          text="💰 Maior Receita: R$ 0.00",
                          bg="#1e1e1e", fg=verde)
lbl_maior_receita.pack(pady=3)

lbl_menor_receita = Label(frame_stats,
                          text="💵 Menor Receita: R$ 0.00",
                          bg="#1e1e1e", fg=verde)
lbl_menor_receita.pack(pady=3)

lbl_maior_despesa = Label(frame_stats,
                          text="💸 Maior Despesa: R$ 0.00",
                          bg="#1e1e1e", fg=vermelho)
lbl_maior_despesa.pack(pady=3)

lbl_menor_despesa = Label(frame_stats,
                          text="🧾 Menor Despesa: R$ 0.00",
                          bg="#1e1e1e", fg=vermelho)
lbl_menor_despesa.pack(pady=3)

# ================= BOTÕES =================

frame_botoes = Frame(frame_dashboard, bg=preto)
frame_botoes.pack(pady=15)

Button(frame_botoes, text="💰 Receita", bg=verde,
       width=15, command=lambda: adicionar_transacao("Receita")).grid(row=0, column=0, padx=5)

Button(frame_botoes, text="💸 Despesa", bg=vermelho,
       fg=branco, width=15, command=lambda: adicionar_transacao("Despesa")).grid(row=0, column=1, padx=5)

Button(frame_botoes, text="🗑 Excluir", bg=laranja,
       fg=branco, width=15, command=excluir_selecionado).grid(row=0, column=2, padx=5)

Button(frame_botoes, text="📊 Gráfico", bg=azul,
       fg=branco, width=15, command=gerar_grafico).grid(row=0, column=3, padx=5)

Button(frame_botoes, text="📋 Relatórios", bg=roxo,
       fg=branco, width=15, command=exibir_relatorios).grid(row=0, column=4, padx=5)

Button(frame_dashboard, text="Sair", bg=cinza,
       fg=branco, width=20, command=mostrar_login).pack(pady=20)

# ================= INICIAR =================

janela.mainloop()
