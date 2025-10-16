HTML = """<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Cotador de Capeamento de Asfalto</title>
<style>
    :root{
        --card-bg: #ffffff;
        --card-alt: #fbfcfd;
        --accent: #007bff;
        --good: #28a745;
        --danger: #e04f4f;
        --muted: #6c757d;
    }

    body {
        font-family: Inter, Arial, sans-serif;
        background: #f4f6f8;
        margin: 0;
        padding: 20px;
        color: #222;
    }

    .container {
        max-width: 960px;
        margin: 24px auto;
        background: #fff;
        padding: 26px;
        border-radius: 10px;
        box-shadow: 0 6px 18px rgba(42, 57, 78, 0.08);
    }

    h2 {
        margin: 0 0 12px;
        font-size: 22px;
        text-align: center;
    }

    h3.section-title {
        margin: 18px 0 12px;
        font-size: 18px;
        color: var(--muted);
        text-align: left;
    }

    .massa-bloco, .cola-bloco {
        border: 1px solid #e6e9ee;
        padding: 14px;
        border-radius: 8px;
        margin-bottom: 12px;
        box-sizing: border-box;
    }
    /* fundo alternado para facilitar leitura */
    .massa-bloco:nth-child(even),
    .cola-bloco:nth-child(even) {
        background: var(--card-alt);
    }

    .row {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        align-items: center;
    }
    .field {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin-bottom: 8px;
    }

    /* label compacto */
    .field label {
        font-size: 13px;
        color: #444;
    }

    /* inputs com largura controlada */
    input[type="number"], input[type="text"], select {
        padding: 8px 10px;
        border-radius: 6px;
        border: 1px solid #d0d7df;
        min-width: 150px;
        width: 220px;
    }

    /* quando precisar expandir largura */
    .field.full input,
    .field.full select {
        width: 100%;
        min-width: 0;
    }

    .controls {
        margin-top: 12px;
    }

    button {
        padding: 9px 14px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        font-weight: 600;
        box-shadow: 0 2px 6px rgba(16,24,40,0.04);
    }
    .add-camada-btn {
        background-color: var(--good);
        color: #fff;
    }
    .remove-btn {
        background: var(--danger);
        color: #fff;
    }
    .btn-radio {
        display: inline-block;
        padding: 6px 12px;
        margin-right: 8px;
        border: 1px solid var(--accent);
        border-radius: 8px;
        cursor: pointer;
        color: var(--accent);
        font-size: 13px;
    }
    input[type="radio"] { display:none; }
    input[type="radio"]:checked + .btn-radio {
        background: var(--accent);
        color: #fff;
    }

    .divisor {
        border: none;
        border-top: 1px solid #e6e9ee;
        margin: 18px 0;
    }

    .custo-camada, .custo-camada-cola {
        margin-top: 10px;
        padding: 8px 10px;
        border-radius: 8px;
        background: #f1f8f5;
        border: 1px solid #d7efe0;
        color: #134e3a;
        font-size: 13px;
        line-height: 1.3;
        word-break: break-word;
    }

    .summary {
        margin-top: 12px;
        font-size: 15px;
    }

    /* responsivo */
    @media (max-width:720px){
        .row { flex-direction: column; }
        input[type="number"], input[type="text"], select { width: 100%; }
    }
</style>
</head>
<body>
<div class="container">
    <h2>Calculadora de Capeamento de Asfalto</h2>

    <!-- MASSA -->
    <h3 class="section-title">MASSA ASFÁLTICA</h3>
    <div id="massa-lista">
        <div class="massa-bloco">
            <h4>Camada 1</h4>

            <div class="row">
                <div class="field">
                    <label>Tipo de massa</label>
                    <div>
                        <input type="radio" id="binder1"  name="tipo_massa_1" value="binder" required>
                        <label for="binder1" class="btn-radio">Binder</label>

                        <input type="radio" id="cbuq1" name="tipo_massa_1" value="cbuq">
                        <label for="cbuq1" class="btn-radio">CBUQ</label>

                        <input type="radio" id="brita1" name="tipo_massa_1" value="brita">
                        <label for="brita1" class="btn-radio">Brita</label>
                    </div>
                </div>

                <div class="field">
                    <label>Metragem (m²)</label>
                    <input type="number" step="any" name="metragem[]" placeholder="ex: 1000" required>
                </div>

                <div class="field">
                    <label>Espessura (cm)</label>
                    <input type="number" step="any" name="expessura[]" placeholder="ex: 4" required>
                </div>

                <div class="field">
                    <label>Densidade (t/m³)</label>
                    <input type="number" step="any" name="densidade[]" placeholder="ex: 2.4" required>
                </div>
            </div>

            <div class="row">
                <div class="field">
                    <label>Preço da massa (R$/t)</label>
                    <input type="number" step="any" name="preco_massa[]" placeholder="ex: 250" required>
                </div>
                <div class="field">
                    <label>Margem de perda/compactação (%)</label>
                    <input type="number" step="any" name="perda[]" value="7" required>
                </div>
                <div class="field">
                    <label>Frete (por viagem 20t)</label>
                    <input type="number" step="any" name="frete[]" placeholder="ex: 350" required>
                </div>
            </div>
        </div>
    </div>

    <div class="summary">
        <strong>Total das massas: R$ <span id="custo-total">0.00</span></strong>
    </div>
    <div class="controls">
        <button type="button" id="add-camada" class="add-camada-btn">+ Adicionar camada de massa</button>
    </div>

    <hr class="divisor">

    <!-- IMPRIMAÇÃO / COLA -->
    <h3 class="section-title">IMPRIMAÇÃO (COLA)</h3>
    <div id="cola-lista">
        <div class="massa-bloco cola-bloco">
            <h4>Imprimação 1</h4>

            <div class="row">
                <div class="field">
                    <label>Tipo de cola</label>
                    <div>
                        <input type="radio" id="cm30_1" name="tipo_cola_1" value="CM-30" required>
                        <label for="cm30_1" class="btn-radio">CM-30</label>

                        <input type="radio" id="rr2_1" name="tipo_cola_1" value="RR-2C">
                        <label for="rr2_1" class="btn-radio">RR-2C</label>
                    </div>
                </div>

                <div class="field">
                    <label>Metragem (m²)</label>
                    <input type="number" step="any" name="metragem_cola[]" placeholder="ex: 1000" required>
                </div>

                <div class="field">
                    <label>Litro por metro (L/m²)</label>
                    <input type="number" step="any" name="litro_m[]" placeholder="ex: 0.5" required>
                </div>

                <div class="field">
                    <label>Litros por tonel</label>
                    <input type="number" step="any" name="litro_tonel[]" placeholder="ex: 1000" required>
                </div>
            </div>

            <div class="row">
                <div class="field">
                    <label>Preço do tonel (R$)</label>
                    <input type="number" step="any" name="preco_tonel[]" placeholder="ex: 1200" required>
                </div>

                <div class="field">
                    <label>Margem de perda (%)</label>
                    <input type="number" step="any" name="perda[]" value="7" required>
                </div>

                <div class="field">
                    <label>Frete (por tonel)</label>
                    <input type="number" step="any" name="frete_tonel[]" placeholder="ex: 80" required>
                </div>
            </div>
        </div>
    </div>

    <div class="summary">
        <strong>Total das imprimações: R$ <span id="custo-total-cola">0.00</span></strong>
    </div>
    <div class="controls">
        <button type="button" id="add-camada-cola" class="add-camada-btn">+ Adicionar camada de imprimação</button>
    </div>

    <hr class="divisor">

    <div class="summary">
        <strong>Total Geral (Massas + Colas): R$ <span id="custo-total-geral">0.00</span></strong>
    </div>

</div>

<script>
document.addEventListener("DOMContentLoaded", () => {
    // ======= MASSA =======
    let contadorCamadas = 1;
    const lista = document.getElementById('massa-lista');
    const addBtn = document.getElementById('add-camada');

    function calcularCusto() {
        let total = 0;
        document.querySelectorAll('#massa-lista .massa-bloco').forEach(camada => {
            const m = parseFloat(camada.querySelector('[name="metragem[]"]').value) || 0;
            const e = parseFloat(camada.querySelector('[name="expessura[]"]').value) || 0;
            const d = parseFloat(camada.querySelector('[name="densidade[]"]').value) || 0;
            const p = parseFloat(camada.querySelector('[name="preco_massa[]"]').value) || 0;
            const f = parseFloat(camada.querySelector('[name="frete[]"]').value) || 0;
            const perda = parseFloat(camada.querySelector('[name="perda[]"]').value) || 0;

            // toneladas considerando densidade em t/m³ e margem de perda
            const toneladasBase = m * (e / 100) * d;
            const toneladas = toneladasBase * (1 + perda / 100);
            const custo = toneladas * p + f; // frete considerado por viagem (valor absoluto)
            total += custo;

            let pc = camada.querySelector('.custo-camada');
            if(!pc){
                pc = document.createElement('p');
                pc.className = 'custo-camada';
                camada.appendChild(pc);
            }
            pc.textContent = `Massa necessária: ${toneladas.toFixed(2)} t (teórica ${toneladasBase.toFixed(2)} t) | Custo: R$ ${custo.toFixed(2)}`;
        });
        document.getElementById('custo-total').textContent = total.toFixed(2);
        atualizarTotalGeral();
    }

    lista.addEventListener('input', calcularCusto);

    addBtn.addEventListener('click', () => {
        contadorCamadas++;
        const nova = document.createElement('div');
        nova.className = 'massa-bloco';
        nova.innerHTML = `
            <h4>Camada ${contadorCamadas}</h4>
            <div class="row">
                <div class="field">
                    <label>Tipo de massa</label>
                    <div>
                        <input type="radio" id="binder${contadorCamadas}" name="tipo_massa_${contadorCamadas}" value="binder" required>
                        <label for="binder${contadorCamadas}" class="btn-radio">Binder</label>
                        <input type="radio" id="cbuq${contadorCamadas}" name="tipo_massa_${contadorCamadas}" value="cbuq">
                        <label for="cbuq${contadorCamadas}" class="btn-radio">CBUQ</label>
                        <input type="radio" id="brita${contadorCamadas}" name="tipo_massa_${contadorCamadas}" value="brita">
                        <label for="brita${contadorCamadas}" class="btn-radio">Brita</label>
                    </div>
                </div>

                <div class="field">
                    <label>Metragem (m²)</label>
                    <input type="number" step="any" name="metragem[]" required>
                </div>

                <div class="field">
                    <label>Espessura (cm)</label>
                    <input type="number" step="any" name="expessura[]" required>
                </div>

                <div class="field">
                    <label>Densidade (t/m³)</label>
                    <input type="number" step="any" name="densidade[]" required>
                </div>
            </div>

            <div class="row">
                <div class="field">
                    <label>Preço da massa (R$/t)</label>
                    <input type="number" step="any" name="preco_massa[]" required>
                </div>
                <div class="field">
                    <label>Margem de perda/compactação (%)</label>
                    <input type="number" step="any" name="perda[]" value="7" required>
                </div>
                <div class="field">
                    <label>Frete (por viagem 20t)</label>
                    <input type="number" step="any" name="frete[]" required>
                </div>
            </div>

            <button type="button" class="remove-btn">Remover camada</button>
        `;
        lista.appendChild(nova);

        // remover -> apenas remove o bloco e recalcula
        nova.querySelector('.remove-btn').addEventListener('click', () => {
            nova.remove();
            calcularCusto();
        });

        // inicializa recálculo (campos vazios não quebram)
        calcularCusto();
    });

    // ======= COLA / IMPRIMAÇÃO =======
    let contadorCola = 1;
    const listaCola = document.getElementById('cola-lista');
    const addCola = document.getElementById('add-camada-cola');

    function calcularCustoCola() {
        let total = 0;
        document.querySelectorAll('#cola-lista .cola-bloco').forEach(camada => {
            const m = parseFloat(camada.querySelector('[name="metragem_cola[]"]').value) || 0;
            const lm = parseFloat(camada.querySelector('[name="litro_m[]"]').value) || 0;
            const lt = parseFloat(camada.querySelector('[name="litro_tonel[]"]').value) || 0;
            const pt = parseFloat(camada.querySelector('[name="preco_tonel[]"]').value) || 0;
            const perda = parseFloat(camada.querySelector('[name="perda[]"]').value) || 0;
            const frete_tonel = parseFloat(camada.querySelector('[name="frete_tonel[]"]').value) || 0;

            // litros necessários (com perda)
            const litrosBase = m * lm;
            const litrosComPerda = litrosBase * (1 + perda / 100);

            // tonelagens necessárias (litros / litros por tonel)
            const toneladas = lt > 0 ? (litrosComPerda / lt) : 0;

            // CUSTO: preço por tonel + frete por tonel (ambos por tonel)
            const custo = toneladas * (pt + frete_tonel);
            total += custo;

            let pc = camada.querySelector('.custo-camada-cola');
            if(!pc){
                pc = document.createElement('p');
                pc.className = 'custo-camada-cola';
                camada.appendChild(pc);
            }
            pc.textContent = `Cola necessária: ${litrosComPerda.toFixed(2)} L (${toneladas.toFixed(2)} tonéis) | Custo: R$ ${custo.toFixed(2)}`;
        });
        document.getElementById('custo-total-cola').textContent = total.toFixed(2);
        atualizarTotalGeral();
    }

    listaCola.addEventListener('input', calcularCustoCola);

    addCola.addEventListener('click', () => {
        contadorCola++;
        const nova = document.createElement('div');
        nova.className = 'massa-bloco cola-bloco';
        nova.innerHTML = `
            <h4>Imprimação ${contadorCola}</h4>

            <div class="row">
                <div class="field">
                    <label>Tipo de cola</label>
                    <div>
                        <input type="radio" id="cm30_${contadorCola}" name="tipo_cola_${contadorCola}" value="CM-30" required>
                        <label for="cm30_${contadorCola}" class="btn-radio">CM-30</label>
                        <input type="radio" id="rr2_${contadorCola}" name="tipo_cola_${contadorCola}" value="RR-2C">
                        <label for="rr2_${contadorCola}" class="btn-radio">RR-2C</label>
                    </div>
                </div>

                <div class="field">
                    <label>Metragem (m²)</label>
                    <input type="number" step="any" name="metragem_cola[]" required>
                </div>

                <div class="field">
                    <label>Litro por metro (L/m²)</label>
                    <input type="number" step="any" name="litro_m[]" required>
                </div>

                <div class="field">
                    <label>Litros por tonel</label>
                    <input type="number" step="any" name="litro_tonel[]" required>
                </div>
            </div>

            <div class="row">
                <div class="field">
                    <label>Preço do tonel (R$)</label>
                    <input type="number" step="any" name="preco_tonel[]" required>
                </div>

                <div class="field">
                    <label>Margem de perda (%)</label>
                    <input type="number" step="any" name="perda[]" value="7" required>
                </div>

                <div class="field">
                    <label>Frete (por tonel)</label>
                    <input type="number" step="any" name="frete_tonel[]" required>
                </div>
            </div>

            <button type="button" class="remove-btn">Remover camada</button>
        `;
        listaCola.appendChild(nova);

        nova.querySelector('.remove-btn').addEventListener('click', () => {
            nova.remove();
            calcularCustoCola();
        });

        calcularCustoCola();
    });

    // Calcula total geral (massas + colas)
    function atualizarTotalGeral(){
        const tMassas = parseFloat(document.getElementById('custo-total').textContent) || 0;
        const tColas = parseFloat(document.getElementById('custo-total-cola').textContent) || 0;
        document.getElementById('custo-total-geral').textContent = (tMassas + tColas).toFixed(2);
    }

    // inicializa
    calcularCusto();
    calcularCustoCola();
});
</script>
</body>
</html>
"""