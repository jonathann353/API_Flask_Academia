from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from controller.supabase_aluno_controller import MY_APP  # Certifique-se de que o import está correto
import os

def create_app():
    try:
        # Criando a instância do Flask
        app = Flask(__name__)

        # Registrando o blueprint para as rotas
        app.register_blueprint(MY_APP)  # Referência do controller

        # Configuração do JSON
        app.json.sort_keys = False  # Desativa a ordem alfabética de exibição do JSON

        # Configuração da chave secreta para JWT
        app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")  # Defina a chave secreta de autenticação com JWT
        jwt = JWTManager(app)  # Inicializando o gerenciador de JWT


        return app

    except Exception as err:
        # Em caso de erro, criar uma resposta adequada
        print(f"Erro: {str(err)}")
        return jsonify({"message": f"Erro interno: {str(err)}"}), 500

# A aplicação Flask é criada com a função `create_app`
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
