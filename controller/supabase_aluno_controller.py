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
import uuid
import jwt
import os
import re

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
                    'sobrenome':aluno['sobrenome'],
                    'documento': aluno['documento'],
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
    
@MY_APP.route('/inserir/aluno', methods=['POST'])
def inserir_Aluno():
    aluno = request.json

    try:
        campos_obrigatorios = [
            'nome', 'sobrenome', 'documento', 'email',
            'telefone','status','data_nascimento',
            'sexo', 'Cod_plano'
        ]

        valido, mensagem = validar_campos(campos_obrigatorios, aluno)
        if not valido:
            return jsonify({'erro': mensagem}), 400

        documento = aluno['documento']

        if not validar_documento(documento):
            return jsonify({'erro': ' ou CNPJ inválido'}), 400

        documento_limpo = somente_numeros(documento)

        # ✅ Verificar duplicidade
        existente = supabase.table('aluno') \
            .select('cod_aluno') \
            .eq('documento', documento_limpo) \
            .execute()

        if existente.data:
            return jsonify({'erro': 'Documento já cadastrado'}), 409

        status_str = aluno['status']
        status_bool = True if status_str.lower() == 'ativo' else False

        supabase.table('aluno').insert({
            'nome': aluno["nome"],
            'sobrenome': aluno["sobrenome"],
            'documento': documento_limpo,
            'email': aluno['email'],
            'telefone': aluno["telefone"],
            'Cod_instrutor': aluno.get('Cod_instrutor'),
            'status': status_bool,
            'data_nascimento': aluno['data_nascimento'],
            'sexo': aluno['sexo'],
            'Cod_plano': aluno['Cod_plano']
        }).execute()

        return jsonify({'message': 'Aluno inserido com sucesso'}), 201

    except Exception as err:
        return jsonify({'erro': str(err)}), 500
    
    
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
                'sobrenome':aluno['sobrenome'],
                'documento': aluno['documento'],
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
            'sobrenome': aluno['sobrenome'],
            'cpf_aluno': aluno['documento'],
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

        # 🔍 Buscar dados do aluno
        response_aluno = supabase.table('aluno').select('nome').eq('cod_aluno', id).execute()
        if not response_aluno.data:
            return jsonify(message='Aluno não encontrado'), 404

        nome_aluno = response_aluno.data[0]['nome']

        # 🔍 Buscar treinos do aluno
        response_treino = supabase.table('treino').select('*').eq('cod_aluno', id).execute()
        if not response_treino.data:
            return jsonify(message='Treinos não encontrados'), 404

        treinos = response_treino.data

        resultado = []

        for treino in treinos:
            cod_treino = treino.get('cod_treino')
            cod_instrutor = treino.get('cod_instrutor')

            # 🔍 Buscar nome do instrutor
            if cod_instrutor:
                response_instrutor = supabase.table('instrutor').select('nome').eq('cod_instrutor', cod_instrutor).execute()
                nome_instrutor = response_instrutor.data[0]['nome'] if response_instrutor.data else 'Não informado'
            else:
                nome_instrutor = 'Não informado'

            # 🔍 Buscar exercícios vinculados a este treino
            response_exercicios = supabase.table('exercicio').select('*').eq('cod_treino', cod_treino).execute()
            exercicios = response_exercicios.data if response_exercicios.data else []

            lista_exercicios = []
            for ex in exercicios:
                lista_exercicios.append({
                    'cod_exercicio': ex.get('cod_exercicio'),
                    'serie': ex.get('serie'),
                    'repeticao': ex.get('repeticao'),
                    'exercicio': ex.get('exercicio'),
                    'intervalo': ex.get('intervalo'),
                    'carga': ex.get('carga'),
                    'concluido': ex.get('concluido')
                })

            # 🔍 Verificar se TODOS os exercícios estão concluídos
            treino_concluido = all(ex.get('concluido') for ex in exercicios) if exercicios else False

            resultado.append({
                'nome_aluno': nome_aluno,
                'nome_instrutor': nome_instrutor,
                'treino': {
                    'cod_treino': cod_treino,
                    'tipo_treino': treino.get('tipo_treino'),
                    'objetivo': treino.get('objetivo'),
                    'observacoes': treino.get('observacoes'),
                    'data_inicio': treino.get('data_inicio'),
                    'data_final': treino.get('data_final'),
                    'dia_semana': treino.get('dia_semana'),
                    'treino_concluido': treino_concluido,
                    'exercicios': lista_exercicios
                }
            })

        return jsonify(resultado), 200

    except Exception as err:
        return jsonify({'message': str(err)}), 500


