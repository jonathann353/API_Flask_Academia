import psycopg2

# Estabelece a conexão com o banco de dados postgres
conn = psycopg2.connect(host='localhost', user='user', password='password', dbname='database')
