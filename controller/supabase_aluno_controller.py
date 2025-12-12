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
from datetime import datetime, timedelta
from random import randint
import uuid
import jwt
import os
import re
import sys
import time

MY_APP = Blueprint('MY_APP', __name__)

# -------------------------------------------
# 🔐 Carregar variáveis de ambiente
# -------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("🔍 DEBUG:")
print("URL =", SUPABASE_URL)
print("KEY começa com =", SUPABASE_KEY[:10] if SUPABASE_KEY else None)
print("KEY tamanho =", len(SUPABASE_KEY) if SUPABASE_KEY else None)

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERRO: SUPABASE_URL ou SUPABASE_KEY não foram definidas!")
    sys.exit(1)

# -------------------------------------------
# 🧠 Inicialização preguiçosa (lazy-loading)
# -------------------------------------------
_supabase: Client | None = None

def supabase() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Cliente Supabase inicializado!")
    return _supabase


logging.basicConfig(level=logging.DEBUG)

# -------------------------------------------
# Função utilitária
# -------------------------------------------
def validar_campos(campos, dados):
    for campo in campos:
        if campo not in dados:
            return False, f"Campo obrigatório: {campo}"
    return True, None


# ============================================================
# 🚀 ROTAS
# ============================================================

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

        response = supabase().table('administrativo').insert({
            'username': adm['username'],
            'password': hash_senha
        }).execute()

        return jsonify(message='Administrador criado com sucesso'), 200
    except Exception as err:
        return jsonify(message=str(err)), 500


@MY_APP.route('/listar/aluno', methods=['GET'])
def listar_Aluno():
    try:
        response = supabase().table('aluno').select("*").execute()
        if response.data:
            lista_alunos = [
                {
                    'cod_aluno': aluno['cod_aluno'],
                    'nome': aluno['nome'],
                    'sobrenome': aluno['sobrenome'],
                    'documento': aluno['documento'],
                    'email': aluno['email'],
                    'telefone': aluno['telefone'],
                    'Cod_instrutor': aluno['Cod_instrutor'],
                    'status': aluno['status'],
                    'data_nascimento': aluno['data_nascimento'],
                    'sexo': aluno['sexo']
                } for aluno in response.data
            ]
            return jsonify(mensagem='lista de alunos', dados=lista_alunos), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500


@MY_APP.route('/listar/instrutor', methods=['GET'])
def listar_Instrutor():
    try:
        response = supabase().table('instrutor').select("*").execute()
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


