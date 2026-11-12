import sqlite3
from pathlib import Path
def get_usuarios_connection():
    caminho = Path(__file__).resolve().parent / "usuarios.db"

    conn = sqlite3.connect(caminho)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def criar_tabelas_usuarios():
    conn = get_usuarios_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            senha TEXT NOT NULL,
            cpf TEXT NOT NULL UNIQUE,
            setor TEXT NOT NULL,
            funcao TEXT NOT NULL DEFAULT 'usuario'
                CHECK(funcao IN ('admin', 'usuario')),
            status TEXT NOT NULL DEFAULT 'ativo'
                CHECK(status IN ('ativo', 'inativo')),
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ultimo_acesso TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS permissoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            modulo TEXT NOT NULL,
            visualizar INTEGER NOT NULL DEFAULT 0,
            criar INTEGER NOT NULL DEFAULT 0,
            editar INTEGER NOT NULL DEFAULT 0,
            excluir INTEGER NOT NULL DEFAULT 0,

            FOREIGN KEY (usuario_id)
                REFERENCES usuarios(id)
                ON DELETE CASCADE,

            UNIQUE(usuario_id, modulo)
        )
    """)

    conn.commit()
    conn.close()
