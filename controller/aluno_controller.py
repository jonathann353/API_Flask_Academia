from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from hashlib import sha256
#from model.connection import conn ##conexão com o workbench 
from model.db_postgres import conn ##conexão com o postgres 
# from model.db_admin import UserTest ##descomente está linha para usar o usuário de teste

MY_APP = Blueprint('MY_APP', __name__)#link do controller com a main


#rota "/" raiz da aplicação lista os alunos cadastrados no sistema
@MY_APP.route('/', methods=['GET'])
@jwt_required()
def listar():
    try:
        cursor = conn.cursor()
        cursor.execute('select * from aluno')
        tabela = cursor.fetchall()
        lista_alunos = []
        for aluno in tabela:
            aluno_dict = {
                'Cod_aluno': aluno[0],
                'nome': aluno[1],
                'cpf': aluno[2],
                'email': aluno[3],
                'telefone': aluno[4]
            }
            lista_alunos.append(aluno_dict)
        return jsonify(mensagem='lista de alunos', dados=lista_alunos), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    finally:
        cursor.close()


#rota "/adm" faz a inserção de um novo administrador do sistema
@MY_APP.route('/criar_administrador', methods=['POST'])
@jwt_required()
def criar_administrador():
    try:
        adm = request.json
        if 'username' not in adm or 'password' not in adm:
            return jsonify(message='Campos obrigatórios: username e password'), 400

        password = adm["password"]
        hash_senha = sha256(password.encode()).hexdigest()

        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO administrativo(username, password) VALUES(%s, %s)', (adm["username"], hash_senha))
            conn.commit()

        return jsonify({'message': 'adm inserido com sucesso'}), 201

    except Exception as err:
        return jsonify({'message': str(err)}), 500


#rota "/aluno" adiciona um novo aluno no sistema 
@MY_APP.route('/aluno', methods=['POST'])
@jwt_required()
def inserir():
    try:
        cursor = conn.cursor()
        aluno = request.json
        if 'nome' not in aluno or 'cpf' not in aluno or 'email' not in aluno or 'telefone' not in aluno or 'Cod_instrutor' not in aluno:
            return jsonify({'message': 'Campos obrigatórios: nome, cpf, email e telefone, Cod_instrutor'}), 400
        cursor.execute('INSERT INTO aluno(nome, cpf, email, telefone, Cod_instrutor) VALUES(%s, %s, %s, %s, %s)', (aluno["nome"], aluno["cpf"], aluno["email"], aluno["telefone"], aluno["Cod_instrutor"]))
        conn.commit() 
        return jsonify({'message': 'Aluno inserido com sucesso'}), 201
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    finally:
        cursor.close()


#rota "/instrutor" metodo Post adiciona um novo instrutor no sistema   
@MY_APP.route('/instrutor', methods=['POST'])
@jwt_required()
def instrutor():
    instrutor = request.json
    cursor = conn.cursor()
    try:
        cursor = conn.cursor()
        instrutor = request.json
        if 'nome' not in instrutor or 'Num_Confef' not in instrutor or 'telefone' not in instrutor or 'funcao' not in instrutor:
            return jsonify(message='Campos obrigatórios: nome, cpf, email e telefone'), 400
        cursor.execute('INSERT INTO instrutor(nome, Num_Confef, telefone, funcao) VALUES(%s, %s, %s, %s)', (instrutor["nome"], instrutor["Num_Confef"], instrutor["telefone"], instrutor["funcao"]))
        conn.commit() 
        return jsonify({'message': 'instrutor inserido com sucesso'}), 201
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    finally:
        cursor.close()


#rota "/instrutor" metodo Post adiciona um novo treino no sistema  
@MY_APP.route('/treino', methods=['POST'])
@jwt_required()
def treino():
    try:
        treino = request.json
        cursor = conn.cursor()
        if 'tipo_treino'  not in treino or 'exercicio'  not in treino or 'serie'  not in treino or 'repeticao' not in treino or 'Cod_aluno' not in treino or 'Cod_instrutor' not in treino:
            return jsonify(message='Campos obrigatórios: tipo_treino, exercicio, serie, repeticoes, Cod_aluno e Cod_instrutor'), 400
        cursor.execute('INSERT INTO treino(tipo_treino, exercicio, serie, repeticao, Cod_aluno, Cod_instrutor) VALUES(%s, %s, %s, %s, %s, %s)', (treino["tipo_treino"], treino["exercicio"], treino["serie"], treino["repeticao"], treino["Cod_aluno"], treino["Cod_instrutor"])) 
        conn.commit()
        return jsonify({'message': 'treino inserido com sucesso'}), 201
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    finally:
        cursor.close()

