// El codigo se incluye para tenerlo disponible en caso de algun inconveniente, pero se ejecuta directamente en el arduino fisico.
// Normalmente seria brazo.ino

#include <Servo.h>
#include <EEPROM.h>
#include <avr/io.h>
#include <avr/interrupt.h>

// Servos
Servo servo1; // D11
Servo servo2; // D10
Servo servo3; // D9
Servo servo4; // D5

// Joysticks
const int joy1X = A0;
const int joy1Y = A1;
const int joy2X = A2;
const int joy2Y = A3;
const int joyButton = 2; // botón L3 joystick (PD2)

// Guardar posiciones
int pos1 = 140;
int pos2 = 110;
int pos3 = 90;
int pos4 = 90;

// Zona muerta y pasos
const int deadzone = 100;
const int step = 2;
const int threshold = 300; // sensibilidad para detectar dirección

// VARIABLES DE PILA
int pilaCount = 0;               // cuántas unidades hay apiladas
const int pilaMax = 5;           // máximo de unidades
const int alturaBase = 110;      // altura inicial del punto B
const int alturaIncremento = 15;  // cuánto sube por cada pieza

// Temporizador de ms (Timer2)
volatile uint32_t msCount = 0;

// ISR Timer2 CTC cada 1 ms
ISR(TIMER2_COMPA_vect) {
  msCount++;
}

// Delay que deja correr interrupciones
void delayNonBlocking(uint32_t t) {
  uint32_t start = msCount;
  while ((msCount - start) < t) {
    // Aquí NO se bloquean las interrupciones.
  }
}

// ADC rápido
// Configurar ADC en setup() y usa fastADC para lecturas rápidas
int fastADC(uint8_t channel) {
  // Selecciona canal manteniendo REFS bits
  ADMUX = (ADMUX & 0xF0) | (channel & 0x0F);
  ADCSRA |= (1 << ADSC);               // iniciar conversión
  while (ADCSRA & (1 << ADSC));        // esperar fin
  return ADC;                          // leer resultado (0-1023)
}

// Lectura de botón rápida
inline bool buttonPressed() {
  return !(PIND & (1 << 2)); // true si presionado
}

// Clamp rápido
inline int clampInt(int v, int lo, int hi) {
  if (v < lo) return lo;
  if (v > hi) return hi;
  return v;
}

// EEPROM
void guardarPilaCount() {
  EEPROM.update(0, (uint8_t)pilaCount);
  Serial.print("pilaCount guardado en EEPROM: ");
  Serial.println(pilaCount);
}

void cargarPilaCount() {
  pilaCount = EEPROM.read(0);
  if (pilaCount > 10) pilaCount = 0;
  Serial.print("pilaCount cargado desde EEPROM: ");
  Serial.println(pilaCount);
}

// Rutinas
void rutina1() {
  // A
  servo4.write(90);
  servo1.write(170);
  delayNonBlocking(500);
  servo2.write(110);
  delayNonBlocking(500);
  servo3.write(180);
  delayNonBlocking(500);
  servo3.write(90);
  delayNonBlocking(500);
  servo1.write(pos1);
  servo2.write(pos2);
}

void rutina2() {
  Serial.print("Desapilando... unidades en la pila: ");
  Serial.println(pilaCount);

  if (pilaCount <= 0) {
    Serial.println("No hay piezas para desapilar.");
    return;
  }

  // Ir al punto B
  servo2.write(160);
  delayNonBlocking(500);
  servo4.write(170);
  delayNonBlocking(500);

  // Calcular altura según pila actual
  int alturaActual = alturaBase + (pilaCount * alturaIncremento);
  int baseActual = 170 - (pilaCount * alturaIncremento);
  if (alturaActual < 110) alturaActual = 110;
  servo2.write(alturaActual);
  delayNonBlocking(500);
  servo1.write(baseActual);
  delayNonBlocking(500);

  // Cerrar pinza (tomar pieza)
  servo3.write(180);
  delayNonBlocking(500);

  // Elevar y girar hacia A
  servo2.write(160);
  delayNonBlocking(500);
  servo4.write(90);
  delayNonBlocking(500);

  // Bajar en A y soltar
  servo2.write(110);
  delayNonBlocking(500);
  servo1.write(170);
  servo3.write(90);
  delayNonBlocking(800);

  // Volver a posición base
  servo1.write(pos1);
  servo2.write(pos2);
  servo3.write(pos3);
  servo4.write(pos4);

  // Actualizar contador
  pilaCount--;
  // ---------------------------- En caso de querer guardar cantidad
  // guardarPilaCount();
  Serial.print("Unidad desapilada. Restantes: ");
  Serial.println(pilaCount);
}

