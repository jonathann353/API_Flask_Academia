from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from model.db_Aluno import aluno, id
from model.db_admin import User

aluno_app = Blueprint('aluno_app', __name__)


@aluno_app.route('/', methods=['GET'])
@jwt_required()
def listar():
    try:
        return jsonify(aluno), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500


@aluno_app.route('/aluno', methods=['POST'])
@jwt_required()
def inserir():
    try:
        global id
        alunos = request.json    
        if 'nome' not in alunos:
            return jsonify({'message': 'Campo "nome" é obrigatório'}), 400 
        id += 1
        alunos['id'] = id
        aluno.append(alunos)
        return jsonify({'message': 'Aluno inserido com sucesso'}), 201
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    
@aluno_app.route('/aluno/<int:id>', methods=['GET'])
@jwt_required()
def buscar(id):
    try:
        alunos = next((t for t in aluno if t['id'] == id), None)
        if alunos:
            return jsonify(alunos)
        return jsonify({'message': 'Aluno não encontrado'}), 404
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    
@aluno_app.route('/aluno/<int:id>', methods=['PUT'])
@jwt_required()
def atualizar(id):
    try:
        alunos = next((t for t in aluno if t['id'] == id), None)
        if not alunos:
            return jsonify({'message': 'Aluno não encontrado'}), 404
        aluno_novo = request.json
        if 'nome' in aluno_novo:
            alunos['nome'] = aluno_novo['nome']
        return jsonify({'message': 'Aluno atualizado com sucesso'}), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    
@aluno_app.route('/aluno/<int:id>', methods=['DELETE'])
@jwt_required()
def deletar(id):
    try:
        alunos = next((t for t in aluno if t['id'] == id), None)
        if not alunos:
            return jsonify({'message': 'Aluno não encontrado'}), 404
        aluno.remove(alunos)
        return jsonify({'message': f'Aluno {alunos} removido com sucesso'}), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500

@aluno_app.route('/login', methods=['POST'])
def login():
    try:
        login_data = request.get_json()
        username = login_data['username']
        password = login_data['password']

        if username is None or password is None:
            return jsonify({'message': 'Nome de usuário e senha são obrigatórios'}), 400

        user = next((t for t in User if t['username'] == username and t['password'] == password), None)
        if not user:
            return jsonify({'message': 'Nome de usuário ou senha incorretos'}), 401

        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500

@aluno_app.route('/logado', methods=['GET'])
@jwt_required()
def protected():
    try:
        current_user = get_jwt_identity()
        return jsonify(f'Logado como: {current_user}'), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500