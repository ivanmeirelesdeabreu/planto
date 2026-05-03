#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#include <LiquidCrystal_I2C.h>
#include <Wire.h>
#include <time.h>

// =====================
// LCD
// =====================
LiquidCrystal_I2C lcd(0x27, 16, 2);

// =====================
// WIFI
// =====================
const char* WIFI_SSID = "IMA";
const char* WIFI_PASSWORD = "12345678";

// =====================
// API
// =====================
const char* API_BASE_URL = "http://SEU_IP_OU_HOST:8000/api";
const char* DEVICE_TOKEN = "TOKEN_DO_DISPOSITIVO";

String endpointLeitura() {
  return String(API_BASE_URL) + "/iot/leituras";
}

String endpointComandos() {
  return String(API_BASE_URL) + "/iot/comandos";
}

String endpointExecucoes() {
  return String(API_BASE_URL) + "/iot/execucoes";
}

// =====================
// PINOS WEMOS D1 R2
// =====================
const int PINO_SENSOR = A0;
const int PINO_BOMBA = D5;

// =====================
// NTP
// =====================
const long GMT_OFFSET_SEC = -3 * 3600;
const int DAYLIGHT_OFFSET_SEC = 0;

// =====================
// LEITURA SENSOR
// =====================
int lerUmidade() {

  int valor = analogRead(PINO_SENSOR);

  return valor;
}

// =====================
// WIFI
// =====================
void conectarWiFi() {

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Conectando WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi conectado");
  Serial.println(WiFi.localIP());
}

// =====================
// NTP
// =====================
void sincronizarHorario() {

  configTime(
    GMT_OFFSET_SEC,
    DAYLIGHT_OFFSET_SEC,
    "pool.ntp.org",
    "br.pool.ntp.org"
  );

  Serial.print("Sincronizando horario");

  time_t now = time(nullptr);

  while (now < 100000) {
    delay(500);
    Serial.print(".");
    now = time(nullptr);
  }

  Serial.println("\nHorario sincronizado");
}

// =====================
// DATA ISO
// =====================
String horarioISO8601() {

  time_t now = time(nullptr);

  struct tm* t = localtime(&now);

  char buffer[25];

  sprintf(
    buffer,
    "%04d-%02d-%02dT%02d:%02d:%02d",
    t->tm_year + 1900,
    t->tm_mon + 1,
    t->tm_mday,
    t->tm_hour,
    t->tm_min,
    t->tm_sec
  );

  return String(buffer);
}

// =====================
// LCD
// =====================
void atualizarLCD(int valor) {

  int porcentagem =
    map(valor, 1024, 700, 0, 100);

  porcentagem =
    constrain(porcentagem, 0, 100);

  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print("Umidade Solo");

  lcd.setCursor(0, 1);
  lcd.print(porcentagem);
  lcd.print("%");
}

// =====================
// ENVIO API
// =====================
void enviarLeitura() {

  if (WiFi.status() != WL_CONNECTED)
    return;

  int valor = lerUmidade();

  WiFiClient client;
  HTTPClient http;

  StaticJsonDocument<256> json;

  json["token"] = DEVICE_TOKEN;
  json["umidade"] = valor;
  json["data_hora"] = horarioISO8601();

  String payload;

  serializeJson(json, payload);

  http.begin(client, endpointLeitura());

  http.addHeader(
    "Content-Type",
    "application/json"
  );

  int httpCode = http.POST(payload);

  Serial.print("HTTP ");
  Serial.println(httpCode);

  http.end();
}

// =====================
// CONSULTAR COMANDOS
// =====================
void consultarComandos() {

  if (WiFi.status() != WL_CONNECTED)
    return;

  WiFiClient client;
  HTTPClient http;

  http.begin(
    client,
    endpointComandos() +
    "?token=" +
    DEVICE_TOKEN
  );

  int httpCode = http.GET();

  if (httpCode != 200) {
    http.end();
    return;
  }

  StaticJsonDocument<256> json;

  deserializeJson(
    json,
    http.getString()
  );

  http.end();

  if (json["ligar_bomba"]) {

    executarComando(
      json["comando_id"],
      json["segundos"]
    );
  }
}

// =====================
// EXECUTAR IRRIGACAO
// =====================
void executarComando(
  const char* comandoId,
  int segundos
) {

  Serial.println("Bomba ligada");

  digitalWrite(PINO_BOMBA, HIGH);

  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Irrigando...");

  delay(segundos * 1000);

  digitalWrite(PINO_BOMBA, LOW);

  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Bomba OFF");

  confirmarExecucao(
    comandoId,
    segundos
  );
}

// =====================
// CONFIRMAR
// =====================
void confirmarExecucao(
  const char* comandoId,
  int segundos
) {

  WiFiClient client;
  HTTPClient http;

  StaticJsonDocument<256> json;

  json["token"] = DEVICE_TOKEN;
  json["comando_id"] = comandoId;
  json["status"] = "FINALIZADO";
  json["segundos_executados"] = segundos;

  String payload;

  serializeJson(json, payload);

  http.begin(
    client,
    endpointExecucoes()
  );

  http.addHeader(
    "Content-Type",
    "application/json"
  );

  http.POST(payload);

  http.end();

  Serial.println("Execucao confirmada");
}

// =====================
// SETUP
// =====================
void setup() {

  Serial.begin(115200);

  pinMode(PINO_BOMBA, OUTPUT);

  digitalWrite(PINO_BOMBA, LOW);

  Wire.begin(D2, D1);

  lcd.init();
  lcd.backlight();

  lcd.setCursor(0,0);
  lcd.print("Inicializando");

  conectarWiFi();

  sincronizarHorario();
}

// =====================
// LOOP
// =====================
void loop() {

  int valor = lerUmidade();

  Serial.print("Umidade: ");
  Serial.println(valor);

  atualizarLCD(valor);

  enviarLeitura();

  consultarComandos();

  delay(30000);
}