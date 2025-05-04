import streamlit as st
from azure.storage.blob import BlobServiceClient
import os
import pymssql
import uuid
import json
from dotenv import load_dotenv
load_dotenv()

blobConnectionString = os.getenv('BLOB_CONNECTION_STRING')
blobContainerName = os.getenv('BLOB_CONTAINER_NAME')
blobAccountName = os.getenv('BLOB_ACCOUNT_NAME')

sqlServer = os.getenv('SQL_SERVER')
sqlDatabase = os.getenv('SQL_DATABASE')
sqlUser = os.getenv('SQL_USER')
sqlPassword = os.getenv('SQL_PASSWORD')

st.title("Cadastro de Produtos")

#formulario de cadastro de produtos
product_name = st.text_input("Nome do Produto")
product_price = st.number_input("Preço do Produto", min_value=0.0, format="%.2f")
product_description = st.text_area("Descrição do Produto")
product_image = st.file_uploader("Imagem do Produto", type=["jpg", "jpeg", "png", "webp"])

#save image on blob storage
def upload_image_to_blob(image_file):
    blob_service_client = BlobServiceClient.from_connection_string(blobConnectionString)
    blob_container_client = blob_service_client.get_container_client(blobContainerName)
    blob_name = str(uuid.uuid4()) + "_" + image_file.name
    blob_client = blob_container_client.get_blob_client(blob_name)
    blob_client.upload_blob(image_file.read(), overwrite=True)
    image_url = f"https://{blobAccountName}.blob.core.windows.net/{blobContainerName}/{blob_name}"
    return image_url

#save product on sql server
def  insert_product(name, price, description, product_image):
    try:
        image_url = upload_image_to_blob(product_image)
        insert_sql = f"INSERT INTO dbo.Produtos (nome, preco, descricao, imagem_url) VALUES ('{name}', '{price}', '{description}', '{image_url}')"
        print(insert_sql)
        conn = pymssql.connect(sqlServer, sqlUser, sqlPassword, sqlDatabase)
        cursor = conn.cursor()
        cursor.execute(insert_sql)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao inserir produto: {e}")  
        return False 
    
#listar produtos no sql server
def list_products():
    try:
        conn = pymssql.connect(server=sqlServer, user=sqlUser, password=sqlPassword, database=sqlDatabase)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dbo.Produtos")
        products = cursor.fetchall()
        conn.close()
        return products
    except Exception as e:
        st.error(f"Erro ao listar produtos: {e}")
        return []
    
def list_products_screen():
    products = list_products()
    if products:
        for product in products:
            with st.container():
                st.image(product[4], width=200)
                st.markdown(f"### {product[1]}")  # Nome do produto como título
                st.markdown(f"**Preço:** R$ {product[3]:.2f}")
                st.markdown(f"**Descrição:** {product[2]}")
                st.markdown("---")  # Linha divisória entre os cards    else:
        st.write("Nenhum produto cadastrado.")

if st.button("Cadastrar Produto"):
    insert_product(product_name, product_price, product_description, product_image)
    return_message = 'Produto salvo com sucesso'

st.header('Produtos Cadastrados')

if st.button('Listar Produtos'):
    list_products_screen()
    return_message = 'Produtos listados com sucesso'
