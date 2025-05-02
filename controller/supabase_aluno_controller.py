from dotenv import load_dotenv
from flask import request, jsonify
from functools import wraps
from flask import Blueprint
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from hashlib import sha256
from supabase import create_client, Client
import logging
from datetime import datetime
from datetime import timedelta
import jwt
import os

MY_APP = Blueprint('MY_APP', __name__)

# Supabase URL e chave (substitua pelos valores da sua conta Supabase)
load_dotenv()  # Carrega as variáveis do .env

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Carregar variáveis de ambiente
SECRET_KEY = os.getenv("SECRET_KEY")

# Crie o cliente do Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

logging.basicConfig(level=logging.DEBUG)
# Função para verificar se os campos obrigatórios estão no JSON
def validar_campos(campos, dados):
    for campo in campos:
        if campo not in dados:
            return False, f"Campo obrigatório: {campo}"
    return True, None

# Rota para criar um novo administrador
@MY_APP.route('/criar_administrador', methods=['POST'])
def criar_administrador():
    try:
        adm = request.json
        campos_obrigatorios = ['username', 'password']
        valido, mensagem = validar_campos(campos_obrigatorios, adm)
        if not valido:
            return jsonify(message=mensagem), 400

        password = adm["password"]
        hash_senha = sha256(password.encode()).hexdigest()

        # Inserindo dados no Supabase
        response = supabase.table('administrativo').insert({
            'username': adm['username'],
            'password': hash_senha
        }).execute()

        return jsonify(message='Administrador criado com sucesso'), 200
        
    except Exception as err:
        return jsonify(message='Erro ao criar administrador'), 500
        


#rota "/" raiz da aplicação lista os alunos cadastrados no sistema
@MY_APP.route('/listar/aluno', methods=['GET'])
#@jwt_required()
def listar_Aluno():
    try:
        response = supabase.table('aluno').select("*").execute()
        if response.data:
            lista_alunos = [
                {
                    'cod_aluno': aluno['cod_aluno'],
                    'nome': aluno['nome'],
                    'cpf': aluno['cpf'],
                    'email': aluno['email'],
                    'telefone': aluno['telefone'],
                    'Cod_instrutor':aluno['Cod_instrutor'],
                    'status': aluno['status'],
                    'data_nascimento': aluno['data_nascimento'],
                    'sexo': aluno['sexo']
                } for aluno in response.data
            ]
            return jsonify(mensagem='lista de alunos', dados=lista_alunos), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500

@MY_APP.route('/listar/instrutor', methods=['GET'])
#@jwt_required()
def listar_Instrutor():
    try:
        response = supabase.table('instrutor').select("*").execute()
        if response.data:
            lista_instrutor = [
                {
                    'cod_instrutor': instrutor['cod_instrutor'],
                    'nome': instrutor['nome'],
                    'num_confef': instrutor['num_confef'],
                    'telefone': instrutor['telefone'],
                    'funcao': instrutor['funcao']
                } for instrutor in response.data
            ]
        return jsonify(mensagem='lista de instrutor', dados=lista_instrutor), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota "/instrutor" - método POST adiciona um novo instrutor no sistema
@MY_APP.route('/inserir/instrutor', methods=['POST'])
#@jwt_required()  # Habilita a verificação do token JWT
def inserir_Instrutor():
    instrutor = request.json
    try:
        # Valida se os campos obrigatórios estão presentes
        campos_obrigatorios = ['nome', 'num_confef', 'telefone', 'funcao']
        valido, mensagem = validar_campos(campos_obrigatorios, instrutor)
        if not valido:
            return jsonify(message=mensagem), 400

        # Inserir o novo instrutor na tabela "instrutor" do Supabase
        response = supabase.table('instrutor').insert({
            'nome': instrutor["nome"],
            'num_confef': instrutor["num_confef"],
            'telefone': instrutor["telefone"],
            'funcao': instrutor["funcao"]
        }).execute()
        return jsonify({'message': 'Instrutor inserido com sucesso'}), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    
# Rota "/aluno" - método POST adiciona um novo aluno no sistema
@MY_APP.route('/inserir/aluno', methods=['POST'])
#@jwt_required()  # Habilita a verificação do token JWT
def inserir_Aluno():
    aluno = request.json
    try:
        # Valida se os campos obrigatórios estão presentes
        campos_obrigatorios = ['nome', 'cpf', 'email', 'telefone','status','data_nascimento', 'sexo']
        valido, mensagem = validar_campos(campos_obrigatorios, aluno)
        if not valido:
            return jsonify("Campos Obrigatórios: 'nome', 'cpf', 'email', 'telefone', 'status','data_nascimento', 'sexo'"), 400

        # Inserir o novo aluno na tabela "aluno" do Supabase
        response = supabase.table('aluno').insert({
            'nome': aluno["nome"],
            'cpf': aluno["cpf"],
            'email':aluno['email'],
            'telefone': aluno["telefone"],
            'Cod_instrutor':aluno['Cod_instrutor'],
            'status': aluno['status'],
            'data_nascimento': aluno['data_nascimento'],
            'sexo': aluno['sexo']
        }).execute()
        return jsonify({'message': 'aluno inserido com sucesso'}), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    
    
