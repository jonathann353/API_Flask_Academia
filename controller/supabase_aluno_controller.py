from dotenv import load_dotenv
from flask import request, jsonify
from functools import wraps
from flask import Blueprint
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from hashlib import sha256
from model.db_supabase import supabase
from supabase import create_client, Client
import datetime
import jwt
import os

MY_APP = Blueprint('MY_APP', __name__)

# Supabase URL e chave (substitua pelos valores da sua conta Supabase)
SUPABASE_URL = "https://pgdldfqzqgxowqedrldh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBnZGxkZnF6cWd4b3dxZWRybGRoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc1Nzk0MjksImV4cCI6MjA1MzE1NTQyOX0.jntDjoG90UW916FljiMlrmM4YqaNLeTphwTO2IPkY9E"  # Substitua pela chave real

# Carregar variáveis de ambiente
SECRET_KEY = os.getenv("SECRET_KEY")

# Crie o cliente do Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Função para verificar se os campos obrigatórios estão no JSON
def validar_campos(campos, dados):
    for campo in campos:
        if campo not in dados:
            return False, f"Campo obrigatório: {campo}"
    return True, None

# Rota "/instrutor" - método POST adiciona um novo instrutor no sistema
@MY_APP.route('/instrutor', methods=['POST'])
# @jwt_required()
def instrutor():
    instrutor = request.json
    try:
        campos_obrigatorios = ['nome', 'Num_Confef', 'telefone', 'funcao']
        valido, mensagem = validar_campos(campos_obrigatorios, instrutor)
        if not valido:
            return jsonify(message=mensagem), 400

        # Inserir no Supabase
        response = supabase.table('instrutor').insert({
            'nome': instrutor["nome"],
            'Num_Confef': instrutor["Num_Confef"],
            'telefone': instrutor["telefone"],
            'funcao': instrutor["funcao"]
        }).execute()

        if response.status_code == 201:
            return jsonify({'message': 'Instrutor inserido com sucesso'}), 201
        return jsonify({'message': 'Erro ao inserir instrutor'}), 500
    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota "/treino" - método POST adiciona um novo treino no sistema
@MY_APP.route('/treino', methods=['POST'])
# @jwt_required()
def treino():
    try:
        treino = request.json
        campos_obrigatorios = ['tipo_treino', 'exercicio', 'serie', 'repeticao', 'Cod_aluno', 'Cod_instrutor']
        valido, mensagem = validar_campos(campos_obrigatorios, treino)
        if not valido:
            return jsonify(message=mensagem), 400

        # Inserir no Supabase
        response = supabase.table('treino').insert({
            'tipo_treino': treino["tipo_treino"],
            'exercicio': treino["exercicio"],
            'serie': treino["serie"],
            'repeticao': treino["repeticao"],
            'Cod_aluno': treino["Cod_aluno"],
            'Cod_instrutor': treino["Cod_instrutor"]
        }).execute()

        if response.status_code == 201:
            return jsonify({'message': 'Treino inserido com sucesso'}), 201
        return jsonify({'message': 'Erro ao inserir treino'}), 500
    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota "/aluno/id" - método GET busca no sistema pelo id do aluno
@MY_APP.route('/aluno/<int:id>', methods=['GET'])
# @jwt_required()
def buscar(id):
    try:
        if not id:
            return jsonify(message='Campo id é obrigatório'), 400

        # Consultar no Supabase
        response = supabase.table('aluno').select('*').eq('Cod_aluno', id).execute()

        if response.status_code == 200 and response.data:
            aluno = response.data[0]
            return jsonify({
                'Cod_aluno': aluno['Cod_aluno'],
                'nome': aluno['nome'],
                'cpf': aluno['cpf'],
                'email': aluno['email'],
                'telefone': aluno['telefone']
            })
        return jsonify(message='Aluno não encontrado'), 404
    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota "/detalhes_aluno_e_instrutores/id" - método GET busca relação de aluno e instrutores
@MY_APP.route('/detalhes_aluno_e_instrutores/<int:id>', methods=['GET'])
# @jwt_required()
def detalhes_aluno_e_instrutores(id):
    try:
        if not id:
            return jsonify(message='Campo id é obrigatório'), 400

        # Consultar no Supabase
        response = supabase.table('aluno').select('nome', 'cpf', 'email', 'telefone', 'instrutor!inner(nome, funcao)').eq('Cod_aluno', id).execute()

        if response.status_code == 200 and response.data:
            aluno = response.data[0]
            return jsonify({
                'nome aluno': aluno['nome'],
                'cpf aluno': aluno['cpf'],
                'email aluno': aluno['email'],
                'telefone aluno': aluno['telefone'],
                'instrutor': {
                    'nome instrutor': aluno['instrutor']['nome'],
                    'funcao instrutor': aluno['instrutor']['funcao']
                }
            })
        return jsonify(message='Aluno não encontrado'), 404
    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota "/detalhes_treino_aluno/id" - método GET busca detalhes do treino do aluno
@MY_APP.route('/detalhes_treino_aluno/<int:id>', methods=['GET'])
# @jwt_required()
def detalhes_treino_aluno(id):
    try:
        if not id:
            return jsonify(message='Campo id é obrigatório'), 400

        # Consultar no Supabase
        response = supabase.table('treino').select('aluno.nome', 'instrutor.nome', 'tipo_treino', 'exercicios', 'serie', 'repeticoes').eq('Cod_aluno', id).execute()

        if response.status_code == 200 and response.data:
            treino = response.data[0]
            return jsonify({
                'nome aluno': treino['aluno']['nome'],
                'nome instrutor': treino['instrutor']['nome'],
                'treino': {
                    'tipo_treino': treino['tipo_treino'],
                    'exercicio': treino['exercicios'],
                    'serie': treino['serie'],
                    'repeticao': treino['repeticoes']
                }
            })
        return jsonify(message='Treino não encontrado'), 404
    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota "/aluno/id" - método PUT atualiza os dados do aluno
@MY_APP.route('/aluno/<int:id>', methods=['PUT'])
# @jwt_required()
def atualizar(id):
    try:
        nome = request.json.get('nome')
        email = request.json.get('email')
        telefone = request.json.get('telefone')
        Cod_instrutor = request.json.get('Cod_instrutor')

        if not nome or not email or not telefone or not Cod_instrutor:
            return jsonify(message='Campos obrigatórios: nome, email, telefone e Cod_instrutor'), 400

        # Atualizar no Supabase
        response = supabase.table('aluno').update({
            'nome': nome,
            'email': email,
            'telefone': telefone,
            'Cod_instrutor': Cod_instrutor
        }).eq('Cod_aluno', id).execute()

        if response.status_code == 200:
            return jsonify(message='Aluno atualizado com sucesso'), 200
        return jsonify(message='Aluno não encontrado'), 404
    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota "/aluno/id" - método DELETE exclui o aluno do sistema
@MY_APP.route('/aluno/<int:id>', methods=['DELETE'])
# @jwt_required()
def deletar(id):
    try:
        response = supabase.table('aluno').delete().eq('Cod_aluno', id).execute()

        if response.status_code == 200:
            return jsonify(message='Aluno deletado com sucesso'), 200
        return jsonify(message='Aluno não encontrado'), 404
    except Exception as err:
        return jsonify({'message': str(err)}), 500

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
        response = supabase.table('administrador').insert({
            'username': adm['username'],
            'password': hash_senha
        }).execute()

        if response.status_code == 201:
            return jsonify(message='Administrador criado com sucesso'), 201
        return jsonify(message='Erro ao criar administrador'), 500
    except Exception as err:
        return jsonify({'message': str(err)}), 500
