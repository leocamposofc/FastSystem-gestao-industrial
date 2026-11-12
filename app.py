from datetime import datetime, timedelta
import time
from flask import Flask, session, abort, render_template, request, send_file, redirect, url_for, jsonify, flash
from Configuracoes import configuracoes
import io
from pathlib import Path
import json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import sqlite3
from Configuracoes import configuracoes
import os
from functools import wraps

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

app = Flask(__name__, template_folder='templates')

# INICIO AREA DE CONFIGURAÇÃO DE SESSÃO E LOGIN
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")

from datetime import timedelta

app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=5)

app.config["SESSION_REFRESH_EACH_REQUEST"] = True

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False #trocar para true ao usar https

app.config["REMEMBER_COOKIE_HTTPONLY"] = True
app.config["REMEMBER_COOKIE_SECURE"] = True

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"
login_manager.login_message = "Faça login para acessar esta página."
login_manager.login_message_category = "warning"

# Classes dos usuarios
class Usuario(UserMixin):

    def __init__(self, dados):
        self.id = dados["id"]
        self.nome = dados["nome"]
        self.email = dados["email"]
        self.cpf = dados["cpf"]
        self.setor = dados["setor"]
        self.funcao = dados["funcao"]
        self.status = dados["status"]

    @property
    def is_active(self):
        return self.status == "ativo"



# CARREGAR USUÁRIO DA SESSÃO
@login_manager.user_loader
def carregar_usuario(usuario_id):

    conn = get_usuarios_connection()

    dados = conn.execute(
        "SELECT * FROM usuarios WHERE id = ? AND status = 'ativo'",
        (usuario_id,)
    ).fetchone()

    conn.close()

    if dados:
        return Usuario(dados)

    return None


# CONTROLE DE INATIVIDADE - 30 MINUTOS
@app.before_request
def controlar_inatividade():

    # Ignora usuários que ainda não fizeram login
    if not current_user.is_authenticated:
        return

    # Não considera arquivos estáticos como atividade
    if request.endpoint == "static":
        return

    agora = time.time()

    ultima_atividade = session.get("ultima_atividade")

    # Verifica se passaram 30 minutos
    if ultima_atividade and agora - ultima_atividade > 1800: # 1800 representa 30m

        logout_user()
        session.clear()

        flash(
            "Sua sessão expirou por inatividade. Faça login novamente.",
            "warning"
        )

        return redirect(url_for("login"))

    # Atualiza o horário da última atividade
    session["ultima_atividade"] = agora


def permissao_required(modulo, acao):
    colunas_validas = {
        "visualizar",
        "criar",
        "editar",
        "excluir"
    }

    if acao not in colunas_validas:
        raise ValueError("Ação de permissão inválida.")

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            # Administrador tem acesso total
            if current_user.funcao == "admin":
                return func(*args, **kwargs)

            conn = get_usuarios_connection()

            permissao = conn.execute(
                f"""
                SELECT {acao}
                FROM permissoes
                WHERE usuario_id = ? AND modulo = ?
                """,
                (current_user.id, modulo)
            ).fetchone()

            conn.close()

            # Sem permissão, bloqueia o acesso
            if not permissao or not permissao[0]:
                abort(403)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("login"))

        if current_user.funcao != "admin":
            abort(403)

        return func(*args, **kwargs)

    return wrapper


MODULOS_USUARIOS = [
    {"chave": "cotador", "nome": "Cotador"},
    {"chave": "orcamentos", "nome": "Orçamentos"},
    {"chave": "clientes", "nome": "Clientes"},
    {"chave": "equipamentos", "nome": "Equipamentos"},
    {"chave": "configuracoes", "nome": "Configurações"},
    {"chave": "usuarios", "nome": "Usuários"},
]


ACOES_PERMISSAO = [
    "visualizar",
    "criar",
    "editar",
    "excluir"
]


def obter_permissoes_formulario():
    permissoes = {}

    for modulo in MODULOS_USUARIOS:
        chave = modulo["chave"]

        permissoes[chave] = {}

        for acao in ACOES_PERMISSAO:
            campo = f"permissoes[{chave}][{acao}]"

            permissoes[chave][acao] = (
                1 if request.form.get(campo) == "1" else 0
            )

    return permissoes


