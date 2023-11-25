from flask import Flask
from flask_jwt_extended import JWTManager
from controller.aluno_controller import MY_APP

try:
    app = Flask(__name__)
    app.register_blueprint(MY_APP) #referencia do controller
    app.json.sort_keys = False # desativa a ordem alfabetica de exibição JSON

    app.config["JWT_SECRET_KEY"] = "super-secret" #Senha secreta de autinticação com JWT
    jwt = JWTManager(app)


    if __name__ == '__main__':
        app.run(debug=True)
except Exception as err:
    print({'message': str(err)}), 500