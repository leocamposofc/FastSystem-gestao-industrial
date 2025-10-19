import sqlite3

conn = sqlite3.connect("orcamentos.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS orcamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    cliente_nome TEXT,
    cliente_empresa TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Aguardando aprovação',
    total_geral REAL,
    observacoes TEXT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS camadas_massa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orcamento_id INTEGER,
    tipo TEXT,
    metragem REAL,
    espessura REAL,
    densidade REAL,
    preco REAL,
    perda REAL,
    frete REAL,
    FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS camadas_cola (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orcamento_id INTEGER,
    tipo TEXT,
    metragem REAL,
    litro_m REAL,
    litro_tonel REAL,
    preco_tonel REAL,
    perda REAL,
    frete_tonel REAL,
    FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS terraplanagem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orcamento_id INTEGER,
    tipo_operacao TEXT,
    area REAL,
    espessura REAL,
    densidade REAL,
    preco REAL,
    perda REAL,
    frete REAL,
    FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS custos_extras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    orcamento_id INTEGER,
    tipo TEXT,
    quantidade INTEGER,
    valor_unitario REAL,
    total REAL,
    FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id)
);
""")

conn.commit()
conn.close()

print("✅ Banco de dados 'orcamentos.db' criado com sucesso!")
