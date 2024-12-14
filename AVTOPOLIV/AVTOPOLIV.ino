#include <NewPing.h>

// Пины подключения
#define RELAY_PIN 3            // Реле для управления помпой
#define SOIL_SENSOR_PIN A0     // Датчик влажности почвы
#define WATER_SENSOR_PIN A1    // Water Sensor
#define TRIG_PIN 4             // Trig HC-SR04
#define ECHO_PIN 5             // Echo HC-SR04

// Параметры резервуара
const int TANK_HEIGHT = 10;    // Высота банки в см
const int MIN_WATER_LEVEL = 3; // Минимальный допустимый уровень воды в см

// Калибровка датчика влажности почвы
const int DRY_SOIL = 1000;      // Значение для сухой почвы
const int WET_SOIL = 200;       // Значение для влажной почвы
const int MODERATE_SOIL = 600;  // Умеренная влажность (примерное значение)

// Пороговые значения для Water Sensor
const int WATER_SENSOR_THRESHOLD = 300; // Порог для наличия воды (0-1023)

// Тайминг
unsigned long lastUpdateTime = 0; // Время последнего обновления
const unsigned long UPDATE_INTERVAL = 30000; // Интервал обновления (1 минута)

NewPing sonar(TRIG_PIN, ECHO_PIN, TANK_HEIGHT * 2);

void setup() {
  Serial.begin(9600); // Инициализация серийного монитора

  pinMode(RELAY_PIN, OUTPUT); // Настройка пина реле как выход
  digitalWrite(RELAY_PIN, LOW); // Отключаем помпу (реле выключено)

  pinMode(SOIL_SENSOR_PIN, INPUT); // Датчик влажности почвы как вход
  pinMode(WATER_SENSOR_PIN, INPUT); // Water Sensor как вход

  pinMode(TRIG_PIN, OUTPUT); // Trig HC-SR04 как выход
  pinMode(ECHO_PIN, INPUT);  // Echo HC-SR04 как вход
}

void loop() {
  // Проверяем, прошло ли достаточно времени для обновления данных
  unsigned long currentTime = millis();
  if (currentTime - lastUpdateTime >= UPDATE_INTERVAL) {
    lastUpdateTime = currentTime;

    // Считывание данных с датчиков
    int soilMoisture = analogRead(SOIL_SENSOR_PIN);
    int waterSensorValue = analogRead(WATER_SENSOR_PIN);
    int waterLevel = 0; // Уровень воды, измеряется только если Water Sensor показывает наличие воды

    // Проверяем наличие воды в емкости с помощью Water Sensor
    if (waterSensorValue > WATER_SENSOR_THRESHOLD) {
      waterLevel = measureWaterLevel(); // Уровень воды с HC-SR04
      Serial.println("Вода обнаружена. Измеряем уровень воды...");
    } else {
      Serial.println("Вода не обнаружена!");
      waterLevel = 0; // Если воды нет, уровень воды = 0
    }

    // Калибровка и вывод значений влажности почвы
    Serial.print("Влажность почвы: ");
    Serial.println(soilMoisture);

    if (soilMoisture >= DRY_SOIL) {
      Serial.println("Почва сухая.");
    } else if (soilMoisture <= WET_SOIL) {
      Serial.println("Почва влажная.");
    } else {
      Serial.println("Почва в промежуточном состоянии.");
    }

    Serial.print("Значение Water Sensor: ");
    Serial.println(waterSensorValue);

    Serial.print("Уровень воды (см): ");
    Serial.println(waterLevel);

    // Логика работы
    if (soilMoisture >= DRY_SOIL) { // Если почва сухая
      if (waterLevel > MIN_WATER_LEVEL) { // Если уровень воды выше минимального
        Serial.println("Почва сухая. Запускаем помпу.");
        digitalWrite(RELAY_PIN, LOW); // Включаем помпу
      } else {
        Serial.println("Недостаточно воды в резервуаре! Помпа выключена.");
        digitalWrite(RELAY_PIN, LOW); // Отключаем помпу
      }
    } else {
      Serial.println("Почва влажная или в промежуточном состоянии. Помпа выключена.");
      digitalWrite(RELAY_PIN, HIGH); // Отключаем помпу
    }

    Serial.println("-------------------------");
  }
}

// Функция измерения уровня воды с помощью HC-SR04
int measureWaterLevel() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH); // Время в микросекундах
  int distance = duration * 0.034 / 2;    // Расстояние в см

  int waterLevel = TANK_HEIGHT - distance; // Уровень воды
  if (waterLevel < 0) waterLevel = 0;     // Ограничиваем минимальное значение
  return waterLevel;
}