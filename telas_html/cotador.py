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
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 10px;
            margin-top: 10px;
        }
        button:hover {
            opacity: 0.9;
        }
        .add-camada-btn {
            background-color: #28a745;
            color: #fff;
        }
        .msg {
            color: green;
        }
        .erro {
            color: red;
        }
        .massa-bloco {
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
            background: #fafafa;
        }
        .remove-btn {
            background: #e04f4f;
        }
        .remove-btn:hover {
            background: #b93434;
        }
        .tipo-massa {
            margin-bottom: 10px;
        }
        .btn-radio {
            display: inline-block;
            padding: 6px 15px;
            margin-right: 10px;
            border: 1px solid #007bff;
            border-radius: 5px;
            cursor: pointer;
            background-color: #fff;
            color: #007bff;
            transition: 0.2s;
        }
        input[type="radio"] {
            display: none; /* esconde o radio padrão */
        }
        input[type="radio"]:checked + .btn-radio {
            background-color: #007bff;
            color: #fff;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Calculadora de Capeamento de Asfalto</h2>
        <form method="post" id="form-massa">
            <div id="massa-container">
                <div id="massa-lista">
                    <div class="massa-bloco"
                        <h3>Camada 1</h3>
                        <div class="tipo-massa">
                            <label>Tipo de massa:</label><br>
                            <input type="radio" id="binder1" name="tipo_massa[]" value="binder" required>
                            <label for="binder1" class="btn-radio">Binder</label>
                            <input type="radio" id="cbuq1" name="tipo_massa[]" value="cbuq">
                            <label for="cbuq1" class="btn-radio">CBUQ</label>
                            <input type="radio" id="brita1" name="tipo_massa[]" value="brita">
                            <label for="brita1" class="btn-radio">Brita</label>
                        </div>
                        Metragem (m²):
                        <input type="number" step="any" name="metragem[]" required><br>
                        Espessura (cm):
                        <input type="number" step="any" name="expessura[]" required><br>
                        Densidade (t/m³):
                        <input type="number" step="any" name="densidade[]" required><br>
                        Preço da massa (R$/t):
                        <input type="number" step="any" name="preco_massa[]" required><br>
                        Frete (por viagem(20t)):
                        <input type="number" step="any" name="frete[]" required><br>
                    </div>
                </div>
                <p><strong>Total das massas: R$ <span id="custo-total">0</span></strong></p>
            </div>

            <button type="button" class="add-camada-btn" id="add-camada">+ Adicionar camada</button>

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

    <script>
let contadorCamadas = 1;
const lista = document.getElementById('massa-lista');
const addBtn = document.getElementById('add-camada');

// Função para recalcular custos e quantidade de massa
function calcularCusto() {
    let custoTotal = 0;
    const camadas = document.querySelectorAll('.massa-bloco');

    camadas.forEach(camada => {
        const metragem = parseFloat(camada.querySelector('input[name="metragem[]"]').value) || 0;
        const espessura = parseFloat(camada.querySelector('input[name="expessura[]"]').value) || 0;
        const densidade = parseFloat(camada.querySelector('input[name="densidade[]"]').value) || 0;
        const preco = parseFloat(camada.querySelector('input[name="preco_massa[]"]').value) || 0;
        const frete = parseFloat(camada.querySelector('input[name="frete[]"]').value) || 0;

        // cálculo da massa em toneladas
        const toneladas = metragem * (espessura / 100) * densidade;
        const custoCamada = toneladas * preco + frete;

        // mostra quantidade de massa e custo dentro da camada
        let pCusto = camada.querySelector('.custo-camada');
        if(!pCusto) {
            pCusto = document.createElement('p');
            pCusto.classList.add('custo-camada');
            camada.appendChild(pCusto);
        }
        pCusto.textContent = `Massa necessária: ${toneladas.toFixed(2)} t | Custo desta camada: R$ ${custoCamada.toFixed(2)}`;

        // adiciona ao total
        custoTotal += custoCamada;
    });

    // mostra total geral
    const totalSpan = document.getElementById('custo-total');
    if(totalSpan) {
        totalSpan.textContent = custoTotal.toFixed(2);
    }
}

// recalcular sempre que qualquer input mudar
lista.addEventListener('input', calcularCusto);

// Adicionar nova camada
addBtn.addEventListener('click', () => {
    contadorCamadas++;
    const novaCamada = document.createElement('div');
    novaCamada.classList.add('massa-bloco');
    novaCamada.innerHTML = `
        <h3>Camada ${contadorCamadas}</h3>
        <div class="tipo-massa">
            <label>Tipo de massa:</label><br>
            <input type="radio" id="binder${contadorCamadas}" name="tipo_massa[]" value="binder" required>
            <label for="binder${contadorCamadas}" class="btn-radio">Binder</label>
            <input type="radio" id="cbuq${contadorCamadas}" name="tipo_massa[]" value="cbuq">
            <label for="cbuq${contadorCamadas}" class="btn-radio">CBUQ</label>
            <input type="radio" id="brita${contadorCamadas}" name="tipo_massa[]" value="brita">
            <label for="brita${contadorCamadas}" class="btn-radio">Brita</label>
        </div>
        Metragem (m²):
        <input type="number" step="any" name="metragem[]" required><br>
        Espessura (cm):
        <input type="number" step="any" name="expessura[]" required><br>
        Densidade (t/m³):
        <input type="number" step="any" name="densidade[]" required><br>
        Preço da massa (R$/t):
        <input type="number" step="any" name="preco_massa[]" required><br>
        Frete (por viagem(20t)):
        <input type="number" step="any" name="frete[]" required><br>
        <button type="button" class="remove-btn">Remover camada</button>
    `;
    lista.appendChild(novaCamada);

    // remover camada
    novaCamada.querySelector('.remove-btn').addEventListener('click', () => {
        novaCamada.remove();
        calcularCusto(); // recalcula após remoção
        contadorCamadas--;
    });
});
</script>

</body>
</html>
"""