def calcular_custo(metragem, espessura_cm, preco_por_m3=250):
    volume_m3 = metragem * (espessura_cm / 100)
    custo_estimado = volume_m3 * preco_por_m3
    return custo_estimado


def get_db_connection():
    conn = sqlite3.connect('clientes.db')
    conn.row_factory = sqlite3.Row  # permite acessar colunas por nome
    return conn


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



def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


@app.context_processor
def inject_config():
    return dict(
        empresa_nome=configuracoes.nome_empresa,
        empresa_slogan=configuracoes.slogan_empresa,
        empresa_site=configuracoes.site_empresa,
        empresa_email=configuracoes.email_empresa,
        sistema_nome=configuracoes.nome_sistema,
        versao_sistema=configuracoes.versao_sistema
    )


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    session.permanent = True
    session["ultima_atividade"] = time.time()
    session["inicio_sessao"] = time.time()
    # Se já estiver conectado, vai direto ao sistema
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "")

        conn = get_usuarios_connection()

        usuario_dados = conn.execute(
            """
            SELECT * FROM usuarios
            WHERE email = ? COLLATE NOCASE
            AND status = 'ativo'
            """,
            (email,)
        ).fetchone()

        conn.close()

        # Verifica se o usuário existe e se a senha está correta
        if usuario_dados and check_password_hash(
            usuario_dados["senha"], senha
        ):

            usuario = Usuario(usuario_dados)

            session.permanent = True  # Mantém a sessão ativa

            login_user(usuario)

            # Atualiza a data do último acesso
            conn = get_usuarios_connection()

            conn.execute(
                """
                UPDATE usuarios
                SET ultimo_acesso = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (usuario.id,)
            )

            conn.commit()
            conn.close()

            return redirect(url_for("inicio"))

        flash("E-mail ou senha incorretos, ou usuário inativo.", "danger")

    return render_template("login.html")


# LOGOUT
@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Você saiu do sistema.", "success")

    return redirect(url_for("login"))



# INICIO TELAS

@app.route("/usuarios")
@login_required
@admin_required
def listar_usuarios():

    conn = get_usuarios_connection()

    usuarios = conn.execute("""
        SELECT
            id,
            nome,
            email,
            cpf,
            setor,
            funcao,
            status,
            data_cadastro,
            ultimo_acesso
        FROM usuarios
        ORDER BY nome ASC
    """).fetchall()

    conn.close()

    return render_template(
        "usuarios.html",
        usuarios=usuarios
    )


@app.route("/usuarios/cadastrar", methods=["GET", "POST"])
@login_required
@admin_required
def cadastrar_usuario():

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        cpf = "".join(filter(str.isdigit, request.form.get("cpf", "")))
        setor = request.form.get("setor", "").strip()
        funcao = request.form.get("funcao", "usuario")
        status = request.form.get("status", "ativo")
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")

        if not nome or not email or not cpf or not setor:
            flash("Preencha todos os campos obrigatórios.", "warning")
            return redirect(url_for("cadastrar_usuario"))

        if len(cpf) != 11:
            flash("O CPF deve conter 11 números.", "warning")
            return redirect(url_for("cadastrar_usuario"))

        if len(senha) < 12:
            flash("A senha deve ter pelo menos 12 caracteres.", "warning")
            return redirect(url_for("cadastrar_usuario"))

        if senha != confirmar_senha:
            flash("As senhas não coincidem.", "warning")
            return redirect(url_for("cadastrar_usuario"))

        if funcao not in ("admin", "usuario"):
            flash("Tipo de usuário inválido.", "warning")
            return redirect(url_for("cadastrar_usuario"))

        if status not in ("ativo", "inativo"):
            flash("Status inválido.", "warning")
            return redirect(url_for("cadastrar_usuario"))

        permissoes = obter_permissoes_formulario()

        conn = get_usuarios_connection()

        try:
            cursor = conn.execute("""
                INSERT INTO usuarios
                (nome, email, senha, cpf, setor, funcao, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                nome,
                email,
                generate_password_hash(senha),
                cpf,
                setor,
                funcao,
                status
            ))

            usuario_id = cursor.lastrowid

            for modulo, acoes in permissoes.items():
                conn.execute("""
                    INSERT INTO permissoes
                    (usuario_id, modulo, visualizar, criar, editar, excluir)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    usuario_id,
                    modulo,
                    acoes["visualizar"],
                    acoes["criar"],
                    acoes["editar"],
                    acoes["excluir"]
                ))

            conn.commit()

            flash("Usuário cadastrado com sucesso!", "success")
            return redirect(url_for("listar_usuarios"))

        except sqlite3.IntegrityError:
            conn.rollback()
            flash("Este e-mail ou CPF já está cadastrado.", "warning")

        finally:
            conn.close()

        return redirect(url_for("cadastrar_usuario"))

    return render_template(
        "cadastrar_usuario.html",
        modulos=MODULOS_USUARIOS
    )


@app.route("/usuarios/<int:usuario_id>/editar", methods=["GET", "POST"])
@login_required
@admin_required
def editar_usuario(usuario_id):

    conn = get_usuarios_connection()

    usuario = conn.execute("""
        SELECT *
        FROM usuarios
        WHERE id = ?
    """, (usuario_id,)).fetchone()

    if not usuario:
        conn.close()
        flash("Usuário não encontrado.", "warning")
        return redirect(url_for("listar_usuarios"))

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        setor = request.form.get("setor", "").strip()
        funcao = request.form.get("funcao", "usuario")
        status = request.form.get("status", "ativo")
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")

        if not nome or not email or not setor:
            conn.close()
            flash("Preencha todos os campos obrigatórios.", "warning")
            return redirect(url_for("editar_usuario", usuario_id=usuario_id))

        if funcao not in ("admin", "usuario"):
            conn.close()
            flash("Tipo de usuário inválido.", "warning")
            return redirect(url_for("editar_usuario", usuario_id=usuario_id))

        if status not in ("ativo", "inativo"):
            conn.close()
            flash("Status inválido.", "warning")
            return redirect(url_for("editar_usuario", usuario_id=usuario_id))

        if senha and len(senha) < 12:
            conn.close()
            flash("A nova senha deve ter pelo menos 12 caracteres.", "warning")
            return redirect(url_for("editar_usuario", usuario_id=usuario_id))

        if senha != confirmar_senha:
            conn.close()
            flash("As novas senhas não coincidem.", "warning")
            return redirect(url_for("editar_usuario", usuario_id=usuario_id))

        permissoes = obter_permissoes_formulario()

        try:
            conn.execute("""
                UPDATE usuarios
                SET nome = ?,
                    email = ?,
                    setor = ?,
                    funcao = ?,
                    status = ?
                WHERE id = ?
            """, (
                nome,
                email,
                setor,
                funcao,
                status,
                usuario_id
            ))

            if senha:
                conn.execute("""
                    UPDATE usuarios
                    SET senha = ?
                    WHERE id = ?
                """, (
                    generate_password_hash(senha),
                    usuario_id
                ))

            # Substitui as permissões antigas pelas novas
            conn.execute("""
                DELETE FROM permissoes
                WHERE usuario_id = ?
            """, (usuario_id,))

            for modulo, acoes in permissoes.items():
                conn.execute("""
                    INSERT INTO permissoes
                    (usuario_id, modulo, visualizar, criar, editar, excluir)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    usuario_id,
                    modulo,
                    acoes["visualizar"],
                    acoes["criar"],
                    acoes["editar"],
                    acoes["excluir"]
                ))

            conn.commit()

            flash("Usuário atualizado com sucesso!", "success")
            return redirect(url_for("listar_usuarios"))

        except sqlite3.IntegrityError:
            conn.rollback()
            flash("Este e-mail já está sendo utilizado por outro usuário.", "warning")

        finally:
            conn.close()

        return redirect(url_for("editar_usuario", usuario_id=usuario_id))

    # Busca as permissões atuais para preencher os checkboxes
    registros = conn.execute("""
        SELECT modulo, visualizar, criar, editar, excluir
        FROM permissoes
        WHERE usuario_id = ?
    """, (usuario_id,)).fetchall()

    conn.close()

    permissoes = {}

    for registro in registros:
        permissoes[registro["modulo"]] = {
            "visualizar": registro["visualizar"],
            "criar": registro["criar"],
            "editar": registro["editar"],
            "excluir": registro["excluir"]
        }

    return render_template(
        "editar_usuario.html",
        usuario=usuario,
        modulos=MODULOS_USUARIOS,
        permissoes=permissoes
    )