@MY_APP.route('/inserir/instrutor', methods=['POST'])
def inserir_Instrutor():
    try:
        instrutor = request.json
        campos_obrigatorios = ['nome', 'num_confef', 'telefone', 'funcao']
        valido, mensagem = validar_campos(campos_obrigatorios, instrutor)
        if not valido:
            return jsonify(message=mensagem), 400

        response = supabase().table('instrutor').insert({
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
    try:
        aluno = request.json

        campos_obrigatorios = [
            'nome', 'sobrenome', 'documento', 'email',
            'telefone', 'status', 'data_nascimento',
            'sexo', 'Cod_plano'
        ]

        valido, mensagem = validar_campos(campos_obrigatorios, aluno)
        if not valido:
            return jsonify({'erro': mensagem}), 400

        documento = aluno['documento']

        if not validar_documento(documento):
            return jsonify({'erro': 'CPF ou CNPJ inválido'}), 400

        documento_limpo = somente_numeros(documento)

        existente = supabase().table('aluno') \
            .select('cod_aluno') \
            .eq('documento', documento_limpo) \
            .execute()

        if existente.data:
            return jsonify({'erro': 'Documento já cadastrado'}), 409

        status_str = aluno['status']
        status_bool = True if status_str.lower() == 'ativo' else False

        supabase().table('aluno').insert({
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


@MY_APP.route('/busca/aluno/<int:id>', methods=['GET'])
def buscar_Aluno(id):
    try:
        response = supabase().table('aluno').select('*').eq('cod_aluno', id).execute()

        if response.data:
            aluno = [{
                'cod_aluno': a['cod_aluno'],
                'nome': a['nome'],
                'sobrenome': a['sobrenome'],
                'documento': a['documento'],
                'email': a['email'],
                'telefone': a['telefone'],
                'Cod_instrutor': a['Cod_instrutor'],
                'status': a['status'],
                'data_nascimento': a['data_nascimento'],
                'sexo': a['sexo']
            } for a in response.data]

            return jsonify(mensagem='Aluno encontrado', dados=aluno), 200

        return jsonify(message="Aluno não encontrado"), 404

    except Exception as err:
        return jsonify({'message': str(err)}), 500

# Rota "/detalhes/aluno/e/instrutores/id"
@MY_APP.route('/detalhes/aluno/e/instrutores/<int:id>', methods=['GET'])
def detalhes_Aluno_e_Instrutores(id):
    try:
        response_aluno = supabase().table('aluno').select("*").eq("cod_aluno", id).execute()
        
        if not response_aluno.data:
            return jsonify(message='Aluno não encontrado'), 404

        aluno = response_aluno.data[0]
        cod_instrutor = aluno.get("Cod_instrutor")

        instrutor = {}
        if cod_instrutor:
            response_instrutor = (
                supabase().table('instrutor')
                .select("nome, funcao")
                .eq("cod_instrutor", cod_instrutor)
                .execute()
            )
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


# Rota "/detalhes/treino/aluno/id"
@MY_APP.route('/detalhes/treino/aluno/<int:id>', methods=['GET'])
def detalhes_Treino_Aluno(id):
    try:
        response_aluno = supabase().table('aluno').select('nome').eq('cod_aluno', id).execute()
        if not response_aluno.data:
            return jsonify(message='Aluno não encontrado'), 404

        nome_aluno = response_aluno.data[0]['nome']

        response_treino = supabase().table('treino').select('*').eq('cod_aluno', id).execute()
        if not response_treino.data:
            return jsonify(message='Treinos não encontrados'), 404

        treinos = response_treino.data
        resultado = []

        for treino in treinos:
            cod_treino = treino.get('cod_treino')
            cod_instrutor = treino.get('cod_instrutor')

            if cod_instrutor:
                response_instrutor = supabase().table('instrutor').select('nome').eq('cod_instrutor', cod_instrutor).execute()
                nome_instrutor = response_instrutor.data[0]['nome'] if response_instrutor.data else 'Não informado'
            else:
                nome_instrutor = 'Não informado'

            response_exercicios = supabase().table('exercicio').select('*').eq('cod_treino', cod_treino).execute()
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


# Atualizar exercício
@MY_APP.route('/atualizar/exercicio/<int:cod_exercicio>', methods=['PUT'])
def atualizar_exercicio(cod_exercicio):
    try:
        dados = request.json

        campos_permitidos = [
            'nome_exercicio', 'serie', 'repeticoes',
            'carga', 'observacao', 'concluido'
        ]

        dados_update = {campo: dados[campo] for campo in campos_permitidos if campo in dados}

        if not dados_update:
            return jsonify({'message': 'Nenhum dado válido para atualizar'}), 400

        response = supabase().table('exercicio').update(dados_update).eq('cod_exercicio', cod_exercicio).execute()

        if response.data:
            return jsonify({'message': 'Exercício atualizado', 'dados': response.data}), 200
        else:
            return jsonify({'message': 'Exercício não encontrado'}), 404

    except Exception as err:
        return jsonify({'message': f'Erro ao atualizar exercício: {str(err)}'}), 500


# Atualizar aluno com foto
@MY_APP.route('/atualizar/aluno/<int:id>', methods=['PUT'])
def atualizar_Aluno(id):
    try:
        nome = request.form.get('nome')
        sobrenome = request.form.get('sobrenome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        Cod_instrutor = request.form.get('Cod_instrutor')
        status = request.form.get('status')

        foto = request.files.get('foto')

        if not nome or not sobrenome or not email or not telefone or not Cod_instrutor:
            return jsonify(message='Campos obrigatórios faltando'), 400

        foto_url = None
        if foto:
            nome_sanitizado = re.sub(r'[^a-zA-Z0-9_-]', '', nome)
            ext = foto.filename.rsplit('.', 1)[-1].lower()
            timestamp = int(time.time())

            filename = f"{nome_sanitizado}_{timestamp}.{ext}"

            supabase().storage.from_("foto de perfil aluno").upload(
                filename,
                foto.read(),
                file_options={"content-type": foto.content_type}
            )

            foto_url = supabase().storage.from_("foto de perfil aluno").get_public_url(filename).get('publicUrl')

        update_data = {
            'nome': nome,
            'sobrenome': sobrenome,
            'email': email,
            'telefone': telefone,
            'Cod_instrutor': Cod_instrutor,
            'status': status
        }

        if foto_url:
            update_data["foto"] = foto_url

        supabase().table('aluno').update(update_data).eq('cod_aluno', id).execute()

        return jsonify(mensagem='Aluno atualizado', foto=foto_url), 200

    except Exception as err:
        return jsonify({'message': str(err)}), 500


# Atualização parcial (PATCH)
@MY_APP.route('/atualizar/aluno/<int:cod_aluno>', methods=['PATCH'])
def atualizar_aluno_parcial(cod_aluno):
    try:
        data = request.get_json()

        if not data:
            return jsonify(mensagem="Nenhum dado enviado"), 400

        response = supabase().table('aluno').update(data).eq('cod_aluno', cod_aluno).execute()

        if not response.data:
            return jsonify(mensagem="Aluno não encontrado"), 404

        return jsonify(mensagem="Aluno atualizado", aluno=response.data[0]), 200

    except Exception as err:
        return jsonify({'erro': str(err)}), 500


# Criar treino
@MY_APP.route('/criar/treino/aluno', methods=['POST'])
def criar_treino_aluno():
    try:
        data = request.json
        obrig = ['tipo_treino', 'cod_aluno', 'cod_instrutor', 'data_inicio', 'dia_semana']

        for c in obrig:
            if not data.get(c):
                return jsonify(message=f"Campo {c} é obrigatório"), 400

        cod_treino = data.get("cod_treino")
        if cod_treino is None:
            cod_treino = randint(100000, 999999)
        else:
            cod_treino = int(cod_treino)

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

        supabase().table("treino").insert(treino).execute()

        return jsonify(message="Treino criado", cod_treino=cod_treino), 201

    except Exception as err:
        return jsonify(message=f"Erro: {e}"), 500


# Criar exercícios
@MY_APP.route('/criar/exercicio/treino', methods=['POST'])
def criar_exercicio_treino():
    try:
        data = request.json

        lista = data["exercicios"] if "exercicios" in data else [data]

        for ex in lista:
            obrig = ['cod_treino', 'exercicio', 'serie', 'repeticao', 'intervalo', 'carga']

            for campo in obrig:
                if ex.get(campo) in [None, ""]:
                    return jsonify(message=f"O campo {campo} é obrigatório"), 400

            ex["cod_treino"] = int(ex["cod_treino"])
            ex["serie"] = int(ex["serie"])
            ex["repeticao"] = int(ex["repeticao"])
            ex["carga"] = float(ex["carga"])

        supabase().table("exercicio").insert(lista).execute()

        return jsonify(message="Exercícios criados"), 201

    except Exception as err:
        return jsonify(message=f"Erro: {e}"), 500


@MY_APP.route('/alunos/do/instrutor/<int:id>', methods=['GET'])
def listar_alunos_por_instrutor(id):
    try:
        response = supabase().table('aluno').select("*").eq("Cod_instrutor", id).execute()

        if not response.data:
            return jsonify(message='Nenhum aluno encontrado'), 404

        lista = [{
            'cod_aluno': a.get('cod_aluno'),
            'nome': a.get('nome'),
            'sobrenome': a.get('sobrenome'),
            'cpf': a.get('documento'),
            'email': a.get('email'),
            'telefone': a.get('telefone'),
        } for a in response.data]

        return jsonify({'instrutor_id': id, 'alunos': lista}), 200

    except Exception as err:
        return jsonify({'message': str(err)}), 500


# Avaliação física
@MY_APP.route('/avaliacao/do/instrutor/<int:cod_instrutor>', methods=['POST'])
def salvar_avaliacao(cod_instrutor):
    try:
        data = request.get_json()

        campos = ['cod_aluno', 'data_avaliacao', 'peso', 'altura', 'imc', 'meta']
        for campo in campos:
            if campo not in data:
                return jsonify({'message': f'O campo {campo} é obrigatório.'}), 400

        payload = {
            'cod_instrutor': cod_instrutor,
            'cod_aluno': data['cod_aluno'],
            'data_avaliacao': data['data_avaliacao'],
            'peso': float(data['peso']),
            'altura': float(data['altura']),
            'imc': float(data['imc']),
            'meta': data['meta'],
            'observacoes': data.get('observacoes', '')
        }

        response = supabase().table('avaliacao_fisica').insert(payload).execute()

        return jsonify({'message': 'Avaliação salva', 'avaliacao': response.data}), 201

    except Exception as err:
        return jsonify({'message': str(err)}), 500


# Buscar avaliações
@MY_APP.route('/avaliacoes/do/aluno/<int:cod_aluno>', methods=['GET'])
def buscar_avaliacoes(cod_aluno):
    try:
        response = (
            supabase().table('avaliacao_fisica')
            .select('*')
            .eq('cod_aluno', cod_aluno)
            .order('data_avaliacao', desc=True)
            .execute()
        )

        if not response.data:
            return jsonify(message='Nenhuma avaliação encontrada', avaliacoes=[]), 404

        return jsonify(message='Avaliações encontradas', avaliacoes=response.data), 200

    except Exception as err:
        return jsonify({'message': f'Erro: {str(err)}'}), 500


# Deletar aluno
@MY_APP.route('/deletar/aluno/<int:id>', methods=['DELETE'])
def deletar_Aluno(id):
    try:
        response = supabase().table('aluno').delete().eq('cod_aluno', id).execute()

        if response.data:
            return jsonify(message='Aluno deletado'), 200

        return jsonify(message='Aluno não encontrado'), 404

    except Exception as err:
        return jsonify({'message': f'Erro ao deletar: {str(err)}'}), 500


# Login
@MY_APP.route('/login', methods=['POST'])
def login_user():
    try:
        login_data = request.get_json()

        username = login_data.get('username')
        password = login_data.get('password')

        if not username or not password:
            return jsonify({'message': 'Campos obrigatórios'}), 400

        response = supabase().table("auth_user").select("*").eq("username", username).execute()
        user = response.data

        if not user:
            return jsonify({'message': 'Usuário ou senha incorretos'}), 401

        hashed_password_from_db = user[0]['password']
        hashed_password_input = sha256(password.encode()).hexdigest()

        if hashed_password_input != hashed_password_from_db:
            return jsonify({'message': 'Usuário ou senha incorretos'}), 401

        access_token = create_access_token(identity=username, expires_delta=timedelta(hours=2))
        return jsonify({'access_token': access_token}), 200

    except Exception as err:
        return jsonify({'message': str(err)}), 500


# Registrar usuário
@MY_APP.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"error": "Campos obrigatórios"}), 400

        existing = supabase().table("auth_user").select("*").eq("username", username).execute()
        if existing.data:
            return jsonify({"error": "Usuário já existe"}), 409

        hashed_password = sha256(password.encode()).hexdigest()

        response = supabase().table("auth_user").insert({
            "username": username,
            "email": email,
            "password": hashed_password,
            "is_superuser": False,
            "is_staff": False,
            "is_active": True,
            "first_name": data.get("first_name", ""),
            "last_name": data.get("last_name", ""),
            "date_joined": datetime.now().isoformat()
        }).execute()

        return jsonify({'message': 'Usuário criado'}), 200

    except Exception as err:
        return jsonify({'message': str(err)}), 500


@MY_APP.route('/logado', methods=['GET'])
@jwt_required()
def protected():
    try:
        user = get_jwt_identity()
        return jsonify(f'Logado como: {user}'), 200
    except Exception as err:
        return jsonify({'message': str(err)}), 500


# =============================================================
# FUNÇÕES AUXILIARES
# =============================================================

def somente_numeros(valor):
    return re.sub(r'\D', '', valor)

def validar_cpf(cpf):
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    dig1 = (soma * 10 % 11) % 10
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    dig2 = (soma * 10 % 11) % 10
    return cpf[-2:] == f"{dig1}{dig2}"

def validar_cnpj(cnpj):
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
    pesos1 = [5,4,3,2,9,8,7,6,5,4,3,2]
    pesos2 = [6] + pesos1
    soma1 = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
    d1 = 11 - (soma1 % 11)
    d1 = 0 if d1 >= 10 else d1
    soma2 = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
    d2 = 11 - (soma2 % 11)
    d2 = 0 if d2 >= 10 else d2
    return cnpj[-2:] == f"{d1}{d2}"

def validar_documento(documento):
    doc = somente_numeros(documento)
    if len(doc) == 11:
        return validar_cpf(doc)
    elif len(doc) == 14:
        return validar_cnpj(doc)
    return False
