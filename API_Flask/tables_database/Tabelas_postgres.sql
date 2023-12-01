CREATE TABLE aluno (
    Cod_aluno serial PRIMARY KEY,
    nome VARCHAR(100) not null,
    cpf VARCHAR(14) not null,
    email VARCHAR(100) not null,
    telefone VARCHAR(20) not null,
    Cod_instrutor INT not null,  -- Chave estrangeira referenciando a tabela instrutor
    UNIQUE (telefone, email, cpf, nome)
);

CREATE TABLE instrutor (
    Cod_instrutor serial PRIMARY KEY,
    nome VARCHAR(100) not null,
    Num_Confef VARCHAR(100) not null,
    telefone VARCHAR(100) not null,
    funcao VARCHAR(100) not null,
    UNIQUE (Num_Confef, nome, telefone)
);

CREATE TABLE treino (
    Cod_treino serial PRIMARY KEY,
    tipo_treino VARCHAR(100) not null,
    exercicio VARCHAR(100) not null,
    serie INTEGER not null,
    repeticao INTEGER not null,
    Cod_aluno INTEGER not null,  -- Chave estrangeira referenciando a tabela aluno
    Cod_instrutor INTEGER not null,  -- Chave estrangeira referenciando a tabela instrutor
    FOREIGN KEY (Cod_aluno) REFERENCES aluno (Cod_aluno) ON DELETE RESTRICT,
    FOREIGN KEY (Cod_instrutor) REFERENCES instrutor (Cod_instrutor) ON DELETE RESTRICT
);
 
-- Chave estrangeira na tabela aluno referenciando a tabela instrutor
ALTER TABLE aluno ADD CONSTRAINT FK_aluno_instrutor
    FOREIGN KEY (Cod_instrutor)
    REFERENCES instrutor (Cod_instrutor)
    ON DELETE RESTRICT;
	
create table administrativo(
username VARCHAR(50) not null,
password VARCHAR(64) not null, 
UNIQUE (username)
);