#rota "/aluno/id" metodo GET faz uma busca no sistema pelo id do aluno   
@MY_APP.route('/aluno/<int:id>', methods=['GET'])
@jwt_required()
def buscar(id):
    try:
        cursor = conn.cursor()
        if not id:
            return jsonify(message='Campo id é obrigatórios'), 400

        cursor.execute('select * from aluno where Cod_aluno=%s', (id,))
        aluno = cursor.fetchall()
        if aluno:
            for dados in aluno:
                dados = {
                'Cod_aluno': dados[0],
                'nome': dados[1],
                'cpf': dados[2],
                'email': dados[3],
                'telefone': dados[4]
            }
            return jsonify(dados)
        return jsonify(message='Aluno não encontrado'), 404
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    finally:
        cursor.close()


#rota "/aluno/id" metodo GET faz uma busca no sistema pelo id do aluno   
@MY_APP.route('/detalhes_aluno_e_instrutores/<int:id>', methods=['GET'])
# @jwt_required()
def detalhes_aluno_e_instrutores(id):
    try:
        cursor = conn.cursor()
        if not id:
            return jsonify(message='Campo id é obrigatórios'), 400

        cursor.execute('SELECT aluno.nome AS NomeAluno, aluno.cpf AS CpfAluno, aluno.email AS EmailAluno, aluno.telefone AS TelefoneAluno, instrutor.nome AS NomeInstrutor, instrutor.funcao AS FuncaoInstrutor FROM aluno JOIN instrutor ON aluno.Cod_instrutor = instrutor.Cod_instrutor WHERE aluno.Cod_aluno = %s', (id,))
        aluno = cursor.fetchall()
        if aluno:
            for dados in aluno:
                dados = {
                'nome aluno': dados[0],
                'cpf aluno': dados[1],
                'email aluno': dados[2],
                'telefone aluno': dados[3],
                'intrutor': {
                    'nome instrutor': dados[4],
                    'função instrutor': dados[5]
                }
            }
            return jsonify(mesagem='relação de aluno e instrutor', lista=dados)
        return jsonify(message='Aluno não encontrado'), 404
    except Exception as err:
        return jsonify({'message': str(err)}), 500
    finally:
        cursor.close()


@MY_APP.route('/detalhes_treino_aluno/<int:id>', methods=['GET'])
#@jwt_required()
def detalhes_treino_aluno(id):
    try:
        cursor = conn.cursor()
        if not id:
            return jsonify(message='Campo id é obrigatórios'), 400

        cursor.execute('SELECT aluno.nome AS NomeAluno, instrutor.nome AS NomeInstrutor, treino.tipo_de_treino, treino.exercicios, treino.serie, treino.repeticoes FROM treino JOIN aluno ON treino.Cod_aluno = aluno.Cod_aluno JOIN instrutor ON aluno.Cod_instrutor = instrutor.Cod_instrutor WHERE aluno.Cod_aluno = %s', (id,))
        aluno = cursor.fetchall()
        if aluno:
            for dados in aluno:
                dados = {
                'nome aluno': dados[0],
                'nome instrutor': dados[1],
                'treino': {
                    'tipo_treino': dados[2],
                    'exercicio': dados[3],
                    'serie': dados[4],
                    'repeticao': dados[5],
                }
            }
            return jsonify(mesagem='treino aluno', lista=dados)
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
        cursor = conn.cursor()
        nome = request.json.get('nome')  
        email = request.json.get('email')
        telefone = request.json.get('telefone')
        Cod_instrutor = request.json.get('Cod_instrutor')
        if nome != nome or email != email or telefone != telefone or Cod_instrutor != Cod_instrutor:
            return jsonify(message='Campo "nome", "e-mail" e "telefone" é obrigatório'), 400
        if not id:
            return jsonify(message='Campo "id" é obrigatório'), 400
        if nome:
            cursor.execute('UPDATE aluno SET nome = %s WHERE Cod_aluno = %s', (nome, id))
            conn.commit()
        if email:
            cursor.execute('UPDATE aluno SET email = %s WHERE Cod_aluno = %s', (email, id))
            conn.commit()
        if telefone:
            cursor.execute('UPDATE aluno SET telefone = %s WHERE Cod_aluno = %s', (telefone, id))
            conn.commit()
        if instrutor:
            cursor.execute('UPDATE aluno SET Cod_instrutor = %s WHERE Cod_aluno = %s', (Cod_instrutor, id))
            conn.commit()
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
        cursor = conn.cursor()
        if not id:
            return jsonify({'message': 'Aluno não encontrado'}), 404
        cursor.execute('delete from aluno where Cod_aluno=%s', (id,))
        conn.commit()
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
        cursor = conn.cursor()
        if 'username' not in login_data or 'password' not in login_data:
            return jsonify({'message': 'Nome de usuário e senha são obrigatórios'}), 400
        username = login_data['username']
        password = login_data['password']
        cursor.execute('SELECT password FROM administrativo WHERE username = %s', (username,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'message': 'Nome de usuário ou senha incorretos'}), 401
        hashed_password_from_conn = result[0]
        hashed_password_input = sha256(password.encode('utf-8')).hexdigest()        
        if hashed_password_input == hashed_password_from_conn:
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
