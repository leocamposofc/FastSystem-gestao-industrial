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
        .massa-bloco {
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
            width: 95%;
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
        .divisor {
        border: none;
        border-top: 2px solid #ccc;
        margin: 25px 0;
        width: 100%;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Calculadora de Capeamento de Asfalto</h2>
        <h3>MASSA ASFALTICA</h3>
        <form method="post" id="form-massa">
            <div id="massa-container">
                <div id="massa-lista">
                    <div class="massa-bloco">
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
                        <input type="number" step="any" value="{{ preco_massa }}" name="preco_massa[]" required><br>
                        Margem de perda/compactação (%):
                        <input type="number" step="any" name="perda[]" value="{{ perda }}" required><br>
                        Frete (por viagem(20t)):
                        <input type="number" step="any" name="frete[]" required><br>
                    </div>
                </div>
                <p><strong>Total das massas: R$ <span id="custo-total">0</span></strong></p>

                <button type="button" class="add-camada-btn" id="add-camada">+ Adicionar camada de massa</button>
            </div>
            <hr class="divisor">
            
            
            <!-- INICIO DO CODIGO IMPRIMAÇÃO -->
            <h3>IMPRIMAÇÂO</h3>
            <div id="cola-lista">
                <div class="massa-bloco">
                    <div class="tipo-cola">
                        <label>Tipo de cola:</label><br>
                        <input type="radio" id="cm-30-1" name="tipo_cola[]" value="CM-30" required>
                        <label for="cm-30-1" class="btn-radio">CM-30</label>
                        <input type="radio" id="RR-2C-1" name="tipo_cola[]" value="RR-2C">
                        <label for="RR-2C-1" class="btn-radio">RR-2C</label>
                    </div>
                    Metragem (m²):
                    <input type="number" step="any" name="metragem_cola[]" required><br>
                    Litro por metro (L/m²):
                    <input type="number" step="any" name="litro_m[]" required><br>
                    litros por tonel:
                    <input type="number" step="any" name="litro_tonel[]" value="{{ litro_tonel }}" required><br>
                    Preço do tonel:
                    <input type="number" step="any" value="{{ preco_tonel }}" name="preco_tonel[]" value="{{ preco_tonel }}" required><br>
                    Margem de perda (%):
                    <input type="number" step="any" name="perda[]" value="{{ perda }}" required><br>
                    Frete (por tonel):
                    <input type="number" step="any" name="frete_tonel[]" value="{{ frete_tonel }}" required><br>
                </div>
                <p><strong>Total das imprimações: R$ <span id="custo-total-cola">0</span></strong></p>

                <button type="button" class="add-camada-btn" id="add-camada-cola">+ Adicionar camada de imprimação</button>

            </div>





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
// variavel massa
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
        const perda = parseFloat(camada.querySelector('input[name="perda[]"]').value) || 0;

        // cálculo da massa em toneladas (com perda)
        const toneladasBase = metragem * (espessura / 100) * densidade;
        const toneladas = toneladasBase * (1 + perda / 100);
        const custoCamada = toneladas * preco + frete;

        // mostra quantidade de massa e custo dentro da camada
        let pCusto = camada.querySelector('.custo-camada');
        if(!pCusto) {
            pCusto = document.createElement('p');
            pCusto.classList.add('custo-camada');
            camada.appendChild(pCusto);
        }
        pCusto.textContent = `
        Massa necessária: ${toneladas.toFixed(2)} t (com ${perda}% de perda) | 
        Custo desta camada: R$ ${custoCamada.toFixed(2)}
`;


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
        <input type="number" step="any" name="preco_massa[]" value="{{ preco_massa }}" required><br>
        Margem de perda/compactação (%):
        <input type="number" step="any" name="perda[]" value="{{ perda }}" required><br>
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

// INICIO SESSAO DA PARTE IMPRIMAÇÃO  
// ===============================
// Funções da COLA
// ===============================

// variavel cola
let contadorCamadasCola = 1;
const lista_cola = document.getElementById('cola-lista');
const addBtn_cola = document.getElementById('add-camada-cola');
// Função para recalcular custo de colas
function calcularCustoCola() {
    let custoTotalCola = 0;
    const camadasCola = document.querySelectorAll('.cola-bloco');

    camadasCola.forEach(camada => {
        const metragem = parseFloat(camada.querySelector('input[name="metragem_cola[]"]').value) || 0;
        const litro_m = parseFloat(camada.querySelector('input[name="litro_m[]"]').value) || 0;
        const litro_tonel = parseFloat(camada.querySelector('input[name="litro_tonel[]"]').value) || 0;
        const preco_tonel = parseFloat(camada.querySelector('input[name="preco_tonel[]"]').value) || 0;
        const perda = parseFloat(camada.querySelector('input[name="perda[]"]').value) || 0;
        const frete_tonel = parseFloat(camada.querySelector('input[name="frete_tonel[]"]').value) || 0;

        // 🔹 Cálculo da quantidade de cola necessária (em litros)
        const litrosBase = metragem * litro_m;
        const litrosComPerda = litrosBase * (1 + perda / 100);

        // 🔹 Quantidade de tonéis necessários
        const toneladas = litrosComPerda / litro_tonel;

        // 🔹 Cálculo do custo total da cola
        const custoCamada = toneladas * preco_tonel + frete_tonel;

        // 🔹 Mostrar resultado dentro da camada
        let pCusto = camada.querySelector('.custo-camada-cola');
        if (!pCusto) {
            pCusto = document.createElement('p');
            pCusto.classList.add('custo-camada-cola');
            camada.appendChild(pCusto);
        }
        pCusto.textContent = `
        Cola necessária: ${litrosComPerda.toFixed(2)} L (${toneladas.toFixed(2)} tonéis) | 
        Custo desta camada: R$ ${custoCamada.toFixed(2)}
        `;

        custoTotalCola += custoCamada;
    });

    // 🔹 Atualiza o custo total da seção de colas
    const totalSpanCola = document.getElementById('custo-total-cola');
    if (totalSpanCola) {
        totalSpanCola.textContent = custoTotalCola.toFixed(2);
    }
}

// Recalcular sempre que algum input mudar
lista_cola.addEventListener('input', calcularCustoCola);

// Adicionar nova camada de cola
addBtn_cola.addEventListener('click', () => {
    contadorCamadasCola++;
    const novaCamadaCola = document.createElement('div');
    novaCamadaCola.classList.add('cola-bloco');
    novaCamadaCola.innerHTML = `
        <h3>Cola ${contadorCamadasCola}</h3>
        Tipo de cola:<br>
        <input type="radio" id="cm30_${contadorCamadasCola}" name="tipo_cola_${contadorCamadasCola}" value="CM-30" required>
        <label for="cm30_${contadorCamadasCola}" class="btn-radio">CM-30</label>
        <input type="radio" id="rr2_${contadorCamadasCola}" name="tipo_cola_${contadorCamadasCola}" value="RR-2C">
        <label for="rr2_${contadorCamadasCola}" class="btn-radio">RR-2C</label><br>

        Metragem (m²):
        <input type="number" step="any" name="metragem_cola[]" required><br>
        Litro por metro (L/m²):
        <input type="number" step="any" name="litro_m[]" required><br>
        Litros por tonel:
        <input type="number" step="any" name="litro_tonel[]" required><br>
        Preço do tonel (R$):
        <input type="number" step="any" name="preco_tonel[]" required><br>
        Margem de perda (%):
        <input type="number" step="any" name="perda[]" required><br>
        Frete (por tonel):
        <input type="number" step="any" name="frete_tonel[]" required><br>

        <button type="button" class="remove-btn">Remover camada</button>
    `;
    lista_cola.appendChild(novaCamadaCola);

    // Remover camada
    novaCamadaCola.querySelector('.remove-btn').addEventListener('click', () => {
        novaCamadaCola.remove();
        calcularCustoCola();
        contadorCamadasCola--;
    });
});

</script>

</body>
</html>
"""