@app.route("/cotador", methods=["GET", "POST"])
@login_required
@permissao_required("cotador", "visualizar")
def index():
    # conectando ao banco de dados
    conn = sqlite3.connect("clientes.db")
    cursor = conn.cursor()
    # buscando clientes
    cursor.execute("SELECT id, nome, empresa FROM clientes")
    clientes = cursor.fetchall()

    custo = None
    erro = ""
    # Preços dos equipamentos
    precos = {
        "rolo_compactor": configuracoes.custo_locacao_rolo,
        "caminhao_caçamba": configuracoes.custo_caminhao_cacamba,
        "pavimentadora": configuracoes.custo_pavimentadora,
        "equipe_mao_obra": configuracoes.custo_mao_obra,
        "sinalizacao": configuracoes.custo_sinalizacao,
        "outros": configuracoes.custo_outros
    }
    if request.method == "POST":
        try:
            metragem = float(request.form["metragem"])
            espessura_cm = float(request.form["espessura_cm"])
            custo = calcular_custo(metragem, espessura_cm)
            equipamentos = request.form.getlist("equipamentos")
            # Soma o preço de cada equipamento selecionado
            for eq in equipamentos:
                eq = eq.strip()
                if eq in precos:
                    custo += precos[eq]
            custo = f"{custo:.2f}"
        except ValueError:
            erro = "Por favor, digite valores numéricos válidos."
    return render_template(
        ("cotador.html"),
        clientes=clientes,
        titulo_pagina="Cotador de Capeamento de Asfalto",
        custo=custo,
        erro=erro,
        preco_rolo=precos["rolo_compactor"],
        preco_caminhao=precos["caminhao_caçamba"],
        preco_pavimentadora=precos["pavimentadora"],
        preco_mao_obra=precos["equipe_mao_obra"],
        preco_sinalizacao=precos["sinalizacao"],
        preco_outros=precos["outros"],
        preco_massa=configuracoes.preco_massa,
        perda=configuracoes.margem_perda,
        litro_tonel=configuracoes.litros_por_tonel,
        preco_tonel=configuracoes.preco_tonel,
        frete_tonel=configuracoes.frete_tonel

    )