void rutina3() {
  Serial.print("Apilando... unidades en la pila: ");
  Serial.println(pilaCount);

  if (pilaCount >= pilaMax) {
    Serial.println("La pila está llena (5 unidades).");
    return;
  }

  // Ir al punto A y recoger
  servo1.write(170);
  delayNonBlocking(500);
  servo3.write(180);
  delayNonBlocking(500);

  // Elevar y girar hacia B
  servo2.write(140);
  delayNonBlocking(500);
  servo4.write(170);
  delayNonBlocking(500);

  // Calcular altura según pila actual
  int alturaActual = alturaBase + (pilaCount * alturaIncremento);
  int baseActual = 170 - (pilaCount * alturaIncremento);
  servo2.write(alturaActual);
  delayNonBlocking(500);
  servo1.write(baseActual);
  delayNonBlocking(500);

  // Soltar la pieza
  servo3.write(90);
  delayNonBlocking(800);

  // Subir y volver al punto A
  servo2.write(160);
  delayNonBlocking(500);
  servo4.write(90);
  delayNonBlocking(500);

  // Volver a posición base
  servo2.write(pos2);
  servo1.write(pos1);

  // Incrementar contador
  pilaCount++;
  // ----------------------------- igual para guardar cantidad
  // guardarPilaCount();
  Serial.print("Unidad apilada. Total: ");
  Serial.println(pilaCount);
}

void rutina4() {
  // Cuadrado
  servo2.write(160);
  delayNonBlocking(500);
  servo4.write(60);
  delayNonBlocking(500);
  servo2.write(110);
  delayNonBlocking(500);
  servo1.write(170);
  delayNonBlocking(500);
  servo3.write(180);
  delayNonBlocking(500);

  servo1.write(140);
  delayNonBlocking(500);
  servo2.write(160);
  delayNonBlocking(500);
  servo4.write(120);
  delayNonBlocking(500);
  servo2.write(110);
  delayNonBlocking(500);
  servo1.write(170);
  delayNonBlocking(500);
  servo3.write(90);
  delayNonBlocking(500);

  servo1.write(140);
  delayNonBlocking(500);
  servo2.write(160);
  delayNonBlocking(500);
  servo4.write(90);
  delayNonBlocking(500);
  servo1.write(pos1);
  servo2.write(pos2);
}

// Selección de rutina
void seleccionarRutina() {
  Serial.println("Mueve el joystick 1 en una dirección...");
  int x = fastADC(0);
  int y = fastADC(1);

  // Esperar a que el usuario mueva el joystick
  while (abs(x - 512) < threshold && abs(y - 512) < threshold) {
    x = fastADC(0);
    y = fastADC(1);
  }

  if (x > 512 + threshold) {
    Serial.println("→ Derecha: rutina 1");
    rutina1();
  } else if (x < 512 - threshold) {
    Serial.println("← Izquierda: rutina 2");
    rutina2();
  } else if (y > 512 + threshold) {
    Serial.println("↑ Arriba: rutina 3");
    rutina3();
  } else if (y < 512 - threshold) {
    Serial.println("↓ Abajo: rutina 4");
    rutina4();
  }

  // Esperar a que vuelva al centro antes de continuar
  do {
    x = fastADC(0);
    y = fastADC(1);
  } while (abs(x - 512) > threshold || abs(y - 512) > threshold);

  Serial.println("Rutina finalizada.");
}