# Rota "/aluno/id" - método GET busca no sistema pelo id do aluno
@MY_APP.route('/busca/aluno/<int:id>', methods=['GET'])
# @jwt_required()
def buscar_Aluno(id):
    try:
        if not id:
            return jsonify(message='Campo id é obrigatório'), 400

        # Consultar no Supabase
        response = supabase.table('aluno').select('*').eq('cod_aluno', id).execute()

        if response.data:
            aluno = [{'cod_aluno': aluno['cod_aluno'],
                'nome': aluno['nome'],
                'cpf': aluno['cpf'],
                'email': aluno['email'],
                'telefone': aluno['telefone'],
                'Cod_instrutor':aluno['Cod_instrutor'],
                'status': aluno['status'],
                'data_nascimento': aluno['data_nascimento'],
                'sexo': aluno['sexo']
                } for aluno in response.data
            ]
        return jsonify(mensagem='Aluno encontrado', dados=aluno), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota "/detalhes_aluno_e_instrutores/id" - método GET busca relação de aluno e instrutores
@MY_APP.route('/detalhes/aluno/e/instrutores/<int:id>', methods=['GET'])
# @jwt_required()
def detalhes_Aluno_e_Instrutores(id):
    try:
        # Buscar aluno pelo ID
        response_aluno = supabase.table('aluno').select("*").eq("cod_aluno", id).execute()
        
        if not response_aluno.data:
            return jsonify(message='Aluno não encontrado'), 404

        aluno = response_aluno.data[0]
        cod_instrutor = aluno.get("Cod_instrutor")

        instrutor = {}
        if cod_instrutor:
            response_instrutor = supabase.table('instrutor').select("nome, funcao").eq("cod_instrutor", cod_instrutor).execute()
            if response_instrutor.data:
                instrutor = response_instrutor.data[0]

        return jsonify({
            'nome_aluno': aluno['nome'],
            'cpf_aluno': aluno['cpf'],
            'email_aluno': aluno['email'],
            'telefone_aluno': aluno['telefone'],
            'instrutor': {
                'nome_instrutor': instrutor.get('nome', 'Não informado'),
                'funcao_instrutor': instrutor.get('funcao', 'Não informado')
            }
        }), 200

    except Exception as err:
        return jsonify({'message': str(err)}), 500
    
    
# Rota "/detalhes_treino_aluno/id" - método GET busca detalhes do treino do aluno
@MY_APP.route('/detalhes/treino/aluno/<int:id>', methods=['GET'])
# @jwt_required()
def detalhes_Treino_Aluno(id):
    try:
        if not id:
            return jsonify(message='Campo id é obrigatório'), 400

        # Consulta os treinos do aluno
        response_treino = supabase.table('treino').select('*').eq('cod_aluno', id).execute()
        if not response_treino.data:
            return jsonify(message='Treinos não encontrados'), 404

        treinos = response_treino.data

        # Pega o nome do aluno
        response_aluno = supabase.table('aluno').select('nome').eq('cod_aluno', id).execute()
        nome_aluno = response_aluno.data[0]['nome'] if response_aluno.data else 'Não informado'

        resultado = []
        for treino in treinos:
            cod_instrutor = treino.get('cod_instrutor')
            if cod_instrutor:
                response_instrutor = supabase.table('instrutor').select('nome').eq('cod_instrutor', cod_instrutor).execute()
                nome_instrutor = response_instrutor.data[0]['nome'] if response_instrutor.data else 'Não informado'
            else:
                nome_instrutor = 'Não informado'

            resultado.append({
                'nome_aluno': nome_aluno,
                'nome_instrutor': nome_instrutor,
                'treino': {
                    'tipo_treino': treino.get('tipo_treino'),
                    'exercicio': treino.get('exercicio'),
                    'serie': treino.get('serie'),
                    'repeticao': treino.get('repeticao')
                }
            })

        return jsonify(resultado), 200

    except Exception as err:
        return jsonify({'message': str(err)}), 500
   
    
