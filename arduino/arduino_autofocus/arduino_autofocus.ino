#include <Stepper.h> 
#include <String.h>

#define MOTOR_PIN1 8  // 使用するモータのpin 
#define MOTOR_PIN2 9 
#define MOTOR_PIN3 10
#define MOTOR_PIN4 11

#define STEPS_PER_ROTATE_ST42BYH1004 400 // 1回転に必要なステップ数　360deg/rotate / 0.9deg/step = 400step/rotate

#define INITIAL_RPM 10 // 初期rpm


class Clipper {
  public:
    Clipper(int min, int max){
      this->min = min;
      this->max = max;
    }
    int clip(int value){
      if(value < min) return min;
      else if(value > max) return max;
      return value;
    }
  private:
    int min;
    int max;
};


void split(const String &input, char delim, String &command, String &value) {
  /*
  split Input by Delim and output Command and Value
  */
  for(int i = 0; i < input.length(); i++) {
    if (input[i] == delim) {
      command = input.substring(0, i);
      value = input.substring(i+1, input.length());
      break;
    }
  }
}

void clear_buffer(){
  /*
  clear buffer
  */
  while (Serial.available())
    Serial.read();
}

Clipper speed_clipper(0, 100);  // speed clipper
Clipper step_clipper(0, 1000);  // step clipper
Stepper myStepper(STEPS_PER_ROTATE_ST42BYH1004, MOTOR_PIN1, MOTOR_PIN2, MOTOR_PIN3, MOTOR_PIN4); //ステッピングライブラリの設定

void setup() { 
  Serial.begin(9600);      // シリアル通信の初期化 
  
  myStepper.setSpeed(INITIAL_RPM);  // rpmを設定 
} 

void loop() {
  if (Serial.available()){
    String str_input_step = Serial.readString();
    String command, value;
    str_input_step.trim();
    split(str_input_step, ' ', command, value);

    if(command == "r"){
      // rotate motor at value step
      // value: int(rotate step) expected positive value
      // after rotataion, send "t"
      myStepper.step(step_clipper.clip(value.toInt()));
      Serial.println("t");
    }

    else if(command == "l"){
      // rotate motor at -1 * value step
      // value: int(rotate step) expected positive value
      // after rotataion, send "t"
      myStepper.step(-1 * step_clipper.clip(value.toInt()));
      Serial.println("t");
    }

    else if(command == "s"){
      
      myStepper.setSpeed(speed_clipper.clip(value.toInt()));

      Serial.println("t");
    }

    else{
      Serial.println("e");
    }
    delay(10);
    clear_buffer();    // バッファのクリア
  }
}
