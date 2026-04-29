# Sistema IoT de Irrigação Automatizada

## Descrição

Projeto de automação de irrigação utilizando:

* PostgreSQL
* Django
* APIs REST
* Dispositivos IoT (ESP32 / ESP8266)
* Sensores de umidade do solo
* Mini bomba de água

O objetivo do sistema é:

* Receber leituras de umidade enviadas pelos dispositivos IoT
* Armazenar histórico das leituras
* Determinar automaticamente quando irrigar
* Enviar comandos de irrigação aos dispositivos
* Registrar confirmação da execução da irrigação
* Permitir auditoria e rastreabilidade das operações

---

# Arquitetura

## Fluxo Geral

1. O dispositivo IoT mede a umidade da terra
2. O dispositivo envia os dados para a API Django
3. O sistema grava as leituras no PostgreSQL
4. O sistema verifica regras de irrigação
5. Caso necessário, cria um comando de irrigação
6. O dispositivo consulta periodicamente a API
7. O dispositivo executa a irrigação
8. O dispositivo confirma a execução
9. O sistema registra a execução da bomba

---

# Tecnologias

## Backend

* Python
* Django
* Django REST Framework

## Banco de Dados

* PostgreSQL

## IoT

* ESP32
* ESP8266

## Comunicação

* HTTP REST API
* JSON

---

# Estrutura do Banco

O banco utiliza um schema separado chamado:

```sql
CREATE SCHEMA iot;
```

Tabelas principais:

| Tabela                     | Finalidade                    |
| -------------------------- | ----------------------------- |
| iot.iot_dispositivo        | Cadastro dos dispositivos     |
| iot.leitura_umidade        | Histórico das leituras        |
| iot.configuracao_irrigacao | Regras automáticas            |
| iot.comando_irrigacao      | Fila de comandos              |
| iot.execucao_irrigacao     | Registro da execução da bomba |

---

# Segurança

## UUID

As APIs utilizam UUID ao invés de IDs inteiros expostos.

Exemplo:

```text
550e8400-e29b-41d4-a716-446655440000
```

Isso evita:

* Enumeração de registros
* URLs previsíveis
* Exposição do crescimento do sistema

---

## Tokens

Os tokens dos dispositivos não são armazenados em texto puro.

O banco armazena apenas:

```text
token_hash
```

---

# Extensão PostgreSQL

O projeto utiliza:

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

Motivos:

* geração automática de UUID
* funções criptográficas
* hash de tokens

---

# Exemplo de Fluxo da API

## Envio de leitura de umidade

### Request

```json
{
  "token": "abc123",
  "data_hora": "2026-04-29T08:00:00",
  "umidade": 28.5
}
```

### Processamento

O backend:

* valida o token
* identifica o dispositivo
* grava a leitura
* verifica configuração de irrigação
* cria comando se necessário

---

# Consulta de comandos

O dispositivo consulta:

```http
GET /api/iot/comandos
```

### Resposta

```json
{
  "comando_id": "550e8400-e29b-41d4-a716-446655440000",
  "ligar_bomba": true,
  "segundos": 5
}
```

---

# Confirmação de execução

Após irrigar:

```json
{
  "comando_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "FINALIZADO",
  "segundos_executados": 5
}
```

---

# Estrutura Recomendada do Projeto Django

```text
backend/
├── apps/
│   ├── iot/
│   ├── irrigacao/
│   └── api/
├── config/
├── requirements.txt
└── manage.py
```

---

# Melhorias Futuras

## MQTT

Substituir polling HTTP por MQTT.

---

## Dashboard Web

Criar gráficos de:

* umidade
* irrigações
* consumo de água
* atividade dos dispositivos

---

## Alertas

Enviar notificações quando:

* sensor parar de responder
* umidade estiver muito baixa
* bomba falhar

---

## Firmware OTA

Atualização remota do firmware dos dispositivos.

---

# Requisitos

## PostgreSQL

Versão recomendada:

* PostgreSQL 14+

## Python

Versão recomendada:

* Python 3.11+

---

# Instalação Inicial

## Criar banco

```sql
CREATE DATABASE irrigacao_iot;
```

---

## Executar DDL

Executar o arquivo SQL de criação das tabelas.

---

## Instalar dependências

```bash
pip install -r requirements.txt
```

---

## Executar migrations

```bash
python manage.py migrate
```

---

## Executar servidor

```bash
python manage.py runserver
```

---

# Objetivos do Projeto

* Estudo de IoT
* Automação residencial
* Integração Django + PostgreSQL + ESP32
* Monitoramento de sensores
* Controle automatizado de irrigação
* Arquitetura escalável para múltiplos dispositivos

---

# Licença

Projeto para fins educacionais e experimentais.

