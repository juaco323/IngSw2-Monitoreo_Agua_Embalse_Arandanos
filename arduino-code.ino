/*
  CÓDIGO ESP8266 - LECTURA DE SENSORES Y ENVÍO A MONGODB
  
  Código para ESP8266 que lee sensores de:
  - pH (entrada analógica A0)
  - Temperatura (OneWire en pin D4)
  - Conductividad Eléctrica (entrada analógica A0 - compartido)
  
  Los datos se envían vía HTTP PUT a la API FastAPI que guarda en MongoDB.
  
  INSTALACIÓN DE LIBRERÍAS:
  1. Abre Arduino IDE
  2. Sketch > Include Library > Manage Libraries
  3. Busca e instala "OneWire" por Jim Studt
  4. Busca e instala "DallasTemperature" por Miles Burton
  5. El ESP8266 incluye librerías de WiFi: ESP8266WiFi, ESP8266HTTPClient
  
  CONFIGURACIÓN ESP8266:
  - Board: NodeMCU 1.0 (ESP-12E Module) o similar
  - CPU Frequency: 80 MHz
  - Flash Size: 4M (FS:2MB OTA:~1019KB)
  
  CONEXIONES:
  - Sensor pH → A0 (entrada analógica)
  - Sensor Temperatura (DS18B20) → D4 (GPIO2)
  - Sensor Conductividad → A0 (entrada analógica compartida)
  - GND → GND
  - 3.3V → 3.3V (ESP8266)
*/

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// ============================================================================
// CONFIGURACIÓN DE WiFi
// ============================================================================

// CAMBIAR ESTOS VALORES SEGÚN TU RED WiFi
const char *ssid = "TU_SSID";                    // Nombre de tu red WiFi
const char *password = "TU_PASSWORD";            // Contraseña WiFi
const char *api_url = "http://192.168.1.100:8000";  // URL de la API FastAPI

// ============================================================================
// CONFIGURACIÓN DE PINES
// ============================================================================

const int PH_SENSOR_PIN = A0;           // Pin analógico para pH (A0)
const int TEMP_SENSOR_PIN = D4;         // Pin digital para sensor temperatura (D4/GPIO2)
const int LED_PIN = D8;                 // LED indicador de estado (D8/GPIO15)

// ============================================================================
// CONFIGURACIÓN DE SENSORES
// ============================================================================

OneWire oneWire(TEMP_SENSOR_PIN);
DallasTemperature temperatureSensors(&oneWire);

// Calibración pH (cambiar según tu sensor)
const float PH_OFFSET = 0.0;    // Offset de calibración
const float pH_AT_7 = 512.0;    // Valor ADC a pH 7

// ============================================================================
// VARIABLES GLOBALES
// ============================================================================

float phValue = 7.0;
float temperatureValue = 20.0;
float conductivityValue = 500.0;

unsigned long lastSensorReadTime = 0;
unsigned long lastHTTPSendTime = 0;
unsigned long wifiReconnectTime = 0;

const unsigned long SENSOR_READ_INTERVAL = 1000;   // Leer sensores cada 1s
const unsigned long HTTP_SEND_INTERVAL = 10000;    // Enviar datos cada 10s
const unsigned long WIFI_RECONNECT_INTERVAL = 5000; // Reintentar WiFi cada 5s

WiFiClient client;
HTTPClient http;

// ============================================================================
// SETUP
// ============================================================================

void setup() {
  Serial.begin(115200);      // Inicializar comunicación serial (115200 baud para ESP8266)
  delay(1000);
  
  Serial.println("\n\n");
  Serial.println("===========================================");
  Serial.println("ESP8266 - Monitoreo de Embalse Arandanos");
  Serial.println("===========================================");
  
  pinMode(LED_PIN, OUTPUT);  // Configurar LED como salida
  
  // Inicializar sensor de temperatura
  temperatureSensors.begin();
  
  // Conectar a WiFi
  connectToWiFi();
  
  Serial.println("Setup completado - Sistema listo");
  delay(500);
}

// ============================================================================
// FUNCIÓN PARA CONECTAR A WiFi
// ============================================================================

void connectToWiFi() {
  Serial.println("\n[WiFi] Intentando conectar a: " + String(ssid));
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("");
    Serial.println("[WiFi] Conectado exitosamente");
    Serial.println("[WiFi] IP: " + WiFi.localIP().toString());
    digitalWrite(LED_PIN, HIGH); // LED encendido cuando conectado
  } else {
    Serial.println("");
    Serial.println("[WiFi] Fallo en la conexión. Reintentando...");
  }
}

