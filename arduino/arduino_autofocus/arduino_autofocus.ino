#include <Stepper.h> 
#include <String.h>

#define MOTOR_PIN1 5  // 使用するモータのpin 
#define MOTOR_PIN2 6 
#define MOTOR_PIN3 7 
#define MOTOR_PIN4 8 
#define STEPS_PER_ROTATE_28BYJ48 2048 // 1回転に必要なステップ数. 360[deg] / 5.625[deg/step] / 2(相励磁) * 64(gear比) 

const int StepsPerRotate = STEPS_PER_ROTATE_28BYJ48; 

// 毎分の回転数(rpm) 
int rpm = 15; // 1-15rpmでないと動かない 
// モータに与えるステップ数 
// 90度回転. 360deg : 90deg = 2048 : 512 

Stepper myStepper(StepsPerRotate, MOTOR_PIN1, MOTOR_PIN3, MOTOR_PIN2, MOTOR_PIN4); //ステッピングライブラリの設定

void setup() { 
  Serial.begin(9600);      // シリアル通信の初期化 
  myStepper.setSpeed(rpm);  // rpmを設定 
} 

void loop() {

  // 受信データがあった時だけ、処理を行う
  if (Serial.available())
  {
    String str_input_step = Serial.readString();
    str_input_step.trim();
    int input_step = str_input_step.toInt();
    myStepper.step(input_step); // 15degステッピングモータを駆動
    delay(500);
    while (Serial.available())
      Serial.read();     // バッファのクリア
    Serial.println('e'); // ステッピングモータ動作終了コマンドをpcに送信
    Serial.println(String(input_step)); // ステッピングモータ動作終了コマンドをpcに送信
  }
}
