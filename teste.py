import sqlite3
# import requests

# cep = '08021-570'
# site = f'https://viacep.com.br/ws/{cep}/json/'
# resposta = requests.get(site)
# dados_cep = resposta.json()
# # print(dados_cep)
# rua = {dados_cep['logradouro']}
# cidade = {dados_cep['localidade']}
# estado = {dados_cep['estado']}
# print(rua)

id_orcamento= 12

conn = sqlite3.connect("orcamentos.db")
cur = conn.cursor()

# Info principal
cur.execute("SELECT * FROM orcamentos WHERE id=?", (id_orcamento,))
orc = cur.fetchone()

cur.execute("SELECT * FROM status WHERE id=?", (orc[5],))
status = cur.fetchone()

end=orc[8]
lat=orc[9]
long=orc[10]
comp=orc[11]


print(f"Orçamento ID:{id_orcamento}\nendereço: {end}\nlatitude: {lat}\nlongitude: {long}\ncomplemento: {comp}")
if status is not None:
    print(f"Status: {status[1]} - {status[2]}")
else:
    print("Status: Não encontrado")

