import requests

cep = '08021-570'
site = f'https://viacep.com.br/ws/{cep}/json/'
resposta = requests.get(site)
dados_cep = resposta.json()
# print(dados_cep)
rua = {dados_cep['logradouro']}
cidade = {dados_cep['localidade']}
estado = {dados_cep['estado']}
print(rua)