#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#include <time.h>

// =====================
// CONFIGURAÇÕES WI-FI
// =====================
const char* WIFI_SSID = "IMA";
const char* WIFI_PASSWORD = "12345678";

// =====================
// CONFIGURAÇÕES API
// =====================
const char* API_BASE_URL = "http://SEU_IP_OU_HOST:8000/api";
const char* DEVICE_TOKEN = "TOKEN_DO_DISPOSITIVO";

// Endpoints
String endpointLeitura()   { return String(API_BASE_URL) + "/iot/leituras"; }
String endpointComandos()  { return String(API_BASE_URL) + "/iot/comandos"; }
String endpointExecucoes() { return String(API_BASE_URL) + "/iot/execucoes"; }

// =====================
// CONFIGURAÇÕES HARDWARE
// =====================
const int PINO_BOMBA = D1;

// =====================
// NTP (HORÁRIO)
// =====================
const long GMT_OFFSET_SEC = -3 * 3600;   // Brasília
const int  DAYLIGHT_OFFSET_SEC = 0;

// =====================
// FUNÇÕES
// =====================

float lerUmidadeFake() {
  return random(20, 60);
}

void conectarWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Conectando ao WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi conectado!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void sincronizarHorario() {
  configTime(GMT_OFFSET_SEC, DAYLIGHT_OFFSET_SEC,
             "pool.ntp.org",
             "time.nist.gov",
             "br.pool.ntp.org");

  Serial.print("Sincronizando horário NTP");

  time_t now = time(nullptr);
  while (now < 100000) {
    delay(500);
    Serial.print(".");
    now = time(nullptr);
  }

  Serial.println("\nHorário sincronizado com sucesso!");
}

String horarioISO8601() {
  time_t now = time(nullptr);
  struct tm* t = localtime(&now);

  char buffer[25];
  sprintf(buffer, "%04d-%02d-%02dT%02d:%02d:%02d",
          t->tm_year + 1900,
          t->tm_mon + 1,
          t->tm_mday,
          t->tm_hour,
          t->tm_min,
          t->tm_sec);

  return String(buffer);
}

// =====================
// ENVIO DE LEITURA
// =====================
void enviarLeitura() {
  if (WiFi.status() != WL_CONNECTED) return;

  WiFiClient client;
  HTTPClient http;

  StaticJsonDocument<256> json;
  json["token"] = DEVICE_TOKEN;
  json["umidade"] = lerUmidadeFake();
  json["data_hora"] = horarioISO8601();

  String payload;
  serializeJson(json, payload);

  http.begin(client, endpointLeitura());
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST(payload);
  Serial.print("Leitura enviada → HTTP ");
  Serial.println(httpCode);

  http.end();
}

// =====================
// CONSULTA DE COMANDOS
// =====================
void consultarComandos() {
  if (WiFi.status() != WL_CONNECTED) return;

  WiFiClient client;
  HTTPClient http;
  http.begin(client, endpointComandos() + "?token=" + DEVICE_TOKEN);

  int httpCode = http.GET();
  if (httpCode != 200) {
    http.end();
    return;
  }

  StaticJsonDocument<256> json;
  deserializeJson(json, http.getString());
  http.end();

  if (json["ligar_bomba"]) {
    executarComando(
      json["comando_id"],
      json["segundos"]
    );
  }
}

// =====================
// EXECUÇÃO DA IRRIGAÇÃO
// =====================
void executarComando(const char* comandoId, int segundos) {
  digitalWrite(PINO_BOMBA, HIGH);
  delay(segundos * 1000);
  digitalWrite(PINO_BOMBA, LOW);

  confirmarExecucao(comandoId, segundos);
}

// =====================
// CONFIRMAÇÃO
// =====================
void confirmarExecucao(const char* comandoId, int segundos) {
  WiFiClient client;
  HTTPClient http;

  StaticJsonDocument<256> json;
  json["token"] = DEVICE_TOKEN;
  json["comando_id"] = comandoId;
  json["status"] = "FINALIZADO";
  json["segundos_executados"] = segundos;

  String payload;
  serializeJson(json, payload);

  http.begin(client, endpointExecucoes());
  http.addHeader("Content-Type", "application/json");
  http.POST(payload);
  http.end();

  Serial.println("Execução confirmada.");
}

// =====================
// SETUP / LOOP
// =====================
void setup() {
  Serial.begin(9600);
  pinMode(PINO_BOMBA, OUTPUT);
  digitalWrite(PINO_BOMBA, LOW);

  conectarWiFi();
  sincronizarHorario();
}

void loop() {
  enviarLeitura();
  consultarComandos();
  delay(30000);  // 30 segundos
}