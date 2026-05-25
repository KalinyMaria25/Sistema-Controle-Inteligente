import sqlite3

# ================= BANCO =================

conexao = sqlite3.connect("financeiro.db")

cursor = conexao.cursor()

# ================= TABELA USUÁRIOS =================

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    nome TEXT,

    email TEXT UNIQUE,

    senha TEXT
)
""")

# ================= TABELA TRANSAÇÕES =================

cursor.execute("""
CREATE TABLE IF NOT EXISTS transacoes(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    tipo TEXT,

    valor REAL,

    descricao TEXT,

    data TEXT
)
""")

# ================= SALVAR =================

conexao.commit()