// ============================================================================
// LOOP PRINCIPAL
// ============================================================================

void loop() {
  unsigned long currentTime = millis();
  
  // Verificar conexión WiFi
  if (WiFi.status() != WL_CONNECTED) {
    if (currentTime - wifiReconnectTime >= WIFI_RECONNECT_INTERVAL) {
      Serial.println("[WiFi] Desconectado. Reintentando...");
      connectToWiFi();
      wifiReconnectTime = currentTime;
    }
  }
  
  // Leer sensores cada SENSOR_READ_INTERVAL ms
  if (currentTime - lastSensorReadTime >= SENSOR_READ_INTERVAL) {
    readAllSensors();
    lastSensorReadTime = currentTime;
    
    // Parpadear LED cuando se leen sensores
    if (WiFi.status() == WL_CONNECTED) {
      digitalWrite(LED_PIN, LOW);
      delayMicroseconds(100);
      digitalWrite(LED_PIN, HIGH);
    }
  }
  
  // Enviar datos por HTTP cada HTTP_SEND_INTERVAL ms
  if (currentTime - lastHTTPSendTime >= HTTP_SEND_INTERVAL) {
    if (WiFi.status() == WL_CONNECTED) {
      sendSensorDataToAPI();
    }
    lastHTTPSendTime = currentTime;
  }
}

// ============================================================================
// FUNCIONES DE LECTURA DE SENSORES
// ============================================================================

void readAllSensors() {
  readpHSensor();
  readTemperatureSensor();
  readConductivitySensor();
}

/*
  LECTURA DE pH
  
  El sensor de pH produce una salida de voltaje:
  - pH 7 = ~2.5V (512 en ADC con 10 bits)
  - pH 6 = ~3.0V
  - pH 8 = ~2.0V
  
  Ajusta los valores según la calibración de tu sensor
*/

void readpHSensor() {
  int phRaw = analogRead(PH_SENSOR_PIN);
  
  // Convertir valor ADC (0-1023) a pH
  // Fórmula: pH = 7.0 + (512 - ADC) * (0.0048)
  float voltage = (phRaw / 1023.0) * 5.0;
  phValue = 7.0 + (2.5 - voltage) * 2.0;
  
  // Limitar valores al rango 0-14
  phValue = constrain(phValue, 0, 14);
}

/*
  LECTURA DE TEMPERATURA
  
  Usa sensor DS18B20 (OneWire)
  El sensor es muy preciso (±0.5°C)
*/

void readTemperatureSensor() {
  temperatureSensors.requestTemperatures();
  temperatureValue = temperatureSensors.getTempCByIndex(0);
  
  // Verificar si hay error en la lectura
  if (temperatureValue == DEVICE_DISCONNECTED_C) {
    temperatureValue = 0.0;
  }
}

/*
  LECTURA DE CONDUCTIVIDAD ELÉCTRICA
  
  IMPORTANTE: ESP8266 tiene solo UNA entrada analógica (A0).
  
  Opciones:
  1. Usar un multiplexor analógico (recomendado para 3+ sensores)
  2. Leer alternativamente pH y conductividad en A0
  3. Usar ADC externo vía I2C/SPI
  
  Para esta versión, asumimos que usas un multiplexor o ADC externo.
  El sensor produce una salida de voltaje proporcional a la conductividad.
  Rango típico: 0-2000 µS/cm (microSiemens)
  
  Ajusta la escala según tu sensor específico
*/

void readConductivitySensor() {
  // NOTA: Esta función asume que tienes una forma de leer conductividad
  // En esta implementación, la conductividad se calcula como un valor
  // proporcional a la temperatura (para demostración).
  // Reemplaza esto con tu propia lógica si usas un ADC externo.
  
  // Versión de demostración: conductividad proporcional a temperatura
  conductivityValue = 500.0 + (temperatureValue * 50.0);
  conductivityValue = constrain(conductivityValue, 0, 2000);
}

// ============================================================================
// ENVÍO DE DATOS A LA API
// ============================================================================

/*
  Enviar datos vía HTTP PUT a la API FastAPI
  La API guardará los datos en MongoDB
*/

