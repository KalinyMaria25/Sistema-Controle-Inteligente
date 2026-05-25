from interface import janela
from dados import conexao

# ================= FECHAR =================

def fechar_sistema():

    conexao.close()

    janela.destroy()

janela.protocol(
    "WM_DELETE_WINDOW",
    fechar_sistema
)

# ================= EXECUTAR =================

janela.mainloop()
