from flask import Flask, render_template, request, redirect, url_for, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
import sqlite3
import io
from datetime import datetime

app = Flask(__name__)
DB = "orcamentos.db"

# Criar o banco se não existir
def init_db():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            data TEXT,
            valor_total REAL,
            dados TEXT
        )
        """)
        con.commit()

init_db()

@app.route("/", methods=["GET", "POST"])
def orcamento():
    if request.method == "POST":
        cliente = request.form.get("cliente")
        valor_total = float(request.form.get("valor_total", 0))
        dados = str(dict(request.form))
        data = datetime.now().strftime("%d/%m/%Y")

        with sqlite3.connect(DB) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO orcamentos (cliente, data, valor_total, dados) VALUES (?, ?, ?, ?)",
                        (cliente, data, valor_total, dados))
            con.commit()

        return redirect(url_for("orcamentos"))

    return render_template("orcamento.html")

@app.route("/orcamentos")
def orcamentos():
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("SELECT id, cliente, data, valor_total FROM orcamentos ORDER BY id DESC")
        orcamentos = cur.fetchall()

    return render_template("orcamentos.html", orcamentos=orcamentos)

@app.route("/gerar_pdf/<int:id>")
def gerar_pdf(id):
    with sqlite3.connect(DB) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM orcamentos WHERE id=?", (id,))
        orc = cur.fetchone()

    if not orc:
        return "Orçamento não encontrado."

    id_, cliente, data, valor_total, dados = orc

    # Cria o PDF em memória
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    largura, altura = A4
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(2 * cm, altura - 2 * cm, "ORÇAMENTO DE SERVIÇOS DE PAVIMENTAÇÃO")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(2 * cm, altura - 3 * cm, f"Cliente: {cliente}")
    pdf.drawString(2 * cm, altura - 4 * cm, f"Data: {data}")
    pdf.drawString(2 * cm, altura - 5 * cm, f"Valor total: R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    pdf.setFont("Helvetica", 10)
    pdf.drawString(2 * cm, altura - 6.5 * cm, "Detalhes do orçamento:")
    texto = pdf.beginText(2 * cm, altura - 7.5 * cm)
    texto.textLines(dados)
    pdf.drawText(texto)

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return send_file(buffer,
                     as_attachment=True,
                     download_name=f"orcamento_{id_}.pdf",
                     mimetype="application/pdf")

if __name__ == "__main__":
    app.run(debug=True)
ç