@MY_APP.route('/atualizar/exercicio/<int:cod_exercicio>', methods=['PUT'])
def atualizar_exercicio(cod_exercicio):
    try:
        dados = request.json

        if not cod_exercicio:
            return jsonify({'message': 'O código do exercício é obrigatório'}), 400

        # ✅ Campos que podem ser atualizados (incluindo 'concluido')
        campos_permitidos = [
            'nome_exercicio', 'serie', 'repeticoes',
            'carga', 'observacao', 'concluido'
        ]

        dados_update = {campo: dados[campo] for campo in campos_permitidos if campo in dados}

        if not dados_update:
            return jsonify({'message': 'Nenhum dado válido para atualizar'}), 400

        # 🔥 Executa o update no Supabase
        response = supabase.table('exercicio').update(dados_update).eq('cod_exercicio', cod_exercicio).execute()

        if response.data:
            return jsonify({'message': 'Exercício atualizado com sucesso!', 'dados': response.data}), 200
        else:
            return jsonify({'message': 'Exercício não encontrado ou não atualizado'}), 404

    except Exception as err:
        return jsonify({'message': f'Erro ao atualizar exercício: {str(err)}'}), 500

    
# Rota "/aluno/id" - método PUT atualiza os dados do aluno
@MY_APP.route('/atualizar/aluno/<int:id>', methods=['PUT'])
# @jwt_required()
def atualizar_Aluno(id):
    try:
        nome = request.json.get('nome')
        sobrenome = request.json.get('sobrenome')
        email = request.json.get('email')
        telefone = request.json.get('telefone')
        Cod_instrutor = request.json.get('Cod_instrutor')
        status= request.json.get('status')
       

        if not nome or not email or not telefone or not Cod_instrutor:
            return jsonify(message='Campos obrigatórios: nome, sobrenome, email, telefone e Cod_instrutor'), 400

        # Atualizar no Supabase
        response = supabase.table('aluno').update({
            'nome': nome,
            'sobrenome': sobrenome,
            'email': email,
            'telefone': telefone,
            'Cod_instrutor': Cod_instrutor,
            'status':status
        }).eq('cod_aluno', id).execute()

        return jsonify(mensagem='Aluno atualizado com sucesso'), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota "/atualizar/aluno/id" - método PATCH atualiza apenas os campos enviados
@MY_APP.route('/atualizar/aluno/<int:cod_aluno>', methods=['PATCH'])
# @jwt_required()
def atualizar_aluno_parcial(cod_aluno):
    try:
        data = request.get_json()

        if not data:
            return jsonify(mensagem="Nenhum dado enviado para atualização"), 400

        # Atualiza apenas os campos enviados no JSON
        response = (
            supabase.table('aluno')
            .update(data)
            .eq('cod_aluno', cod_aluno)
            .execute()
        )

        if not response.data:
            return jsonify(mensagem="Aluno não encontrado ou sem alterações"), 404

        return jsonify(
            mensagem="Aluno atualizado com sucesso",
            aluno=response.data[0]
        ), 200

    except Exception as err:
        return jsonify({'erro': str(err)}), 500

@MY_APP.route('/criar/treino/aluno', methods=['POST'])
def criar_treino_aluno():
    try:
        data = request.json

        obrig = ['tipo_treino', 'cod_aluno', 'cod_instrutor', 'data_inicio', 'dia_semana']
        for c in obrig:
            if not data.get(c):
                return jsonify(message=f"Campo {c} é obrigatório"), 400

        # usa o cod_treino se vier do Django, senão cria um UUID
        cod_treino = data.get("cod_treino") or str(uuid.uuid4())

        treino = {
            "cod_treino": cod_treino,
            "tipo_treino": data['tipo_treino'],
            "cod_aluno": data['cod_aluno'],
            "cod_instrutor": data['cod_instrutor'],
            "objetivo": data.get("objetivo", ""),
            "observacoes": data.get("observacoes", ""),
            "data_inicio": data['data_inicio'],
            "data_final": data.get("data_final"),
            "dia_semana": data['dia_semana']
        }

        supabase.table("treino").insert(treino).execute()

        return jsonify(message="Treino criado com sucesso", cod_treino=cod_treino), 201

    except Exception as e:
        return jsonify(message=f"Erro interno: {e}"), 500

@MY_APP.route('/criar/exercicio/treino', methods=['POST'])
def criar_exercicio_treino():
    try:
        data = request.json

        # aceita payload único ou lista
        if "exercicios" in data:
            lista = data["exercicios"]
        else:
            lista = [data]

        for ex in lista:
            obrig = ['cod_treino', 'exercicio', 'serie', 'repeticao', 'intervalo', 'carga']
            for campo in obrig:
                if ex.get(campo) in [None, ""]:
                    return jsonify(message=f"O campo {campo} é obrigatório"), 400

            ex["serie"] = int(ex["serie"])
            ex["repeticao"] = int(ex["repeticao"])
            ex["carga"] = float(ex["carga"])

        supabase.table("exercicio").insert(lista).execute()

        return jsonify(message="Exercícios criados com sucesso"), 201

    except Exception as e:
        return jsonify(message=f"Erro interno: {e}"), 500