def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


@app.route("/salvar_orcamento", methods=["POST"])
@login_required
@permissao_required("orcamentos", "criar")
def salvar_orcamento():
    dados = request.get_json()
    local = dados.get("local_obra", {})
    conn = sqlite3.connect("orcamentos.db")
    cur = conn.cursor()

    # Cria orçamento principal
    cur.execute("""
        INSERT INTO orcamentos (cliente_id, cliente_nome, cliente_empresa, total_geral, endereco, latitude, longitude, complementos)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        dados["cliente"]["id"],
        dados["cliente"]["nome"],
        dados["cliente"]["empresa"],
        safe_float(dados["resumo"]["geral"]),
        local.get("endereco"),
        local.get("lat"),
        local.get("lng"),
        local.get("complementos")
    ))
    orcamento_id = cur.lastrowid

    # Salva massas
    for m in dados["massas"]:
        cur.execute("""
            INSERT INTO camadas_massa
            (orcamento_id, tipo, metragem, espessura, densidade, preco, perda, frete)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            orcamento_id,
            m.get("tipo"),
            safe_float(m.get("metragem")),
            safe_float(m.get("espessura")),
            safe_float(m.get("densidade")),
            safe_float(m.get("preco")),
            safe_float(m.get("perda")),
            safe_float(m.get("frete"))
        ))

    # Salva colas
    for c in dados["colas"]:
        cur.execute("""
            INSERT INTO camadas_cola
            (orcamento_id, tipo, metragem, litro_m, litro_tonel, preco_tonel, perda, frete_tonel)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            orcamento_id,
            c.get("tipo"),
            safe_float(c.get("metragem")),
            safe_float(c.get("litro_m")),
            safe_float(c.get("litro_tonel")),
            safe_float(c.get("preco_tonel")),
            safe_float(c.get("perda")),
            safe_float(c.get("frete_tonel"))
        ))

    # Terraplanagem
    for t in dados["terraplanagem"]:
        cur.execute("""
            INSERT INTO terraplanagem (orcamento_id, tipo_operacao, area, espessura, densidade, preco, perda, frete)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            orcamento_id,
            t.get("tipo_operacao"),
            safe_float(t.get("area")),
            safe_float(t.get("espessura")),
            safe_float(t.get("densidade")),
            safe_float(t.get("preco")),
            safe_float(t.get("perda")),
            safe_float(t.get("frete"))
        ))

    # Custos extras
    for e in dados["extras"]:
        cur.execute("""
            INSERT INTO custos_extras
            (orcamento_id, tipo, quantidade, valor_unitario, total)
            VALUES (?, ?, ?, ?, ?)
        """, (
            orcamento_id,
            e.get("tipo"),
            safe_float(e.get("quantidade")),
            safe_float(e.get("valor_unitario")),
            safe_float(e.get("total"))
        ))

    conn.commit()
    conn.close()

    # Cria pasta e salva JSON do orçamento
    pasta = Path("orcamentos") / f"orcamento_{orcamento_id}"
    pasta.mkdir(parents=True, exist_ok=True)
    with open(pasta / "dados.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "sucesso", "orcamento_id": orcamento_id})


@app.route("/orcamentos")
@login_required
@permissao_required("orcamentos", "visualizar")
def listar_orcamentos():
    conn = sqlite3.connect("orcamentos.db")
    cur = conn.cursor()

    # 1️⃣ Pega o prazo de validade
    prazo_validade = timedelta(days=configuracoes.validade_orcamento_dias)
    hoje = datetime.now()

    # 2️⃣ Busca orçamentos ainda válidos (não vencidos)
    cur.execute("""
        SELECT id, data_criacao, status_id
        FROM orcamentos
        WHERE status_id != (
            SELECT id FROM status WHERE nome = 'Vencido'
        )
    """)
    orcs = cur.fetchall()

    # 3️⃣ Verifica se algum venceu
    for id_orc, data_criacao_str, status_id in orcs:
        try:
            data_criacao = datetime.fromisoformat(data_criacao_str)
        except ValueError:
            data_criacao = datetime.strptime(
                data_criacao_str, "%Y-%m-%d %H:%M:%S")

        if hoje - data_criacao > prazo_validade:
            cur.execute("""
                UPDATE orcamentos
                SET status_id = (SELECT id FROM status WHERE nome = 'Vencido')
                WHERE id = ?
            """, (id_orc,))

    conn.commit()

    # 4️⃣ Busca todos os status possíveis (para o seletor)
    cur.execute("SELECT id, nome FROM status ORDER BY id")
    status_opcoes = cur.fetchall()

    # 5️⃣ Busca orçamentos já atualizados, sem join com clientes
    cur.execute("""
        SELECT o.id, 
               o.cliente_nome, 
               o.cliente_empresa, 
               o.data_criacao, 
               s.nome AS status_nome, 
               o.status_id, 
               o.total_geral
        FROM orcamentos o
        LEFT JOIN status s ON o.status_id = s.id
        ORDER BY o.data_criacao DESC
    """)
    orcamentos = cur.fetchall()

    conn.close()

    # 6️⃣ Renderiza a tela
    return render_template(
        "orcamentos_lista.html",
        orcamentos=orcamentos,
        status_opcoes=status_opcoes
    )


@app.route("/atualizar_status", methods=["POST"])
@login_required
@permissao_required("orcamentos", "editar")
def atualizar_status():
    data = request.get_json()
    orcamento_id = data.get("id")
    status_id = data.get("status_id")

    if not orcamento_id or not status_id:
        return jsonify({"erro": "Dados incompletos"}), 400

    conn = sqlite3.connect("orcamentos.db")
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE orcamentos
            SET status_id = ?
            WHERE id = ?
        """, (status_id, orcamento_id))
        conn.commit()
    except Exception as e:
        print("Erro ao atualizar status:", e)
        return jsonify({"erro": "Erro interno"}), 500
    finally:
        conn.close()

    return jsonify({"sucesso": True})



@app.route("/orcamento/<int:orcamento_id>")
@login_required
@permissao_required("orcamentos", "visualizar")
def ver_orcamento(orcamento_id):
    conn = sqlite3.connect("orcamentos.db")
    cur = conn.cursor()

    # Info principal
    cur.execute("SELECT * FROM orcamentos WHERE id=?", (orcamento_id,))
    orc = cur.fetchone()

    if not orc:
        conn.close()
        return f"<h3>Orçamento #{orcamento_id} não encontrado.</h3>"

    # Localização da obra
    local_obra = {
        "endereco": orc[8],
        "lat": orc[9],
        "lng": orc[10],
        "complementos": orc[11]
    }

    # Tabelas relacionadas
    cur.execute("SELECT * FROM camadas_massa WHERE orcamento_id=?",
                (orcamento_id,))
    massas = cur.fetchall()

    cur.execute("SELECT * FROM camadas_cola WHERE orcamento_id=?",
                (orcamento_id,))
    colas = cur.fetchall()

    cur.execute("SELECT * FROM terraplanagem WHERE orcamento_id=?",
                (orcamento_id,))
    terra = cur.fetchall()

    cur.execute("SELECT * FROM custos_extras WHERE orcamento_id=?",
                (orcamento_id,))
    extras = cur.fetchall()

    cur.execute("SELECT * FROM status WHERE id=?", (orc[5],))
    status = cur.fetchone()

    # FILTRA REGISTROS SEM IDENTIFICAÇÃO
    def registro_valido(registro):
        valor = registro[2]

        return (
            valor is not None
            and str(valor).strip().lower() not in ("", "none", "null")
        )

    massas = [m for m in massas if registro_valido(m)]
    colas = [c for c in colas if registro_valido(c)]
    terra = [t for t in terra if registro_valido(t)]
    extras = [e for e in extras if registro_valido(e)]

    conn.close()

    return render_template(
        "ver_orcamento.html",
        orc=orc,
        massas=massas,
        colas=colas,
        terra=terra,
        extras=extras,
        local_obra=local_obra,
        status=status
    )



@app.route("/emitir_orcamento", methods=["POST"])
@login_required
@permissao_required("orcamentos", "criar")
def emitir_orcamento():
    try:
        metragem = float(request.form["metragem"])
        espessura_cm = float(request.form["espessura_cm"])
        custo_base = calcular_custo(metragem, espessura_cm)
        equipamentos = request.form.getlist("equipamentos")
        precos = {
            "rolo_compactor": configuracoes.custo_locacao_rolo,
            "caminhao_caçamba": configuracoes.custo_caminhao_cacamba,
            "pavimentadora": configuracoes.custo_pavimentadora,
            "equipe_mao_obra": configuracoes.custo_mao_obra,
            "sinalizacao": configuracoes.custo_sinalizacao,
            "outros": configuracoes.custo_outros
        }
        custo_total = custo_base
        detalhes = []
        for eq in equipamentos:
            eq = eq.strip()
            if eq in precos:
                custo_total += precos[eq]
                detalhes.append(
                    f"{eq.replace('_', ' ').title()}: R$ {precos[eq]:.2f}")
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)

        # Logo quadrada (ajuste o caminho e tamanho conforme sua imagem)
        try:
            p.drawImage("midias/logo.jpeg", 50, 780,
                        width=60, height=60, mask='auto')
        except Exception:
            pass

        # Marca d'água como imagem (ajuste o caminho e tamanho conforme sua imagem)
        try:
            p.saveState()
            p.translate(150, 250)  # posição central aproximada
            p.setFillAlpha(0.15)   # transparência (requer ReportLab >= 3.5)
            p.drawImage("midias/marcadagua.png", 0, 0,
                        width=350, height=350, mask='auto')
            p.restoreState()
        except Exception:
            pass

        # Conteúdo principal
        p.setFont("Helvetica-Bold", 16)
        p.setFillColorRGB(0, 0, 0)
        p.drawString(50, 720, "Orçamento Detalhado - Capeamento de Asfalto")
        p.setFont("Helvetica", 12)
        p.drawString(50, 690, f"Metragem: {metragem} m²")
        p.drawString(50, 670, f"Espessura: {espessura_cm} cm")
        p.drawString(50, 650, f"Custo base: R$ {custo_base:.2f}")
        y = 630
        p.drawString(50, y, "Equipamentos selecionados:")
        y -= 20
        if detalhes:
            for item in detalhes:
                p.drawString(70, y, item)
                y -= 20
        else:
            p.drawString(70, y, "Nenhum equipamento selecionado.")
            y -= 20
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, f"Custo total estimado: R$ {custo_total:.2f}")

        # Rodapé
        p.setFont("Helvetica-Oblique", 10)
        p.setFillColorRGB(0.4, 0.4, 0.4)
        p.drawString(
            50, 40, f"{configuracoes.nome_empresa} - {configuracoes.site_empresa} | Este orçamento é válido por {configuracoes.validade_orcamento_dias} dias.")
        p.drawString(
            50, 25, f"Contato: {configuracoes.email_empresa} | Data emissão {datetime.now().strftime('%d/%m/%Y')}")

        p.showPage()
        p.save()
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="orcamento.pdf", mimetype="application/pdf")
    except Exception as e:
        return f"Erro ao gerar orçamento: {str(e)}", 400


@app.route("/", methods=["GET"])
@login_required
def inicio():
    return render_template("inicio.html", titulo_pagina="Início")


@app.route("/clientes", methods=["GET", "POST"])
@login_required
@permissao_required("clientes", "visualizar")
def clientes():
    mensagem = ""

    if request.method == "POST":
        # Deletar cliente
        if "deletar_id" in request.form:
            deletar_id = request.form.get("deletar_id")
            senha = request.form.get("senha_deletar", "")
            if senha == configuracoes.senha_de_seguranca:
                try:
                    banco = sqlite3.connect('clientes.db')
                    cursor = banco.cursor()
                    cursor.execute(
                        "DELETE FROM clientes WHERE id = ?", (deletar_id,))
                    banco.commit()
                    mensagem = "Cliente deletado com sucesso!"
                except Exception as e:
                    mensagem = f"Erro ao deletar cliente: {str(e)}"
                finally:
                    banco.close()
            else:
                mensagem = "Senha incorreta para deletar cliente."

    # GET: busca clientes e pega mensagem da query string
    mensagem = request.args.get("mensagem", "")
    clientes_lista = []
    try:
        banco = sqlite3.connect('clientes.db')
        cursor = banco.cursor()
        cursor.execute("""
            SELECT id, nome, sobrenome, empresa, cnpj, celular1, celular2, email, tipo,
                   endereco, cidade, estado, cep, observacoes
            FROM clientes
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
        for row in rows:
            clientes_lista.append({
                "id": row[0],
                "nome": row[1],
                "sobrenome": row[2],
                "empresa": row[3],
                "cnpj": row[4],
                "celular1": row[5],
                "celular2": row[6],
                "email": row[7],
                "tipo": row[8],
                "endereco": row[9],
                "cidade": row[10],
                "estado": row[11],
                "cep": row[12],
                "observacoes": row[13]
            })
    except Exception as e:
        mensagem = f"Erro ao buscar clientes: {str(e)}"
    finally:
        banco.close()

    return render_template("clientes.html", clientes=clientes_lista, sucesso=mensagem)


@app.route("/cliente_cadastro", methods=["GET", "POST"])
@login_required
@permissao_required("clientes", "criar")
def cliente_cadastro():
    mensagem = ""

    if request.method == "POST":
        print("Recebido POST para cadastro de cliente")
        print(request.form)
        nome = request.form.get("nome", "").strip()
        sobrenome = request.form.get("sobrenome", "").strip()
        empresa = request.form.get("empresa", "").strip()
        cnpj = request.form.get("cnpj", "").strip()
        celular1 = request.form.get("celular1", "").strip()
        celular2 = request.form.get("celular2", "").strip()
        email = request.form.get("email", "").strip()
        tipo = request.form.get("tipo", "").strip()
        endereco = request.form.get("endereco", "").strip()
        numero = request.form.get("numero", "").strip()
        complemento = request.form.get("complemento", "").strip()
        cidade = request.form.get("cidade", "").strip()
        estado = request.form.get("estado", "").strip()
        bairro = request.form.get("bairro", "").strip()
        cep = request.form.get("cep", "").strip()
        observacoes = request.form.get("observacoes", "").strip()
        cep_valido = request.form.get("cep_valido", "false")

        if nome and celular1 and email:
            if cep_valido == "true":
                try:
                    banco = sqlite3.connect('clientes.db')
                    cursor = banco.cursor()
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS clientes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome TEXT NOT NULL,
                            sobrenome TEXT,
                            empresa TEXT,
                            cnpj TEXT,
                            celular1 TEXT,
                            celular2 TEXT,
                            email TEXT,
                            tipo TEXT,
                            endereco TEXT,
                            numero TEXT,
                            complemento TEXT,
                            cidade TEXT,
                            estado TEXT,
                            bairro TEXT,
                            cep TEXT,
                            observacoes TEXT
                        )
                    """)
                    cursor.execute("""
                        INSERT INTO clientes (
                            nome, sobrenome, empresa, cnpj, celular1, celular2, email, tipo,
                            endereco, numero, complemento, cidade, estado, bairro, cep, observacoes
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        nome, sobrenome, empresa, cnpj, celular1, celular2, email, tipo,
                        endereco, numero, complemento, cidade, estado, bairro, cep, observacoes
                    ))
                    banco.commit()
                    mensagem = "Cliente cadastrado com sucesso!"
                except Exception as e:
                    mensagem = f"Erro ao cadastrar cliente: {str(e)}"
                finally:
                    banco.close()
            else:
                mensagem = "Erro: o CEP informado é inválido."
                return render_template("cadastro_cliente.html", mensagem=mensagem)
        else:
            mensagem = "Preencha os campos obrigatórios: Nome, Celular1 e Email."

    return render_template("cliente_cadastro.html", mensagem=mensagem)


