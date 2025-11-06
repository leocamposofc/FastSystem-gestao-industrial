from datetime import datetime
from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
from Configuracoes import configuracoes
import io
from pathlib import Path
import json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import sqlite3
from Configuracoes import configuracoes

app = Flask(__name__, template_folder='templates')


def calcular_custo(metragem, espessura_cm, preco_por_m3=250):
    volume_m3 = metragem * (espessura_cm / 100)
    custo_estimado = volume_m3 * preco_por_m3
    return custo_estimado


@app.route("/cotador", methods=["GET", "POST"])
def index():
    # conectando ao banco de dados
    conn = sqlite3.connect("clientes.db")
    cursor = conn.cursor()
    #buscando clientes
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

@app.route("/salvar_orcamento", methods=["POST"])
def salvar_orcamento():
    dados = request.get_json()
    conn = sqlite3.connect("orcamentos.db")
    cur = conn.cursor()

    # Cria orçamento principal
    cur.execute("""
        INSERT INTO orcamentos (cliente_id, cliente_nome, cliente_empresa, total_geral)
        VALUES (?, ?, ?, ?)
    """, (
        dados["cliente"]["id"],
        dados["cliente"]["nome"],
        dados["cliente"]["empresa"],
        dados["resumo"]["geral"]
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
            float(m.get("metragem", 0)),
            float(m.get("espessura", 0)),
            float(m.get("densidade", 0)),
            float(m.get("preco", 0)),
            float(m.get("perda", 0)),
            float(m.get("frete", 0))
        ))

    # Salva colas
    for c in dados["colas"]:
        cur.execute("""
            INSERT INTO camadas_cola (orcamento_id, tipo, metragem, litro_m, litro_tonel, preco_tonel, perda, frete_tonel)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            orcamento_id,
            m.get("tipo"),
            float(m.get("metragem", 0)),
            float(m.get("litro_m", 0)),
            float(m.get("litro_tonel", 0)),
            float(m.get("preco_tonel", 0)),
            float(m.get("perda", 0)),
            float(m.get("frete_tonel", 0))
        ))

    # Terraplanagem
    for t in dados["terra"]:
        cur.execute("""
            INSERT INTO terraplanagem (orcamento_id, tipo_operacao, area, espessura, densidade, preco, perda, frete)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (orcamento_id, *t.values()))

    # Custos extras
    for e in dados["extras"]:
        cur.execute("""
            INSERT INTO custos_extras
            (orcamento_id, tipo, quantidade, valor_unitario, total)
            VALUES (?, ?, ?, ?, ?)
        """, (
            orcamento_id,
            e.get("tipo"),
            float(e.get("quantidade", 0)),
            float(e.get("valor_unitario", 0)),
            float(e.get("total", 0))
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
def listar_orcamentos():
    conn = sqlite3.connect("orcamentos.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT id, cliente_nome, cliente_empresa, data_criacao, status, total_geral
        FROM orcamentos
        ORDER BY id DESC
    """)
    orcamentos = cur.fetchall()
    conn.close()
    return render_template("orcamentos_lista.html", orcamentos=orcamentos)


@app.route("/orcamento/<int:orcamento_id>")
def ver_orcamento(orcamento_id):
    conn = sqlite3.connect("orcamentos.db")
    cur = conn.cursor()

    # Info principal
    cur.execute("SELECT * FROM orcamentos WHERE id=?", (orcamento_id,))
    orc = cur.fetchone()

    if not orc:
        return f"<h3>Orçamento #{orcamento_id} não encontrado.</h3>"

    # Tabelas relacionadas
    cur.execute("SELECT * FROM camadas_massa WHERE orcamento_id=?", (orcamento_id,))
    massas = cur.fetchall()

    cur.execute("SELECT * FROM camadas_cola WHERE orcamento_id=?", (orcamento_id,))
    colas = cur.fetchall()

    cur.execute("SELECT * FROM terraplanagem WHERE orcamento_id=?", (orcamento_id,))
    terra = cur.fetchall()

    cur.execute("SELECT * FROM custos_extras WHERE orcamento_id=?", (orcamento_id,))
    extras = cur.fetchall()

    conn.close()

    return render_template(
        "ver_orcamento.html",
        orc=orc, massas=massas, colas=colas, terra=terra, extras=extras
    )

@app.route("/emitir_orcamento", methods=["POST"])
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
def inicio():
    return render_template("inicio.html", titulo_pagina="Início")


@app.route("/clientes", methods=["GET", "POST"])
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
                    cursor.execute("DELETE FROM clientes WHERE id = ?", (deletar_id,))
                    banco.commit()
                    mensagem = "Cliente deletado com sucesso!"
                except Exception as e:
                    mensagem = f"Erro ao deletar cliente: {str(e)}"
                finally:
                    banco.close()
            else:
                mensagem = "Senha incorreta para deletar cliente."
        # Cadastro de cliente
        # else:
        #     id = request.form.get("id", "").strip()
        #     nome = request.form.get("nome", "").strip()
        #     sobrenome = request.form.get("sobrenome", "").strip()
        #     empresa = request.form.get("empresa", "").strip()
        #     cnpj = request.form.get("cnpj", "").strip()
        #     celular1 = request.form.get("celular1", "").strip()
        #     celular2 = request.form.get("celular2", "").strip()
        #     email = request.form.get("email", "").strip()
        #     tipo = request.form.get("tipo", "").strip()
        #     endereco = request.form.get("endereco", "").strip()
        #     cidade = request.form.get("cidade", "").strip()
        #     estado = request.form.get("estado", "").strip()
        #     cep = request.form.get("cep", "").strip()
        #     observacoes = request.form.get("observacoes", "").strip()

        #     if nome and celular1 and email:
        #         try:
        #             banco = sqlite3.connect('clientes.db')
        #             cursor = banco.cursor()
        #             cursor.execute("""
        #                 CREATE TABLE IF NOT EXISTS clientes (
        #                     id INTEGER PRIMARY KEY AUTOINCREMENT,
        #                     nome TEXT NOT NULL,
        #                     sobrenome TEXT,
        #                     empresa TEXT,
        #                     cnpj TEXT,
        #                     celular1 TEXT,
        #                     celular2 TEXT,
        #                     email TEXT,
        #                     tipo TEXT,
        #                     endereco TEXT,
        #                     cidade TEXT,
        #                     estado TEXT,
        #                     cep TEXT,
        #                     observacoes TEXT
        #                 )
        #             """)
        #             cursor.execute("""
        #                 INSERT INTO clientes (
        #                     nome, sobrenome, empresa, cnpj, celular1, celular2, email, tipo,
        #                     endereco, cidade, estado, cep, observacoes
        #                 ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        #             """, (
        #                 nome, sobrenome, empresa, cnpj, celular1, celular2, email, tipo,
        #                 endereco, cidade, estado, cep, observacoes
        #             ))
        #             banco.commit()
        #             mensagem = "Cliente cadastrado com sucesso!"
        #         except Exception as e:
        #             mensagem = f"Erro ao cadastrar cliente: {str(e)}"
        #         finally:
        #             banco.close()
        #     else:
        #         mensagem = "Preencha os campos obrigatórios: Nome, Celular1 e Email."

        # # Redireciona para GET para evitar reenvio no F5
        # return redirect(url_for("clientes", mensagem=mensagem))

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
def exemplo():
    return render_template("exemplo.html")

if __name__ == "__main__":
    app.run(debug=True)
