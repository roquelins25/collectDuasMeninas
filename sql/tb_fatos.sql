CREATE TABLE IF NOT EXISTS tbFatos (
    _id SERIAL PRIMARY KEY,
    status INTEGER,
    codterceiros VARCHAR(100),
    datacriacao DATE,
    nomfor VARCHAR(255),
    nomcli VARCHAR(255),
    codcli VARCHAR(100),
    datemi DATE,
    receita NUMERIC(15,2),
    custovendas NUMERIC(15,2),
    pmv NUMERIC(15,4),
    mc NUMERIC(15,2),
    codtipo VARCHAR(100),
    miudos NUMERIC(15,2),
    mccommiudo NUMERIC(15,2),
    boi NUMERIC(15,4)
);