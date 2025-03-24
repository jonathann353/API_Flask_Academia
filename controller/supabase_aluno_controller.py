from dotenv import load_dotenv
from flask import request, jsonify
from functools import wraps
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from hashlib import sha256
from model.db_supabase import supabase
import datetime
import jwt
import os


MY_APP = Blueprint('MY_APP', __name__)#link do controller com a main

# Carrega as variáveis do arquivo .env
load_dotenv()

# Agora você pode acessar as variáveis de ambiente
SECRET_KEY = os.getenv("SECRET_KEY")

# Rota para listar alunos
@MY_APP.route('/', methods=['GET'])
@jwt_required()
def listar():
    try:
        # Consultando dados de alunos no Supabase
        response = supabase.table('aluno').select('*').execute()
        lista_alunos = response.data
        return jsonify(mensagem='lista de alunos', dados=lista_alunos), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota para criar um novo administrador
@MY_APP.route('/criar_administrador', methods=['POST'])
@jwt_required()
def criar_administrador():
    try:
        adm = request.json
        if 'username' not in adm or 'password' not in adm:
            return jsonify(message='Campos obrigatórios: username e password'), 400

        password = adm["password"]
        hash_senha = sha256(password.encode()).hexdigest()

        # Inserindo dados do administrador no Supabase
        response = supabase.table('administrativo').insert([{
            'username': adm["username"],
            'password': hash_senha
        }]).execute()

        return jsonify({'message': 'adm inserido com sucesso'}), 201
    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota para inserir um novo aluno
@MY_APP.route('/aluno', methods=['POST'])
@jwt_required()
def inserir():
    try:
        aluno = request.json
        if 'nome' not in aluno or 'cpf' not in aluno or 'email' not in aluno or 'telefone' not in aluno or 'Cod_instrutor' not in aluno:
            return jsonify({'message': 'Campos obrigatórios: nome, cpf, email e telefone, Cod_instrutor'}), 400
        
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
@jwt_required()
def atualizar(id):
    try:
        nome = request.json.get('nome')  
        email = request.json.get('email')
        telefone = request.json.get('telefone')
        Cod_instrutor = request.json.get('Cod_instrutor')

        if not nome or not email or not telefone or not Cod_instrutor:
            return jsonify(message='Campos obrigatórios: nome, email, telefone e Cod_instrutor'), 400
        
        # Atualizando os dados do aluno no Supabase
        update_data = {}
        if nome:
            update_data['nome'] = nome
        if email:
            update_data['email'] = email
        if telefone:
            update_data['telefone'] = telefone
        if Cod_instrutor:
            update_data['Cod_instrutor'] = Cod_instrutor

        response = supabase.table('aluno').update(update_data).eq('Cod_aluno', id).execute()

        if response.status_code == 200:
            return jsonify(message='Aluno atualizado com sucesso'), 200
        else:
            return jsonify(message='Aluno não encontrado'), 404
    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota para deletar aluno
@MY_APP.route('/aluno/<int:id>', methods=['DELETE'])
@jwt_required()
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
            # Se não houver um usuário, podemos tentar acessar o erro de outra forma
            return jsonify(message="Erro ao registrar usuário", error=str(response)), 400

    except Exception as e:
        return jsonify(message=str(e)), 500
    
    
@MY_APP.route('/login', methods=['POST'])
def login():
    try:
        # Dados de login
        email = request.json.get('email')
        senha = request.json.get('senha')

        if not email or not senha:
            return jsonify(message="Email e senha são obrigatórios"), 400

        # Tentando fazer login com o Supabase
        response = supabase.auth.sign_in_with_password({
            'email': email,
            'password': senha
        })

        # Verificando se o login foi bem-sucedido
        if response.user:  # Verifica se o usuário foi autenticado com sucesso
            # Extraindo os dados do usuário
            user_data = {
                'id': response.user.id,
                'email': response.user.email
            }

            # Gerando o token JWT
            payload = {
                'user_id': user_data['id'],
                'email': user_data['email'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Expiração do token (1 hora)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

            # Retornando a resposta com o token
            return jsonify(message="Login bem-sucedido", user=user_data, token=token), 200

        else:
            # Se houver erro, acessa o atributo 'error'
            error_message = response.error.message if response.error else "Erro desconhecido"
            return jsonify(message=f"Erro ao fazer login: {error_message}"), 401

    except Exception as e:
        return jsonify(message=str(e)), 500
    

@MY_APP.route('/logout', methods=['POST'])
def logout():
    try:
        # Desconectando o usuário
        response = supabase.auth.sign_out()

        return jsonify(message="Logout bem-sucedido"), 200

    except Exception as e:
        return jsonify(message=str(e)), 500

# Função de decorador para exigir um JWT
def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')  # Obtendo o cabeçalho 'Authorization'
        if not token:
            return jsonify(message="Token de autenticação ausente"), 401
        
        token = token.split("Bearer ")[-1]  # Remove o "Bearer" para pegar o token puro
        
        try:
            # Decodificando o token com a chave secreta do Supabase (substitua 'sua-chave-secreta-aqui' pela chave real)
            decoded_token = jwt.decode(token, 'sua-chave-secreta-aqui', algorithms=['HS256'])
            request.user = decoded_token  # Adiciona o usuário decodificado à requisição
        except jwt.ExpiredSignatureError:
            return jsonify(message="Token expirado"), 401
        except jwt.InvalidTokenError:
            return jsonify(message="Token inválido"), 401
        return f(*args, **kwargs)
    return decorated_function

# Rota para verificar o usuário
@MY_APP.route('/verificar_usuario', methods=['GET'])
@jwt_required  # Apenas decorador
def verificar_usuario():
    try:
        user = request.user  # Obtendo usuário do token decodificado

        if user:
            return jsonify({
                'message': 'Usuário autenticado',
                'user': user
            }), 200
        else:
            return jsonify(message="Usuário não autenticado"), 401

    except Exception as e:
        return jsonify(message=str(e)), 500


@MY_APP.route('/verificar_email', methods=['POST'])
def verificar_email():
    try:
        email = request.json.get('email')

        if not email:
            return jsonify(message="Email é obrigatório"), 400

        # Enviando email de verificação
        response = supabase.auth.api.send_verification_email(email)

        if response.get('email'):
            return jsonify(message="Email de verificação enviado"), 200
        else:
            return jsonify(message="Erro ao enviar email de verificação"), 400

    except Exception as e:
        return jsonify(message=str(e)), 500
