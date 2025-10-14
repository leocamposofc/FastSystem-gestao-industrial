from datetime import datetime
from flask import Flask, render_template_string, request, send_file
from Configuracoes import configuracoes
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import sqlite3
from telas 

app = Flask(__name__)


def calcular_custo(metragem, espessura_cm, preco_por_m3=250):
    volume_m3 = metragem * (espessura_cm / 100)
    custo_estimado = volume_m3 * preco_por_m3
    return custo_estimado


HTML = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Cotador de Capeamento de Asfalto</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f4f4;
        }
        .container {
            max-width: 900px;
            margin: 40px auto;
            background: #fff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px #ccc;
        }
        h2 {
            text-align: center;
            margin-bottom: 20px;
        }
        form {
            margin-bottom: 30px;
        }
        input, select, textarea {
            width: 100%;
            padding: 8px;
            margin: 6px 0;
            border-radius: 4px;
            border: 1px solid #ccc;
        }
        fieldset {
            margin-top: 15px;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #ccc;
            background: #fafafa;
        }
        legend {
            font-weight: bold;
        }
        input[type="checkbox"] {
            width: auto;
            margin-right: 6px;
        }
        button {
            padding: 10px 20px;
            background: #007bff;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 10px;
            margin-top: 10px;
        }
        button:hover {
            background: #0056b3;
        }
        p {
            font-size: 15px;
        }
        .msg {
            color: green;
        }
        .erro {
            color: red;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Calculadora de Capeamento de Asfalto</h2>
        <form method="post">
            Metragem (m²):
            <input type="number" step="any" name="metragem" required><br>
            
            Espessura da massa (cm):
            <input type="number" step="any" name="espessura_cm" required><br>
            
            <fieldset>
                <legend>Selecione o que será necessário na obra:</legend>
                <label><input type="checkbox" name="equipamentos" value="rolo_compactor"> Rolo Compactador (R$ {{ preco_rolo }})</label><br>
                <label><input type="checkbox" name="equipamentos" value="pavimentadora"> Pavimentadora (R$ {{ preco_pavimentadora }})</label><br>
                <label><input type="checkbox" name="equipamentos" value="equipe_mao_obra"> Equipe de Mão de Obra (R$ {{ preco_mao_obra }})</label><br>
                <label><input type="checkbox" name="equipamentos" value="sinalizacao"> Sinalização de Segurança (R$ {{ preco_sinalizacao }})</label><br>
                <label><input type="checkbox" name="equipamentos" value="outros"> Outros (R$ {{ preco_outros }})</label><br>
            </fieldset>

            <button type="submit">Calcular</button>
            <button type="submit" formaction="/emitir_orcamento" formmethod="post">Emitir Orçamento PDF</button>
        </form>

        {% if custo is not none %}
            <p class="msg">Custo estimado: R$ {{ custo }}</p>
        {% endif %}
        {% if erro %}
            <p class="erro">{{ erro }}</p>
        {% endif %}
    </div>
</body>
</html>"""



@app.route("/cotador", methods=["GET", "POST"])
def index():
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
    return render_template_string(
        HTML,
        custo=custo,
        erro=erro,
        preco_rolo=precos["rolo_compactor"],
        preco_caminhao=precos["caminhao_caçamba"],
        preco_pavimentadora=precos["pavimentadora"],
        preco_mao_obra=precos["equipe_mao_obra"],
        preco_sinalizacao=precos["sinalizacao"],
        preco_outros=precos["outros"]
    )
# def main():
#     print("=== Calculadora de Capeamento de Asfalto ===")
#     try:
#         metragem = float(input("Digite a metragem (m²): "))
#         espessura_cm = float(input("Digite a espessura da massa (cm): "))
#         custo = calcular_custo(metragem, espessura_cm)
#         print(f"Custo estimado: R$ {custo:.2f}")
#     except ValueError:
#         print("Por favor, digite valores numéricos válidos.")

# if __name__ == "__main__":
#     main()


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
    html_inicio = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Início - Sistema de Asfalto</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f4f4; }
            .container { max-width: 400px; margin: 80px auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px #ccc; }
            h2 { text-align: center; margin-bottom: 30px; }
            .menu-btn { display: block; width: 100%; margin: 12px 0; padding: 12px; font-size: 16px; border: none; border-radius: 5px; background: #007bff; color: #fff; cursor: pointer; text-decoration: none; text-align: center; }
            .menu-btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>FastSystem</h2>
            <a href="/cotador" class="menu-btn">Cotador</a>
            <a href="/clientes" class="menu-btn">Clientes</a>
            <a href="/configuracoes" class="menu-btn">Configurações</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_inicio)


@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    erro = ""
    sucesso = ""
    clientes_lista = []
    # Deletar cliente se solicitado
    if request.method == "POST" and "deletar_id" in request.form:
        deletar_id = request.form.get("deletar_id")
        senha = request.form.get("senha_deletar", "")
        if senha == configuracoes.senha_de_seguranca:
            try:
                banco = sqlite3.connect('clientes.db')
                cursor = banco.cursor()
                cursor.execute(
                    "DELETE FROM clientes WHERE id = ?", (deletar_id,))
                banco.commit()
                sucesso = "Cliente deletado com sucesso!"
            except Exception as e:
                erro = f"Erro ao deletar cliente: {str(e)}"
            finally:
                banco.close()
        else:
            erro = "Senha incorreta para deletar cliente."
    # Cadastro de cliente
    elif request.method == "POST":
        nome = request.form.get("nome", "").strip()
        sobrenome = request.form.get("sobrenome", "").strip()
        empresa = request.form.get("empresa", "").strip()
        cnpj = request.form.get("cnpj", "").strip()
        celular1 = request.form.get("celular1", "").strip()
        celular2 = request.form.get("celular2", "").strip()
        email = request.form.get("email", "").strip()
        tipo = request.form.get("tipo", "").strip()
        endereco = request.form.get("endereco", "").strip()
        cidade = request.form.get("cidade", "").strip()
        estado = request.form.get("estado", "").strip()
        cep = request.form.get("cep", "").strip()
        observacoes = request.form.get("observacoes", "").strip()
        # Campos obrigatórios: nome, celular1, email
        if nome and celular1 and email:
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
                        cidade TEXT,
                        estado TEXT,
                        cep TEXT,
                        observacoes TEXT
                    )
                """)
                cursor.execute("""
                    INSERT INTO clientes (
                        nome, sobrenome, empresa, cnpj, celular1, celular2, email, tipo,
                        endereco, cidade, estado, cep, observacoes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    nome, sobrenome, empresa, cnpj, celular1, celular2, email, tipo,
                    endereco, cidade, estado, cep, observacoes
                ))
                banco.commit()
                sucesso = "Cliente cadastrado com sucesso!"
            except Exception as e:
                erro = f"Erro ao cadastrar cliente: {str(e)}"
            finally:
                banco.close()
        else:
            erro = "Preencha os campos obrigatórios: Nome, Celular1 e Email."
    # Buscar clientes do banco
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
        erro = f"Erro ao buscar clientes: {str(e)}"
    finally:
        banco.close()
    html_clientes = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Clientes</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f4f4; }
            .container { max-width: 900px; margin: 40px auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px #ccc; }
            h2 { text-align: center; margin-bottom: 20px; }
            form { margin-bottom: 30px; }
            input, select, textarea { width: 100%; padding: 8px; margin: 6px 0; border-radius: 4px; border: 1px solid #ccc; }
            button { padding: 10px 20px; background: #007bff; color: #fff; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .msg { color: green; }
            .erro { color: red; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background: #007bff; color: #fff; }
            .del-form { display:inline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Cadastro de Clientes</h2>
            <form method="post">
                Nome*: <input type="text" name="nome" required><br>
                Sobrenome: <input type="text" name="sobrenome"><br>
                Empresa: <input type="text" name="empresa"><br>
                CNPJ: <input type="text" name="cnpj"><br>
                Celular 1*: <input type="text" name="celular1" required><br>
                Celular 2: <input type="text" name="celular2"><br>
                Email*: <input type="email" name="email" required><br>
                Tipo: 
                <select name="tipo">
                    <option value="">Selecione</option>
                    <option value="cliente">Cliente</option>
                    <option value="fornecedor">Fornecedor</option>
                </select><br>
                Endereço: <input type="text" name="endereco"><br>
                Cidade: <input type="text" name="cidade"><br>
                Estado: <input type="text" name="estado"><br>
                CEP: <input type="text" name="cep"><br>
                Observações: <textarea name="observacoes"></textarea><br>
                <button type="submit">Cadastrar</button>
            </form>
            {% if sucesso %}
                <p class="msg">{{ sucesso }}</p>
            {% endif %}
            {% if erro %}
                <p class="erro">{{ erro }}</p>
            {% endif %}
            <h3>Lista de Clientes</h3>
            <table>
                <tr>
                    <th>Nome</th>
                    <th>Sobrenome</th>
                    <th>Empresa</th>
                    <th>CNPJ</th>
                    <th>Celular 1</th>
                    <th>Celular 2</th>
                    <th>Email</th>
                    <th>Tipo</th>
                    <th>Endereço</th>
                    <th>Cidade</th>
                    <th>Estado</th>
                    <th>CEP</th>
                    <th>Observações</th>
                    <th>Ações</th>
                </tr>
                {% for cliente in clientes %}
                <tr>
                    <td>{{ cliente.nome }}</td>
                    <td>{{ cliente.sobrenome }}</td>
                    <td>{{ cliente.empresa }}</td>
                    <td>{{ cliente.cnpj }}</td>
                    <td>{{ cliente.celular1 }}</td>
                    <td>{{ cliente.celular2 }}</td>
                    <td>{{ cliente.email }}</td>
                    <td>{{ cliente.tipo }}</td>
                    <td>{{ cliente.endereco }}</td>
                    <td>{{ cliente.cidade }}</td>
                    <td>{{ cliente.estado }}</td>
                    <td>{{ cliente.cep }}</td>
                    <td>{{ cliente.observacoes }}</td>
                    <td>
                        <form method="post" class="del-form" style="display:inline;">
                            <input type="hidden" name="deletar_id" value="{{ cliente.id }}">
                            <input type="password" name="senha_deletar" placeholder="Senha" required style="width:80px;">
                            <button type="submit" onclick="return confirm('Deseja realmente deletar este cliente?');">Deletar</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </table>
            <p style="font-size:12px;">* Campos obrigatórios</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(
        html_clientes,
        clientes=clientes_lista,
        erro=erro,
        sucesso=sucesso
    )


if __name__ == "__main__":
    app.run(debug=False)
