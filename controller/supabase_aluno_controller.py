from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from hashlib import sha256
from model.db_supabase import supabase


MY_APP = Blueprint('MY_APP', __name__)#link do controller com a main

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

        # Realizando login com o Supabase
        response = supabase.auth.sign_in_with_password({
            'email': email,
            'password': senha
        })

        # Verificando se o login foi bem-sucedido
        if response.get('user'):
            return jsonify(message="Usuário logado com sucesso", user=response['user']), 200
        else:
            return jsonify(message="Erro ao fazer login", error=str(response)), 400

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

@MY_APP.route('/verificar_usuario', methods=['GET'])
@jwt_required()  # Você pode adicionar essa proteção se usar JWT ou outra forma de autenticação
def verificar_usuario():
    try:
        # Obtendo informações do usuário logado
        user = supabase.auth.get_user()

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
