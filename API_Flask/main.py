from flask import Flask
from flask_jwt_extended import JWTManager
from controller.aluno_controller import aluno_app

try:
    app = Flask(__name__)
    app.register_blueprint(aluno_app)
    app.json.sort_keys = False

    app.config["JWT_SECRET_KEY"] = "super-secret" 
    jwt = JWTManager(app)


    if __name__ == '__main__':
        app.run(debug=True)
except Exception as err:
    print({'message': str(err)}), 500