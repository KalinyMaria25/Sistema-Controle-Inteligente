if __name__ == "__main__":

    # ================= INICIALIZAÇÃO =================
    janela = Tk()
    janela.title("Sistema Financeiro")
    janela.geometry("1100x750")
    janela.config(bg=preto)

    # ================= INICIAR NA TELA DE LOGIN =================
    frame_login.pack(expand=True)

    # ================= FECHAMENTO SEGURO =================
    def fechar_sistema():
        try:
            conexao.close()
        except:
            pass
        janela.destroy()

    janela.protocol("WM_DELETE_WINDOW", fechar_sistema)

    # ================= INICIAR LOOP =================
    janela.mainloop()
