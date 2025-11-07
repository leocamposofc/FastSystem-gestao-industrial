import sqlite3

conn = sqlite3.connect("orcamentos.db")
cur = conn.cursor()

# === TABELA DE STATUS ===
cur.execute("""
CREATE TABLE IF NOT EXISTS status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT
);
""")

# Popula os status apenas se a tabela estiver vazia
cur.execute("SELECT COUNT(*) FROM status")
if cur.fetchone()[0] == 0:
    cur.executemany("""
        INSERT INTO status (nome, descricao) VALUES (?, ?)
    """, [
        ('Em elaboração', 'Orçamento em fase de criação.'),
        ('Aguardando aprovação', 'Enviado ao cliente, aguardando retorno.'),
        ('Em revisão', 'Devolvido para ajustes.'),
        ('Aprovado', 'Aprovado pelo cliente.'),
        ('Em execução', 'Serviço em andamento.'),
        ('Concluído', 'Serviço finalizado.'),
        ('Reprovado', 'Recusado pelo cliente.'),
        ('Cancelado', 'Cancelado antes da execução.'),
        ('Expirado', 'Prazo de validade ultrapassado.'),
        ('Aguardando pagamento', 'Aprovado, mas não pago.'),
        ('Pago', 'Pagamento confirmado.')
    ])
    print("✅ Status padrão inseridos.")

# === TABELA DE ORÇAMENTOS ===
cur.execute("""
CREATE TABLE IF NOT EXISTS orcamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    cliente_nome TEXT,
    cliente_empresa TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status_id INTEGER,
    total_geral REAL,
    observacoes TEXT,
    FOREIGN KEY (status_id) REFERENCES status(id)
);
""")

# === DEMAIS TABELAS ===
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

print("✅ Banco de dados 'orcamentos.db' recriado com sucesso!")
