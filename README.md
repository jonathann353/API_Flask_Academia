## API Flask para Gerenciamento de Alunos ##
Esta é uma API Flask simples para gerenciamento de alunos, onde você pode realizar operações CRUD (Criar, Ler, Atualizar, Deletar) sobre informações de alunos.

Rotas Disponíveis
Listar Alunos
Rota: /
Método: GET
Autenticação: JWT Token obrigatório
Descrição: Obtém a lista de todos os alunos cadastrados.

Inserir Aluno
Rota: /aluno
Método: POST
Autenticação: JWT Token obrigatório
Parâmetros no Corpo da Requisição (JSON):

nome (obrigatório): Nome do aluno.
cpf (obrigatório): CPF do aluno.
email (obrigatório): E-mail do aluno.
telefone (obrigatório): Número de telefone do aluno.
Descrição: Insere um novo aluno no sistema.

Buscar Aluno por ID
Rota: /aluno/<int:id>
Método: GET
Autenticação: JWT Token obrigatório
Parâmetros de URL:

id (obrigatório): ID do aluno a ser buscado.
Descrição: Obtém as informações de um aluno específico com base no ID.

Atualizar Aluno por ID
Rota: /aluno/<int:id>
Método: PUT
Autenticação: JWT Token obrigatório
Parâmetros de URL:

id (obrigatório): ID do aluno a ser atualizado.
Parâmetros no Corpo da Requisição (JSON):
nome (obrigatório): Novo nome do aluno.
email (obrigatório): Novo e-mail do aluno.
telefone (obrigatório): Novo número de telefone do aluno.
Descrição: Atualiza as informações de um aluno específico com base no ID.

Deletar Aluno por ID
Rota: /aluno/<int:id>
Método: DELETE
Autenticação: JWT Token obrigatório
Parâmetros de URL:

id (obrigatório): ID do aluno a ser deletado.
Descrição: Deleta um aluno específico com base no ID.

Login
Rota: /login
Método: POST
Parâmetros no Corpo da Requisição (JSON):

username (obrigatório): Nome de usuário.
password (obrigatório): Senha.
Descrição: Realiza o login e fornece um token JWT para autenticação.

Verificar Login
Rota: /logado
Método: GET
Autenticação: JWT Token obrigatório
Descrição: Verifica se o usuário está autenticado e retorna o nome do usuário logado.

## Executando a Aplicação ##
Instale as dependências executando o sequinte comando:
pip install -r requirements.txt
