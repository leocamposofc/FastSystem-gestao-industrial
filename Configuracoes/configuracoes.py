# Variáveis de configuração (consultadas pelo sistema)
densidade_asfalto = 0.0     # em kg/m³
preco_asfalto_por_tonelada = 0.0  # em R$
fator_perda = 0.0           # percentual de perda (%)
fator_compactacao = 0.0     # percentual de compactação (%)
litros_por_tonel = 200       # quantidade de litros que um tonel de cola tem
preco_tonel = 1300         # em R$ (preço padrão do tonel de cola)
frete_tonel = 2000         # em R$ (frete padrão por tonel)

# Custos adicionais (consultados pelo sistema)
custo_mao_obra = 100.0     # em R$
custo_transporte = 0.0      # em R$
custo_locacao_rolo = 1300.0    # em R$ (valor da locação do rolo)
custo_caminhao_cacamba = 2000.0  # em R$ (valor do custo do caminhão caçamba)
custo_pavimentadora = 2000.0     # em R$ (valor do custo da pavimentadora)
custo_sinalizacao = 0.0       # em R$ (valor do custo da sinalização)
custo_outros = 0.0            # em R$ (outros custos)
preco_massa = 660  # em R$ (preço padrão da massa asfáltica por tonelada)
margem_perda = 10.0  # em % (margem padrão de perda/compactação)

# Resultados do cálculo (inicializados)
volume_total = 0.0          # em m³
massa_total = 0.0           # em toneladas
custo_total = 0.0           # em R$

# Configurações do desenvolvedor
nome_empresa = "Camp's serviços"
slogan_empresa = "Solidez e experiencia em cada metro de asfalto."
site_empresa = "www.campsservicos.com.br"
email_empresa = "campsservicos@gmail.com"
validade_orcamento_dias = 15  # validade do orçamento em dias
senha_de_seguranca = "camps123"  # senha de segurança para deletar clientes no db
versao_sistema = "1.5-beta"
nome_sistema = "FastSystem - Gestão Industrial"
