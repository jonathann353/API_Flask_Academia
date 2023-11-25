from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from hashlib import sha256
from model.connection import db
from model.db_admin import UserTest

MY_APP = Blueprint('MY_APP', __name__)#link do controller com a main


#rota "/" raiz da aplicação lista os alunos cadastrados no sistema
@MY_APP.route('/', methods=['GET'])
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


#rota "/adm" faz a inserção de um novo administrador do sistema
@MY_APP.route('/adm', methods=['POST'])
@jwt_required()
def admin():
    try:
        cursor = db.cursor()
        adm = request.json
        if 'username' not in adm or 'password' not in adm:
            return jsonify(message='Campos obrigatórios: username e password'), 400        
        password = adm["password"]
        hash_senha = sha256(password.encode()).hexdigest()
        adms = 'INSERT INTO administrativo(username, password) VALUES(%s, %s)'
        dados = (adm["username"], hash_senha)  # Armazenando o hash da senha no banco
        cursor.execute(adms, dados)
        db.commit() 
        return jsonify({'message': 'adm inserido com sucesso'}), 201
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    finally:
        cursor.close()


#rota "/aluno" adiciona um novo aluno no sistema 
@MY_APP.route('/aluno', methods=['POST'])
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


#rota "/aluno/id" metodo GET faz uma busca no sistema pelo id do aluno   
@MY_APP.route('/aluno/<int:id>', methods=['GET'])
@jwt_required()
def buscar(id):
    try:
        cursor = db.cursor()
        if not id:
            return jsonify(message='Campo id é obrigatórios'), 400

        cursor.execute('select * from aluno where Cod_aluno=%s', (id))
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


#rota "/aluno/id" metodo PUT atualiza os dados do alunos
@MY_APP.route('/aluno/<int:id>', methods=['PUT'])
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
        cursor.execute('UPDATE aluno SET nome = %s, email = %s, telefone = %s WHERE Cod_aluno = %s', (nome, email, telefone, id))
        db.commit()
        if cursor.rowcount > 0:
            return jsonify(message='Aluno atualizado com sucesso'), 200
        else:
            return jsonify(message='Aluno não encontrado'), 404
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    finally:
        cursor.close()


#rota "/aluno/id" metodo DELETE exclui o aluno do sistema
@MY_APP.route('/aluno/<int:id>', methods=['DELETE'])
@jwt_required()
def deletar(id):
    try:
        cursor = db.cursor()
        if not id:
            return jsonify({'message': 'Aluno não encontrado'}), 404
        cursor.execute('delete from aluno where Cod_= %s', (id))
        db.commit()
        if cursor.rowcount > 0:
            return jsonify(message='Aluno deletado com sucesso'), 200
        else:
            return jsonify(message='Aluno não encontrado'), 404
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    finally:
        cursor.close()


#rota "/login" realiza a autenticação do administrador no sistema 
@MY_APP.route('/login', methods=['POST'])
def login():
    try:
        login_data = request.get_json()
        cursor = db.cursor()
        if 'username' not in login_data or 'password' not in login_data:
            return jsonify({'message': 'Nome de usuário e senha são obrigatórios'}), 400
        username = login_data['username']
        password = login_data['password']
        cursor.execute('SELECT password FROM administrativo WHERE username = %s', (username,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'message': 'Nome de usuário ou senha incorretos'}), 401
        hashed_password_from_db = result[0]
        hashed_password_input = sha256(password.encode('utf-8')).hexdigest()        
        if hashed_password_input == hashed_password_from_db:
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({'message': 'Nome de usuário ou senha incorretos'}), 401
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    finally:
        cursor.close()


# @MY_APP.route('/loginTest', methods=['POST'])
# def loginTest():
#     try:
#         login_data = request.get_json()
#         username = login_data['username']
#         password = login_data['password']

#         if username is None or password is None:
#             return jsonify({'message': 'Nome de usuário e senha são obrigatórios'}), 400

#         user = next((t for t in UserTest if t['username'] == username and t['password'] == password), None)
#         if not user:
#             return jsonify({'message': 'Nome de usuário ou senha incorretos'}), 401

#         access_token = create_access_token(identity=username)
#         return jsonify(access_token=access_token), 200
#     except Exception as err:
#         return jsonify({'message': str(err)}), 500

#rota "/logado" indica que é o administrador que esta logado no momento
@MY_APP.route('/logado', methods=['GET'])
@jwt_required()
def protected():
    try:
        current_user = get_jwt_identity()
        return jsonify(f'Logado como: {current_user}'), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500