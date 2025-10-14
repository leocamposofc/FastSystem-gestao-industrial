HTML = """
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