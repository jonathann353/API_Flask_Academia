API Flask para Gerenciamento de Alunos
Esta é uma API Flask simples para gerenciamento de alunos, onde você pode realizar operações CRUD (Criar, Ler, Atualizar, Deletar) sobre informações de alunos.

Endpoints
Aqui estão alguns dos principais endpoints disponíveis nesta API.

Listar Alunos
GET '/' 
Retorna uma lista de todos os alunos cadastrados no sistema.
--------------------------------------------------------------
POST '/criar_administrador'
Permite a criação de um novo administrador do sistema.

Parâmetros
Campo	Tipo	Descrição
username	string	Nome de usuário do administrador.
password	string	Senha do administrador.
Adicionar Aluno
--------------------------------------------------------------
POST '/aluno'
Adiciona um novo aluno ao sistema.

Parâmetros
Campo	Tipo	Descrição
nome	string	Nome do aluno.
cpf	string	CPF do aluno.
email	string	E-mail do aluno.
telefone	string	Número de telefone do aluno.
Cod_instrutor	int	Código do instrutor do aluno.

--------------------------------------------------------------
POST '/instrutor'
Adiciona um novo instrutor ao sistema.

Parâmetros
Campo	Tipo	Descrição
nome	string	Nome do instrutor.
Num_Confef	string	Número Confef do instrutor.
telefone	string	Número de telefone do instrutor.
funcao	string	Função do instrutor.

--------------------------------------------------------------
POST '/treino'
Adiciona um novo treino ao sistema.

Parâmetros
Campo	Tipo	Descrição
tipo_treino	string	Tipo de treino.
exercicio	string	Nome do exercício.
serie	int	Número de séries do exercício.
repeticao	int	Número de repetições do exercício.
Cod_aluno	int	Código do aluno associado ao treino.
Cod_instrutor	int	Código do instrutor associado ao treino.
Detalhes do Aluno e Instrutores
--------------------------------------------------------------
GET '/detalhes_aluno_e_instrutores/{id}'
Retorna detalhes de um aluno e os instrutores associados a esse aluno.

Parâmetros
Campo	Tipo	Descrição
id	int	Identificador único do aluno.
Detalhes do Treino do Aluno
--------------------------------------------------------------
GET '/detalhes_treino_aluno/{id}'
Retorna detalhes do treino associado a um aluno.

Parâmetros
Campo	Tipo	Descrição
id	int	Identificador único do aluno.
Atualizar Aluno
--------------------------------------------------------------
PUT '/aluno/{id}'
Atualiza os detalhes de um aluno.

Parâmetros
Campo	Tipo	Descrição
id	int	Identificador único do aluno.
nome	string	Novo nome do aluno.
email	string	Novo e-mail do aluno.
telefone	string	Novo número de telefone do aluno.
Cod_instrutor	int	Novo código do instrutor do aluno.
Excluir Aluno
--------------------------------------------------------------
DELETE '/aluno/{id}'
Exclui um aluno do sistema.

Parâmetros
Campo	Tipo	Descrição
id	int	Identificador único do aluno.
Login do Administrador
--------------------------------------------------------------
POST '/login'
Realiza a autenticação do administrador no sistema.

Parâmetros
Campo	Tipo	Descrição
username	string	Nome de usuário do administrador.
password	string	Senha do administrador.
Status de Logado
--------------------------------------------------------------
GET '/logado'
Indica qual administrador está logado no momento.