# Nova Rota "/alunos/do/instrutor/id" - método GET
@MY_APP.route('/alunos/do/instrutor/<int:id>', methods=['GET'])
# @jwt_required()
def listar_alunos_por_instrutor(id):
    try:
        # Buscar todos os alunos com o Cod_instrutor informado
        response_alunos = supabase.table('aluno').select("*").eq("Cod_instrutor", id).execute()

        if not response_alunos.data:
            return jsonify(message='Nenhum aluno vinculado a este instrutor'), 404

        # Construir a lista de alunos
        lista_alunos = []
        for aluno in response_alunos.data:
            lista_alunos.append({
                'cod_aluno': aluno.get('cod_aluno'),
                'nome': aluno.get('nome'),
                'sobrenome': aluno.get('sobrenome'),
                'cpf': aluno.get('documento'),
                'email': aluno.get('email'),
                'telefone': aluno.get('telefone'),
            })

        return jsonify({'instrutor_id': id, 'alunos': lista_alunos}), 200

    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Nova Rota "/avaliacao/do/instrutor/id" - método POST
@MY_APP.route('/avaliacao/do/instrutor/<int:cod_instrutor>', methods=['POST'])
# @jwt_required()
def salvar_avaliacao(cod_instrutor):
    try:
        data = request.get_json()

        # Validação dos dados obrigatórios
        campos_obrigatorios = ['cod_aluno', 'data_avaliacao', 'peso', 'altura', 'imc', 'meta']
        for campo in campos_obrigatorios:
            if campo not in data or data[campo] == "" or data[campo] is None:
                return jsonify({'message': f'O campo {campo} é obrigatório.'}), 400

        # Montar o payload para salvar na tabela de avaliação
        payload = {
            'cod_instrutor':cod_instrutor,
            'cod_aluno': data.get('cod_aluno'),
            'data_avaliacao': data.get('data_avaliacao'),
            'peso': float(data.get('peso')),
            'altura': float(data.get('altura')),
            'imc': float(data.get('imc')),
            'meta': data.get('meta'),
            'observacoes': data.get('observacoes', '')  # Observações é opcional
        }

        # Inserir no banco (supabase)
        response = supabase.table('avaliacao_fisica').insert(payload).execute()

        if response.data:
            return jsonify({
                'message': 'Avaliação salva com sucesso!',
                'avaliacao': response.data
            }), 201
        else:
            return jsonify({'message': 'Erro ao salvar avaliação.'}), 500

    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota "/avaliacoes/do/aluno/<id>" - método GET
@MY_APP.route('/avaliacoes/do/aluno/<int:cod_aluno>', methods=['GET'])
# @jwt_required()  # Descomente se estiver usando autenticação JWT
def buscar_avaliacoes(cod_aluno):
    try:
        # Consulta no Supabase as avaliações do aluno específico
        response = supabase.table('avaliacao_fisica') \
            .select('*') \
            .eq('cod_aluno', cod_aluno) \
            .order('data_avaliacao', desc=True) \
            .execute()

        avaliacoes = response.data

        if not avaliacoes:
            return jsonify({
                'message': 'Nenhuma avaliação encontrada para este aluno.',
                'avaliacoes': []
            }), 404

        return jsonify({
            'message': 'Avaliações encontradas com sucesso.',
            'avaliacoes': avaliacoes
        }), 200

    except Exception as err:
        return jsonify({'message': f'Erro ao buscar avaliações: {str(err)}'}), 500
        
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
        is_superuser = data.get('is_superuser', False)  

        if not username or not email or not password:
            return jsonify({"error": "Missing required fields"}), 400

        # Verifique se o usuário já existe
        existing_user = supabase.table("auth_user").select("*").eq("username", username).execute()
        if existing_user.data:
            return jsonify({"error": "User already exists"}), 409

        # Gerar hash da senha com sha256
        hashed_password = sha256(password.encode('utf-8')).hexdigest()

        # Inserir o novo usuário com is_superuser vindo do request
        response = supabase.table("auth_user").insert({
            "username": username,
            "email": email,
            "password": hashed_password,
            "is_superuser": is_superuser, 
            "is_staff": is_superuser,      
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


# Remove tudo que não for número
def somente_numeros(valor):
    return re.sub(r'\D', '', valor)


def validar_cpf(cpf):
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # Primeiro dígito
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10 % 11) % 10

    # Segundo dígito
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10 % 11) % 10

    return cpf[-2:] == f"{digito1}{digito2}"


def validar_cnpj(cnpj):
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1

    soma1 = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
    digito1 = 11 - (soma1 % 11)
    digito1 = 0 if digito1 >= 10 else digito1

    soma2 = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
    digito2 = 11 - (soma2 % 11)
    digito2 = 0 if digito2 >= 10 else digito2

    return cnpj[-2:] == f"{digito1}{digito2}"


def validar_documento(documento):
    doc = somente_numeros(documento)

    if len(doc) == 11:
        return validar_cpf(doc)
    elif len(doc) == 14:
        return validar_cnpj(doc)
    return False
