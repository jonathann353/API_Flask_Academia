from dotenv import load_dotenv
from flask import request, jsonify
from functools import wraps
from flask import Blueprint
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from hashlib import sha256
from model.db_supabase import supabase
import datetime
import jwt
import os

MY_APP = Blueprint('MY_APP', __name__)  # Link do controller com a main

# Carrega as variáveis do arquivo .env
load_dotenv()

# Agora você pode acessar as variáveis de ambiente
SECRET_KEY = os.getenv("SECRET_KEY")

# Função para verificar se os campos obrigatórios estão no JSON
def validar_campos(campos, dados):
    for campo in campos:
        if campo not in dados:
            return False, f"Campo obrigatório: {campo}"
    return True, None

# Rota para listar alunos
@MY_APP.route('/', methods=['GET'])
#@jwt_required()
def listar():
    try:
        # Consultando dados de alunos no Supabase
        response = supabase.table('aluno').select('*').execute()
        lista_alunos = response.data
        return jsonify(mensagem='Lista de alunos', dados=lista_alunos), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota para criar um novo administrador
@MY_APP.route('/criar_administrador', methods=['POST'])
#@jwt_required()
def criar_administrador():
    try:
        adm = request.json
        campos_obrigatorios = ['username', 'password']
        valido, mensagem = validar_campos(campos_obrigatorios, adm)
        if not valido:
            return jsonify(message=mensagem), 400

        password = adm["password"]
        hash_senha = sha256(password.encode()).hexdigest()

        # Inserindo dados do administrador no Supabase
        response = supabase.table('administrativo').insert([{
            'username': adm["username"],
            'password': hash_senha
        }]).execute()

        return jsonify({'message': 'Administrador inserido com sucesso'}), 201
    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota para inserir um novo aluno
@MY_APP.route('/aluno', methods=['POST'])
#@jwt_required()
def inserir():
    try:
        aluno = request.json
        campos_obrigatorios = ['nome', 'cpf', 'email', 'telefone', 'Cod_instrutor']
        valido, mensagem = validar_campos(campos_obrigatorios, aluno)
        if not valido:
            return jsonify({'message': mensagem}), 400
        
        # Inserindo novo aluno no Supabase
        response = supabase.table('aluno').insert([{
            'nome': aluno["nome"],
            'cpf': aluno["cpf"],
            'email': aluno["email"],
            'telefone': aluno["telefone"],
            'Cod_instrutor': aluno["Cod_instrutor"]
        }]).execute()

        return jsonify({'message': 'Aluno inserido com sucesso'}), 201
    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota para atualizar aluno
@MY_APP.route('/aluno/<int:id>', methods=['PUT'])
#@jwt_required()
def atualizar(id):
    try:
        nome = request.json.get('nome')  
        email = request.json.get('email')
        telefone = request.json.get('telefone')
        Cod_instrutor = request.json.get('Cod_instrutor')

        if not nome or not email or not telefone or not Cod_instrutor:
            return jsonify(message='Campos obrigatórios: nome, email, telefone e Cod_instrutor'), 400
        
        # Atualizando os dados do aluno no Supabase
        update_data = {
            'nome': nome,
            'email': email,
            'telefone': telefone,
            'Cod_instrutor': Cod_instrutor
        }

        response = supabase.table('aluno').update(update_data).eq('Cod_aluno', id).execute()

        if response.status_code == 200:
            return jsonify(message='Aluno atualizado com sucesso'), 200
        else:
            return jsonify(message='Aluno não encontrado'), 404
    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota para deletar aluno
@MY_APP.route('/aluno/<int:id>', methods=['DELETE'])
#@jwt_required()
def deletar(id):
    try:
        # Deletando aluno no Supabase
        response = supabase.table('aluno').delete().eq('Cod_aluno', id).execute()

        if response.status_code == 200:
            return jsonify(message='Aluno deletado com sucesso'), 200
        else:
            return jsonify(message='Aluno não encontrado'), 404
    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota para registrar um novo usuário
@MY_APP.route('/registrar', methods=['POST'])
def registrar():
    try:
        # Dados do novo usuário
        email = request.json.get('email')
        senha = request.json.get('senha')

        if not email or not senha:
            return jsonify(message="Email e senha são obrigatórios"), 400

        # Registrando usuário com o Supabase
        response = supabase.auth.sign_up({
            'email': email,
            'password': senha
        })

        # Verificando se a resposta contém erro
        if response.user:
            return jsonify(message="Usuário registrado com sucesso"), 201
        else:
            return jsonify(message="Erro ao registrar usuário", error=str(response)), 400

    except Exception as e:
        return jsonify(message=str(e)), 500

# Rota para login
# @MY_APP.route('/login', methods=['POST'])
# def login():
#     try:
#         email = request.json.get('email')
#         senha = request.json.get('senha')

#         if not email or not senha:
#             return jsonify(message="Email e senha são obrigatórios"), 400

#         # Tentando autenticação no Supabase
#         response = supabase.auth.sign_in_with_password({
#             "email": email,
#             "password": senha
#         })

#         # Verificando se a resposta contém user e session
#         if response and response.user:
#             token = response.session.access_token  # Obtendo o token do Supabase

#             return jsonify(
#                 message="Login bem-sucedido",
#                 user={"id": response.user.id, "email": response.user.email},
#                 token=token
#             ), 200

#         else:
#             return jsonify(message="Falha no login"), 401

#     except Exception as e:
#         return jsonify(message=f"Erro: {str(e)}"), 500

# # Rota para logout
# @MY_APP.route('/logout', methods=['POST'])
# def logout():
#     try:
#         # Desconectando o usuário
#         response = supabase.auth.sign_out()

#         return jsonify(message="Logout bem-sucedido"), 200

#     except Exception as e:
#         return jsonify(message=str(e)), 500

# Rota para verificar o usuário
# @MY_APP.route('/verificar_usuario', methods=['GET'])
# @jwt_required()  # Requer um token fresco
# def verificar_usuario():
#     try:
#         user_identity = get_jwt_identity()
#         if user_identity:
#             return jsonify({'message': 'Usuário autenticado', 'user': user_identity}), 200
#         else:
#             return jsonify(message="Usuário não autenticado"), 401

#     except Exception as e:
#         return jsonify(message=f"Erro interno: {str(e)}"), 500

# # Rota para verificar email
# @MY_APP.route('/verificar_email', methods=['POST'])
# def verificar_email():
#     try:
#         email = request.json.get('email')

#         if not email:
#             return jsonify(message="Email é obrigatório"), 400

#         # Enviando email de verificação
#         response = supabase.auth.api.send_verification_email(email)

#         if response.get('email'):
#             return jsonify(message="Email de verificação enviado"), 200
#         else:
#             return jsonify(message="Erro ao enviar email de verificação"), 400

#     except Exception as e:
#         return jsonify(message=str(e)), 500
