
import sqlite3
import re
from pathlib import Path
from getpass import getpass
from werkzeug.security import generate_password_hash


# Banco exclusivo dos usuários
CAMINHO_BANCO = Path(__file__).resolve().parent / "usuarios.db"


def criar_tabelas(conn):

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


def criar_admin():

    conn = sqlite3.connect(CAMINHO_BANCO)

    try:
        criar_tabelas(conn)

        quantidade = conn.execute(
            "SELECT COUNT(*) FROM usuarios WHERE funcao = 'admin'"
        ).fetchone()[0]

        if quantidade > 0:
            print("\nJá existe um administrador cadastrado.")
            return

        print("\n=== CADASTRO DO ADMINISTRADOR ===\n")

        nome = input("Nome completo: ").strip()
        email = input("E-mail: ").strip().lower()
        cpf = re.sub(r"\D", "", input("CPF: "))
        setor = input("Setor: ").strip()

        if not nome or not email or not setor:
            print("\nPreencha todos os campos.")
            return

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            print("\nE-mail inválido.")
            return

        if len(cpf) != 11:
            print("\nCPF deve conter 11 dígitos.")
            return

        senha = getpass("\nCrie sua senha: ")
        confirmacao = getpass("Confirme sua senha: ")

        if len(senha) < 12:
            print("\nUse uma senha com pelo menos 12 caracteres.")
            return

        if senha != confirmacao:
            print("\nAs senhas não conferem.")
            return

        senha_hash = generate_password_hash(senha)

        conn.execute("""
            INSERT INTO usuarios
                (nome, email, senha, cpf, setor, funcao, status)
            VALUES (?, ?, ?, ?, ?, 'admin', 'ativo')
        """, (nome, email, senha_hash, cpf, setor))

        conn.commit()

        print("\nAdministrador cadastrado com sucesso!")
        print("Banco:", CAMINHO_BANCO)

    except sqlite3.IntegrityError:
        conn.rollback()
        print("\nErro: este e-mail ou CPF já está cadastrado.")

    finally:
        conn.close()


if __name__ == "__main__":
    criar_admin()
