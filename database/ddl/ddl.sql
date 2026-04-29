-- =========================================================
-- EXTENSÕES
-- =========================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- =========================================================
-- SCHEMA
-- =========================================================

CREATE SCHEMA IF NOT EXISTS iot;


-- =========================================================
-- TABELA: DISPOSITIVOS IOT
-- =========================================================

CREATE TABLE iot.iot_dispositivo (

    id BIGSERIAL PRIMARY KEY,

    uuid UUID NOT NULL UNIQUE
        DEFAULT gen_random_uuid(),

    nome VARCHAR(100) NOT NULL,

    descricao TEXT,

    token_hash VARCHAR(255) NOT NULL UNIQUE,

    ativo BOOLEAN NOT NULL DEFAULT TRUE,

    data_criacao TIMESTAMP NOT NULL DEFAULT NOW(),

    ultimo_contato TIMESTAMP
);


-- =========================================================
-- TABELA: LEITURAS DE UMIDADE
-- =========================================================

CREATE TABLE iot.leitura_umidade (

    id BIGSERIAL PRIMARY KEY,

    uuid UUID NOT NULL UNIQUE
        DEFAULT gen_random_uuid(),

    dispositivo_id BIGINT NOT NULL,

    data_hora TIMESTAMP NOT NULL,

    umidade NUMERIC(5,2) NOT NULL,

    bateria NUMERIC(5,2),

    payload_json JSONB,

    data_recebimento TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_leitura_dispositivo
        FOREIGN KEY (dispositivo_id)
        REFERENCES iot.iot_dispositivo(id)
        ON DELETE CASCADE
);


-- =========================================================
-- TABELA: CONFIGURAÇÃO DE IRRIGAÇÃO
-- =========================================================

CREATE TABLE iot.configuracao_irrigacao (

    id BIGSERIAL PRIMARY KEY,

    uuid UUID NOT NULL UNIQUE
        DEFAULT gen_random_uuid(),

    dispositivo_id BIGINT NOT NULL,

    umidade_minima NUMERIC(5,2) NOT NULL,

    segundos_irrigacao INTEGER NOT NULL,

    intervalo_minimo_minutos INTEGER NOT NULL DEFAULT 30,

    ativo BOOLEAN NOT NULL DEFAULT TRUE,

    data_criacao TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_config_dispositivo
        FOREIGN KEY (dispositivo_id)
        REFERENCES iot.iot_dispositivo(id)
        ON DELETE CASCADE
);


-- =========================================================
-- TABELA: COMANDOS DE IRRIGAÇÃO
-- =========================================================

CREATE TABLE iot.comando_irrigacao (

    id BIGSERIAL PRIMARY KEY,

    uuid UUID NOT NULL UNIQUE
        DEFAULT gen_random_uuid(),

    dispositivo_id BIGINT NOT NULL,

    segundos_irrigacao INTEGER NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',

    origem VARCHAR(20) NOT NULL DEFAULT 'AUTO',

    data_criacao TIMESTAMP NOT NULL DEFAULT NOW(),

    data_envio TIMESTAMP,

    data_confirmacao TIMESTAMP,

    observacao TEXT,

    CONSTRAINT chk_comando_status
        CHECK (
            status IN (
                'PENDENTE',
                'ENVIADO',
                'EXECUTANDO',
                'FINALIZADO',
                'ERRO'
            )
        ),

    CONSTRAINT chk_comando_origem
        CHECK (
            origem IN (
                'AUTO',
                'MANUAL',
                'AGENDADO'
            )
        ),

    CONSTRAINT fk_comando_dispositivo
        FOREIGN KEY (dispositivo_id)
        REFERENCES iot.iot_dispositivo(id)
        ON DELETE CASCADE
);


-- =========================================================
-- TABELA: EXECUÇÃO REAL DA IRRIGAÇÃO
-- =========================================================

CREATE TABLE iot.execucao_irrigacao (

    id BIGSERIAL PRIMARY KEY,

    uuid UUID NOT NULL UNIQUE
        DEFAULT gen_random_uuid(),

    comando_id BIGINT NOT NULL,

    dispositivo_id BIGINT NOT NULL,

    data_inicio TIMESTAMP NOT NULL,

    data_fim TIMESTAMP,

    segundos_executados INTEGER,

    sucesso BOOLEAN,

    mensagem TEXT,

    payload_json JSONB,

    data_registro TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_execucao_comando
        FOREIGN KEY (comando_id)
        REFERENCES iot.comando_irrigacao(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_execucao_dispositivo
        FOREIGN KEY (dispositivo_id)
        REFERENCES iot.iot_dispositivo(id)
        ON DELETE CASCADE
);


-- =========================================================
-- ÍNDICES
-- =========================================================

CREATE INDEX idx_leitura_dispositivo_data
ON iot.leitura_umidade (
    dispositivo_id,
    data_hora DESC
);

CREATE INDEX idx_leitura_data
ON iot.leitura_umidade (
    data_hora DESC
);

CREATE INDEX idx_comando_status
ON iot.comando_irrigacao (
    status
);

CREATE INDEX idx_comando_dispositivo
ON iot.comando_irrigacao (
    dispositivo_id
);

CREATE INDEX idx_execucao_dispositivo
ON iot.execucao_irrigacao (
    dispositivo_id
);

CREATE INDEX idx_execucao_comando
ON iot.execucao_irrigacao (
    comando_id
);

CREATE INDEX idx_dispositivo_uuid
ON iot.iot_dispositivo (
    uuid
);


-- =========================================================
-- COMENTÁRIOS
-- =========================================================

COMMENT ON SCHEMA iot IS
'Sistema de irrigação IoT';

COMMENT ON TABLE iot.iot_dispositivo IS
'Dispositivos físicos IoT';

COMMENT ON TABLE iot.leitura_umidade IS
'Histórico de leituras de sensores';

COMMENT ON TABLE iot.configuracao_irrigacao IS
'Regras automáticas de irrigação';

COMMENT ON TABLE iot.comando_irrigacao IS
'Fila de comandos enviados ao dispositivo';

COMMENT ON TABLE iot.execucao_irrigacao IS
'Execução real da bomba de água';


-- =========================================================
-- EXEMPLO DE INSERÇÃO DE DISPOSITIVO
-- =========================================================

-- IMPORTANTE:
-- token_hash abaixo é apenas exemplo fictício

--INSERT INTO iot.iot_dispositivo (
--    nome,
--    descricao,
--    token_hash
--)
--VALUES (
--    'ESP32 - Vaso Sala',
--    'Controle de irrigação da planta da sala',
--    '4f8d0f8d8d5f4c5b2a7d9e0b3a2c1f0'
--);