import redis
import pymongo
import json
import time
from pymongo.server_api import ServerApi

# Conexão com o Redis
r = redis.Redis(
    host='redis-host-aqui',
    port=11111,
    password='senha-aqui'
)

# Conexão com o MongoDB
client = pymongo.MongoClient("mongodb+srv://user:senha-aqui", server_api=ServerApi('1'))
db = client.MercadoLivre
product_collection = db["Produto"]
vendor_collection = db["Vendedor"]
user_collection = db["Usuário"]

# Função para inserir um novo produto no Redis, alterar seus dados, manter a lógica do Fast Buy para um usuário, e remover um vendedor do MongoDB
def iniciarRedis():
    produto_nome = input("Digite o nome do produto: ")

    # Buscar o produto no MongoDB
    product_data = product_collection.find_one({"produto": produto_nome})

    if product_data:
        product_json = json.dumps(product_data, default=str)

        # Armazenar o produto no Redis
        r.set('Produto', product_json)
        print("Produto encontrado e inserido no REDIS com sucesso")

        # Solicitar novos dados do produto
        novo_produto = input("Digite o novo nome do produto (deixe em branco para não alterar): ")
        nova_quantidade = input("Digite a nova quantidade (deixe em branco para não alterar): ")
        novo_preco = input("Digite o novo preço (deixe em branco para não alterar): ")

        # Atualizar os dados no dicionário
        if novo_produto: product_data['produto'] = novo_produto
        if nova_quantidade: product_data['quantidade'] = int(nova_quantidade)
        if novo_preco: product_data['preco'] = str(novo_preco)

        # Atualizar os dados no Redis
        r.set('Produto', json.dumps(product_data, default=str))
        print("Dados do produto atualizados no Redis com sucesso")

        # Atualizar os dados no MongoDB
        product_collection.update_one({"_id": product_data["_id"]}, {"$set": product_data})
        print("Dados do produto atualizados no MongoDB com sucesso")

    else:
        print("Produto não encontrado no MongoDB")

    nome_usuario = input("Digite o nome do usuário para Fast Buy: ")

    # Buscar o usuário no MongoDB
    user_data = user_collection.find_one({"nome": nome_usuario})

    if user_data:
        Fast_Buy = input("Digite o seu Fast Buy: ")

        # Atualizar o Fast Buy no MongoDB
        user_collection.update_one({"_id": user_data["_id"]}, {"$set": {"Fast_Buy": Fast_Buy}})
        print("Fast Buy adicionado ao usuário! Você tem 40s para comprar tudo pela metade do preço")

        # Timer de 40 segundos para Fast Buy
        time.sleep(40)

        # Remover o Fast Buy após 40 segundos
        user_collection.update_one({"_id": user_data["_id"]}, {"$unset": {"Fast_Buy": ""}})
        print("Fast Buy utilizado com sucesso!")
    else:
        print("Usuário não encontrado no MongoDB")

    vendedor_nome = input("Digite o nome do vendedor que deseja remover: ")

    # Buscar e remover o vendedor no MongoDB
    vendor_data = vendor_collection.find_one({"vendedor": vendedor_nome})

    if vendor_data:
        vendor_collection.delete_one({"_id": vendor_data["_id"]})
        print("Vendedor removido do MongoDB com sucesso")
    else:
        print("Vendedor não encontrado no MongoDB")

# Chamar a função iniciarRedis para executar o código
iniciarRedis()
