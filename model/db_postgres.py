import psycopg2

# Estabelece a conexão com o banco de dados postgres
conn = psycopg2.connect(host='localhost', user='username', port='port', password='password', dbname='database')