# Rota "/aluno/id" - método PUT atualiza os dados do aluno
@MY_APP.route('/atualizar/aluno/<int:id>', methods=['PUT'])
# @jwt_required()
def atualizar_Aluno(id):
    try:
        nome = request.json.get('nome')
        email = request.json.get('email')
        telefone = request.json.get('telefone')
        Cod_instrutor = request.json.get('Cod_instrutor')
        status= request.json.get('status')
       

        if not nome or not email or not telefone or not Cod_instrutor:
            return jsonify(message='Campos obrigatórios: nome, email, telefone e Cod_instrutor'), 400

        # Atualizar no Supabase
        response = supabase.table('aluno').update({
            'nome': nome,
            'email': email,
            'telefone': telefone,
            'Cod_instrutor': Cod_instrutor,
            'status':status
        }).eq('cod_aluno', id).execute()

        return jsonify(mensagem='Aluno atualizado com sucesso'), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    

# Rota "/aluno/id" - método DELETE exclui o aluno do sistema
@MY_APP.route('/deletar/aluno/<int:id>', methods=['DELETE'])
def deletar_Aluno(id):
    try:
        response = supabase.table('aluno').delete().eq('cod_aluno', id).execute()
        if response.data:
            return jsonify(message='Aluno deletado com sucesso'), 200
        return jsonify(message='Aluno não encontrado'), 404
    except Exception as err:
        return jsonify({'message': f'Erro ao deletar: {str(err)}'}), 500

# Rota "/treino" - método POST adiciona um novo treino no sistema
@MY_APP.route('/adicionar/treino', methods=['POST'])
# @jwt_required()
def adicionar_Treino():
    try:
        treino = request.json
        campos_obrigatorios = ['tipo_treino', 'exercicio', 'serie', 'repeticao', 'cod_aluno', 'cod_instrutor']
        valido, mensagem = validar_campos(campos_obrigatorios, treino)
        if not valido:
            return jsonify(message=mensagem), 400

        # Inserir no Supabase
        response = supabase.table('treino').insert({
            'tipo_treino': treino["tipo_treino"],
            'exercicio': treino["exercicio"],
            'serie': treino["serie"],
            'repeticao': treino["repeticao"],
            'cod_aluno': treino["cod_aluno"],
            'cod_instrutor': treino["cod_instrutor"]
        }).execute()

        if response.data:
            return jsonify({'message': 'Treino inserido com sucesso'}), 200
        return jsonify({'message': 'Erro ao inserir treino'}), 500
    except Exception as err:
        return jsonify({'message': str(err)}), 500

@MY_APP.route('/login', methods=['POST'])
def login_user():
    try:
        login_data = request.get_json()

        if 'username' not in login_data or 'password' not in login_data:
            return jsonify({'message': 'Nome de usuário e senha são obrigatórios'}), 400

        username = login_data['username']
        password = login_data['password']

        # Busca o usuário na tabela 'administrativo' no Supabase
        response = supabase.table("auth_user").select("*").eq("username", username).execute()
        user_data = response.data

        if not user_data:
            return jsonify({'message': 'Nome de usuário ou senha incorretos'}), 401

        # Pegando o hash da senha salva no banco
        hashed_password_from_db = user_data[0]['password']

        # Gerando hash da senha enviada pelo usuário
        hashed_password_input = sha256(password.encode('utf-8')).hexdigest()

        if hashed_password_input == hashed_password_from_db:
            # Criando token com validade de 2h
            access_token = create_access_token(identity=username, expires_delta=timedelta(hours=2))
            return jsonify({'access_token': access_token}), 200
        else:
            return jsonify({'message': 'Nome de usuário ou senha incorretos'}), 401

    except Exception as err:
        return jsonify({'message': str(err)}), 500

@MY_APP.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name') or ""
        last_name = data.get('last_name') or ""

        if not username or not email or not password:
            return jsonify({"error": "Missing required fields"}), 400

        # Verifique se o usuário já existe
        existing_user = supabase.table("auth_user").select("*").eq("username", username).execute()
        if existing_user.data:
            return jsonify({"error": "User already exists"}), 409

        # Gerar hash da senha com sha256
        hashed_password = sha256(password.encode('utf-8')).hexdigest()

        # Inserir o novo usuário
        response = supabase.table("auth_user").insert({
            "username": username,
            "email": email,
            "password": hashed_password,
            "is_superuser": False,
            "is_staff": False,
            "is_active": True,
            "first_name": first_name,
            "last_name": last_name,
            "date_joined": datetime.now().isoformat()
        }).execute()

        if response.data:
            return jsonify({'message': 'Usuário adicionado com sucesso'}), 200
        return jsonify({'message': 'Erro ao inserir usuário'}), 500

    except Exception as err:
        return jsonify({'message': str(err)}), 500


@MY_APP.route('/logado', methods=['GET'])
@jwt_required()
def protected():
    try:
        current_user = get_jwt_identity()
        return jsonify(f'Logado como: {current_user}'), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500