@app.route("/exemplo", methods=["GET", "POST"])
@login_required
def exemplo():
    return render_template("exemplo.html")


@app.route('/clientes/<int:id>/view', methods=['GET', 'POST'])
@login_required
@permissao_required("clientes", "editar")
def editar_cliente(id):
    conn = get_db_connection()

    if request.method == 'POST':
        # Pega dados do formulário
        nome = request.form['nome']
        sobrenome = request.form.get('sobrenome')
        empresa = request.form['empresa']
        cnpj = request.form.get('cnpj')
        celular1 = request.form['celular1']
        celular2 = request.form.get('celular2')
        email = request.form['email']
        tipo = request.form['tipo']

        cep = request.form['cep']
        cidade = request.form['cidade']
        estado = request.form['estado']
        bairro = request.form['bairro']
        endereco = request.form['endereco']
        numero = request.form['numero']
        complemento = request.form.get('complemento')

        # Atualiza no banco
        conn.execute("""
            UPDATE clientes SET
                nome=?, sobrenome=?, empresa=?, cnpj=?, celular1=?, celular2=?,
                email=?, tipo=?, cep=?, cidade=?, estado=?, bairro=?,
                endereco=?, numero=?, complemento=?
            WHERE id=?
        """, (nome, sobrenome, empresa, cnpj, celular1, celular2, email, tipo,
              cep, cidade, estado, bairro, endereco, numero, complemento, id))
        conn.commit()
        conn.close()

        return redirect(url_for('clientes'))  # volta pra lista

    # Se for GET → busca os dados e mostra o form
    cliente = conn.execute(
        'SELECT * FROM clientes WHERE id = ?', (id,)).fetchone()
    conn.close()

    if cliente is None:
        return "Cliente não encontrado", 404

    return render_template('cliente_editar.html', cliente=cliente)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

