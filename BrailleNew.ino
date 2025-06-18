// Definir los pines de los solenoides (pines 2 a 7)
const int solenoidePins[] = {2, 3, 4, 5, 6, 7};
const int numSolenoides = 6;

void setup() {
  // Inicializar los pines de los solenoides como salida
  for (int i = 0; i < numSolenoides; i++) {
    pinMode(solenoidePins[i], OUTPUT);
    digitalWrite(solenoidePins[i], LOW);  // Apagar los solenoides al principio
  }

  // Iniciar la comunicación serial
  Serial.begin(9600);  // Coincida con la velocidad usada en Python
}

void loop() {
  // Revisar si hay datos disponibles en el puerto serial
  if (Serial.available() > 0) {
    // Leer el dato que llega (se espera una cadena de 6 caracteres: "100000", "101000", etc.)
    String brailleChar = Serial.readStringUntil('\n');  // Leer hasta el salto de línea

    // Asegurarse de que la cadena tiene 6 caracteres
    brailleChar.trim();  // Eliminar espacios y saltos de línea extra
    if (brailleChar.length() == 6) {
      // Activar los solenoides correspondientes
      for (int i = 0; i < numSolenoides; i++) {
        if (brailleChar[i] == '1') {
          digitalWrite(solenoidePins[i], HIGH);  // Activar el solenoide
        } else {
          digitalWrite(solenoidePins[i], LOW);   // Asegurar que esté apagado
        }
      }

      delay(2000);  // Mantener activación de la letra durante 2 segundos

      // Apagar todos los solenoides entre letras
      for (int i = 0; i < numSolenoides; i++) {
        digitalWrite(solenoidePins[i], LOW);
      }

      delay(500);  // Esperar medio segundo antes de la siguiente letra
    }
  }
}

