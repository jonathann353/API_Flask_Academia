CREATE TABLE aluno (
    Cod_aluno serial PRIMARY KEY,
    nome VARCHAR(100),
    cpf VARCHAR(14),
    email VARCHAR(100),
    telefone VARCHAR(20),
    Cod_instrutor INT,  -- Chave estrangeira referenciando a tabela instrutor
    UNIQUE (telefone, email, cpf, nome)
);

CREATE TABLE instrutor (
    Cod_instrutor serial PRIMARY KEY,
    nome VARCHAR(100),
    Num_Confef VARCHAR(100),
    telefone VARCHAR(100),
    funcao VARCHAR(100),
    UNIQUE (Num_Confef, nome, telefone)
);

CREATE TABLE treino (
    Cod_treino serial PRIMARY KEY,
    tipo_de_treino VARCHAR(100),
    exercicios VARCHAR(100),
    serie INTEGER,
    repeticoes INTEGER,
    Cod_aluno INTEGER,  -- Chave estrangeira referenciando a tabela aluno
    Cod_instrutor INTEGER,  -- Chave estrangeira referenciando a tabela instrutor
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
password VARCHAR(64), 
UNIQUE (username)
);