void sendSensorDataToAPI() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[HTTP] WiFi no conectado");
    return;
  }
  
  // Crear JSON con los datos de los sensores
  DynamicJsonDocument doc(256);
  doc["ph"] = round(phValue * 100) / 100.0;
  doc["temperature"] = round(temperatureValue * 100) / 100.0;
  doc["conductivity"] = round(conductivityValue * 100) / 100.0;
  doc["timestamp"] = millis() / 1000;
  
  String jsonData;
  serializeJson(doc, jsonData);
  
  Serial.println("[HTTP] Enviando datos:");
  Serial.println(jsonData);
  
  // Realizar HTTP PUT
  String url = String(api_url) + "/api/sensors/ph";
  http.begin(client, url);
  http.addHeader("Content-Type", "application/json");
  
  int httpCode = http.PUT(jsonData);
  
  if (httpCode > 0) {
    Serial.print("[HTTP] Respuesta: ");
    Serial.println(httpCode);
    
    if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_CREATED) {
      Serial.println("[HTTP] Datos guardados exitosamente en MongoDB");
      digitalWrite(LED_PIN, LOW);
      delay(100);
      digitalWrite(LED_PIN, HIGH);
    } else {
      String response = http.getString();
      Serial.println("[HTTP] Error: " + response);
    }
  } else {
    Serial.print("[HTTP] Error: ");
    Serial.println(http.errorToString(httpCode));
  }
  
  http.end();
}

// ============================================================================
// FUNCIONES AUXILIARES
// ============================================================================

/*
  Función para procesar comandos recibidos por serial (opcional)
  Permite cambiar configuraciones remotamente
*/

void processSerialCommand() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    
    if (command == "STATUS") {
      Serial.print("[SYS] WiFi: ");
      Serial.println(WiFi.status() == WL_CONNECTED ? "Conectado" : "Desconectado");
      Serial.print("[SYS] IP: ");
      Serial.println(WiFi.localIP().toString());
      Serial.print("[SYS] Señal: ");
      Serial.print(WiFi.RSSI());
      Serial.println(" dBm");
    }
    else if (command == "RECONNECT") {
      Serial.println("[CMD] Reconectando WiFi...");
      connectToWiFi();
    }
    else if (command == "INFO") {
      Serial.println("[INFO] Sistema: Monitoreo Embalse Arandanos");
      Serial.println("[INFO] Sensores: pH, Temperatura, Conductividad");
      Serial.println("[INFO] Destino: MongoDB vía API FastAPI");
    }
  }
}

// ============================================================================
// NOTAS IMPORTANTES PARA ESP8266
// ============================================================================

/*
  1. CONFIGURACIÓN INICIAL:
     - Cambiar SSID y PASSWORD con tu red WiFi
     - Cambiar api_url con la IP/hostname de tu servidor FastAPI
     - Asegúrate que el ESP8266 y servidor estén en la misma red

  2. INSTALACIÓN DE LIBRERÍAS ArduinoJson:
     - Sketch > Include Library > Manage Libraries
     - Busca "ArduinoJson" por Benoit Blanchon
     - Instala versión 6.x o superior

  3. PUERTOS ANALÓGICOS EN ESP8266:
     - Solo tiene UNA entrada analógica (A0)
     - Para 3 sensores necesitas:
       * ADC externo vía I2C (ADS1115 recomendado)
       * Multiplexor analógico
       * Leer alternadamente (más lento)

  4. DEBUGGING:
     - Abre Monitor Serial a 115200 baud
     - Verifica mensajes de conexión WiFi
     - Verifica respuestas HTTP de la API

  5. ALIMENTACIÓN:
     - ESP8266 requiere ~10-20mA en operación
     - Usa regulador LDO 3.3V de buena calidad
     - Capacitor de 10µF cercano al pin de alimentación
     - NO conectes 5V directamente (destruye el módulo)

  6. PROTOCOLO HTTP:
     - Asegúrate que API_URL sea accesible desde ESP8266
     - Usa HTTP no HTTPS (HTTPS requiere más memoria)
     - Timeout es 5 segundos (configurable)

  7. CALIBRACIÓN DE SENSORES:
     - pH: Referencia a pH 7, ajusta PH_OFFSET
     - Temperatura: DS18B20 no necesita calibración
     - Conductividad: Ajusta factor multiplicador según sensor

  8. TROUBLESHOOTING:
     Problema: ESP no se conecta a WiFi
     - Verifica SSID y contraseña
     - Verifica que el router use 2.4GHz (ESP8266 no soporta 5GHz)
     - Aumenta intentos de conexión en connectToWiFi()

     Problema: No envía datos a API
     - Verifica IP/URL de la API
     - Verifica que API esté ejecutándose
     - Revisa firewall/enrutador
     - Revisa logs de la API

     Problema: Datos incompletos o incorrectos
     - Verifica calibración de sensores
     - Confirma conexiones eléctricas
     - Prueba sensores individualmente
*/

// ============================================================================
// FIN DEL CÓDIGO
// ============================================================================
