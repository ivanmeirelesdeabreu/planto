# Sistema IoT de Irrigação Automatizada

Este repositório contém o código-fonte do backend de um **Sistema Inteligente de Irrigação Automatizada**, desenvolvido com foco em Internet das Coisas (IoT), automação residencial e boas práticas de engenharia de software.

O sistema integra dispositivos embarcados (ESP32/ESP8266), sensores de umidade do solo, banco de dados PostgreSQL e uma API REST desenvolvida em Python com Django.

---

## Objetivo do Projeto

O objetivo principal do projeto é permitir o **monitoramento contínuo da umidade do solo** e o **acionamento inteligente de um sistema de irrigação**, de forma automática ou manual, garantindo:

- uso eficiente de água;
- automação de baixo custo;
- registro e rastreabilidade das operações;
- escalabilidade para múltiplos dispositivos.

---

## Funcionalidades Principais

- Recepção de leituras de umidade enviadas por dispositivos IoT;
- Armazenamento histórico das leituras em banco de dados;
- Avaliação automática das regras de irrigação;
- Geração de comandos automáticos ou manuais;
- Comunicação bidirecional entre servidor e dispositivos;
- Registro da execução e auditoria da irrigação.

---

## Arquitetura do Sistema

### Fluxo Geral

1. O dispositivo IoT mede a umidade do solo;
2. O dispositivo envia os dados para a API REST;
3. O backend valida e armazena as leituras no PostgreSQL;
4. O sistema avalia as regras de irrigação configuradas;
5. Caso necessário, cria um comando de irrigação;
6. O dispositivo consulta periodicamente a API (polling);
7. O dispositivo executa a irrigação;
8. O dispositivo confirma a execução;
9. O sistema registra o histórico de execuções.

---

## Tecnologias Utilizadas

### Backend
- Python 3.11+
- Django
- Django REST Framework

### Banco de Dados
- PostgreSQL 14+
- Extensão `pgcrypto` (UUID e funções criptográficas)

### IoT
- ESP32 / ESP8266
- Sensores de umidade do solo
- Atuadores (relé e bomba d’água)

### Comunicação
- HTTP
- REST API
- JSON

---

## Estrutura do Banco de Dados

O banco utiliza um schema dedicado:


CREATE SCHEMA iot;

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
Autenticação por Token com Hash + Pepper

Cada dispositivo possui um token secreto;
O token não é armazenado em texto puro;
O banco armazena apenas o token_hash;
O hash é gerado utilizando SHA-256 combinado com um pepper interno;
O pepper permanece apenas no backend.

Esse modelo garante que mesmo em caso de vazamento do banco, os dispositivos não possam ser falsificados.

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
CREATE DATABASE planto;
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