// Control manual
void controlManual() {
  int x1 = fastADC(0);
  int y1 = fastADC(1);
  int x2 = fastADC(2);
  int y2 = fastADC(3);

  // Servo 1 (Joystick 1 X)
  if (x1 < (512 - deadzone)) pos1 = clampInt(pos1 - step, 0, 160);
  if (x1 > (512 + deadzone)) pos1 = clampInt(pos1 + step, 0, 170);

  // Servo 2 (Joystick 1 Y)
  if (y1 < (512 - deadzone)) pos2 = clampInt(pos2 - step, 0, 170);
  if (y1 > (512 + deadzone)) pos2 = clampInt(pos2 + step, 0, 170);

  // Servo 3 (Joystick 2 X)
  if (x2 < (512 - deadzone)) pos3 = clampInt(pos3 - step, 0, 180);
  if (x2 > (512 + deadzone)) pos3 = clampInt(pos3 + step, 0, 180);

  // Servo 4 (Joystick 2 Y)
  if (y2 < (512 - deadzone)) pos4 = clampInt(pos4 - step, 0, 180);
  if (y2 > (512 + deadzone)) pos4 = clampInt(pos4 + step, 0, 180);

  // Escribir posiciones
  servo1.write(pos1);
  servo2.write(pos2);
  servo3.write(pos3);
  servo4.write(pos4);

  delayNonBlocking(15);
}

/*
     NUEVO enviar_rutina()
     Recibe:  a , b
     si recibe 0,0 pasa a posición segura
   */
void procesarComandoRutina() {
  if (!Serial.available()) return;

  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  if (cmd.length() < 3) return;

  int coma = cmd.indexOf(',');
  if (coma < 0) return;

  int servoID = cmd.substring(0, coma).toInt();
  int angulo  = cmd.substring(coma + 1).toInt();

  // Si recibe 0,0 
  if (servoID == 0 && angulo == 0) {
    servo1.write(140);
    servo2.write(110);
    servo3.write(90);
    servo4.write(90);

    pos1 = 140;
    pos2 = 110;
    pos3 = 90;
    pos4 = 90;

    return;
  }

  // Comando normal: servo,ángulo
  switch (servoID) {
    case 1:
      servo1.write(angulo);
      pos1 = angulo;
      break;
    case 2:
      servo2.write(angulo);
      pos2 = angulo;
      break;
    case 3:
      servo3.write(angulo);
      pos3 = angulo;
      break;
    case 4:
      servo4.write(angulo);
      pos4 = angulo;
      break;
  }
}


// Setup
void setup() {
  // Servos attach
  servo1.attach(11);
  servo2.attach(10);
  servo3.attach(9);
  servo4.attach(5);

  // Botón con pullup
  pinMode(joyButton, INPUT_PULLUP);

  // posiciones iniciales
  servo1.write(pos1);
  servo2.write(pos2);
  servo3.write(pos3);
  servo4.write(pos4);

  Serial.begin(9600);

  // Cargar pilaCount
  // cargarPilaCount();

  // Configurar ADC 
  ADMUX = (1 << REFS0); // AVcc 
  ADCSRA = (1 << ADEN) | (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0);

  // Configurar Timer2 para 1ms ticks (CTC, prescaler 64, OCR2A = 249)
  TCCR2A = (1 << WGM21);            
  TCCR2B = (1 << CS22);             
  TCCR2B = (1 << CS22) | (1 << CS21); // CS22=1 and CS21=1 -> prescaler 64 (CS22:CS21:CS20 = 1:1:0)
  OCR2A = 249;
  TIMSK2 |= (1 << OCIE2A);

  sei();
}


// Main loop
void loop() {
  
  procesarComandoRutina();   //  Comandos Python 

  // leer botón forma rápida
  bool boton = buttonPressed(); // true si presionado

  if (boton) {
    seleccionarRutina();
  } else {
    controlManual();
  }
}