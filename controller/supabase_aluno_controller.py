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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
def inserir():
    try:
        aluno = request.json
        campos_obrigatorios = ['nome', 'cpf', 'email', 'telefone']
        valido, mensagem = validar_campos(campos_obrigatorios, aluno)
        if not valido:
            return jsonify({'message': mensagem}), 400
        
        # Inserindo novo aluno no Supabase
        response = supabase.table('aluno').insert([{
            'nome': aluno["nome"],
            'cpf': aluno["cpf"],
            'email': aluno["email"],
            'telefone': aluno["telefone"]
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

#rota "/instrutor" metodo Post adiciona um novo instrutor no sistema   
@MY_APP.route('/instrutor', methods=['POST'])
# @jwt_required()
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
# @jwt_required()
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
# @jwt_required()
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
@jwt_required()
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
@jwt_required()
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
# @jwt_required()
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
#@jwt_required()  # Requer um token fresco
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
