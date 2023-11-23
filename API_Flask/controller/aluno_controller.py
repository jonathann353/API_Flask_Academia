from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from model.connection import db
from model.db_admin import User

aluno_app = Blueprint('aluno_app', __name__)

@aluno_app.route('/', methods=['GET'])
@jwt_required()
def listar():
    try:
        cursor = db.cursor()
        cursor.execute('select * from aluno')
        tabela = cursor.fetchall()

        lista_alunos = []
        for aluno in tabela:
            aluno_dict = {
                'Cod_aluno': aluno[0],
                'nome': aluno[1],
                'cpf': aluno[2],
                'email': aluno[3],
                'telefone': aluno[4],
                'instrutor': aluno[5]
            }
            lista_alunos.append(aluno_dict)

        return jsonify(mensagem='lista de alunos', dados=lista_alunos), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    finally:
        cursor.close()

@aluno_app.route('/aluno', methods=['POST'])
@jwt_required()
def inserir():
    try:
        cursor = db.cursor()
        aluno = request.json
        if 'nome' not in aluno or 'cpf' not in aluno or 'email' not in aluno or 'telefone' not in aluno:
            return jsonify({'message': 'Campos obrigatórios: nome, cpf, email e telefone'}), 400

        alunos = 'INSERT INTO aluno(nome, cpf, email, telefone) VALUES(%s, %s, %s, %s)'
        dados = (aluno["nome"], aluno["cpf"], aluno["email"], aluno["telefone"])
        cursor.execute(alunos, dados)
        db.commit() 
        return jsonify({'message': 'Aluno inserido com sucesso'}), 201
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    finally:
        cursor.close()
    
@aluno_app.route('/aluno/<int:id>', methods=['GET'])
@jwt_required()
def buscar(id):
    try:
        cursor = db.cursor()
        if not id:
            return jsonify(message='Campo id é obrigatórios'), 400

        cursor.execute(f'select * from aluno where Cod_aluno={id}')
        aluno = cursor.fetchall()
        if aluno:
            for dados in aluno:
                dados = {
                'Cod_aluno': dados[0],
                'nome': dados[1],
                'cpf': dados[2],
                'email': dados[3],
                'telefone': dados[4],
                'instrutor': dados[5]
            }
            return jsonify(dados)
        return jsonify(message='Aluno não encontrado'), 404
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    finally:
        cursor.close()

@aluno_app.route('/aluno/<int:id>', methods=['PUT'])
@jwt_required()
def atualizar(id):
    try:
        cursor = db.cursor()
        nome = request.json.get('nome')  
        email = request.json.get('email')
        telefone = request.json.get('telefone')
        if not nome or not email or not telefone:
            return jsonify(message='Campo "nome", "e-mail" e "telefone" é obrigatório'), 400
        if not id:
            return jsonify(message='Campo "id" é obrigatório'), 400
        sql = "UPDATE aluno SET nome = %s, email = %s, telefone = %s WHERE Cod_aluno = %s"
        dados = (nome, email, telefone, id)
        cursor.execute(sql, dados)
        db.commit()
        if cursor.rowcount > 0:
            return jsonify(message='Aluno atualizado com sucesso'), 200
        else:
            return jsonify(message='Aluno não encontrado'), 404
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    finally:
        cursor.close()


@aluno_app.route('/aluno/<int:id>', methods=['DELETE'])
@jwt_required()
def deletar(id):
    try:
        cursor = db.cursor()
        if not id:
            return jsonify({'message': 'Aluno não encontrado'}), 404
        cursor.execute(f"delete from aluno where Cod_={id}")
        db.commit()
        if cursor.rowcount > 0:
            return jsonify(message='Aluno deletado com sucesso'), 200
        else:
            return jsonify(message='Aluno não encontrado'), 404
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    finally:
        cursor.close()

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