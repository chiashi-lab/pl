#include <Stepper.h> 
#include <String.h>
#include <HardwareSerial.h>

#define MOTOR_PIN1 8  // 使用するモータのpin 
#define MOTOR_PIN2 9 
#define MOTOR_PIN3 10
#define MOTOR_PIN4 11
#define STEPS_PER_ROTATE_ST42BYH1004 400 // 1回転に必要なステップ数　360deg/rotate / 0.9deg/step = 400step/rotate
#define INITIAL_RPM 10 // 初期rpm

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


class MYStepper{
  public:
    MYStepper(int step, int pin1, int pin2, int pin3, int pin4)
      : super_stepper(step, pin1, pin2, pin3, pin4) {
    }
    void _setSpeed(int rpm){
      this->step_per_sec = STEPS_PER_ROTATE_ST42BYH1004 * rpm / 60;
      this->super_stepper.setSpeed(rpm);
    }
    int _step(int steps, bool stoppableflag){
      for(int rotatedstep = 0; rotatedstep < steps; rotatedstep+=this->step_per_sec){
        if(stoppableflag && Serial.available()){
          String str_input = Serial.readString();
          str_input.trim();
          clear_buffer();
          if(str_input == "s") return rotatedstep;
        }
        this->super_stepper.step(min(this->step_per_sec, steps-rotatedstep));
      }
      return steps;
    }
    int getSpeed(){
      return this->rpm;
    }

  private:
    int rpm;
    int step_per_sec;
    Stepper super_stepper;
};


Clipper speed_clipper(0, 100);  // speed clipper
Clipper step_clipper(0, 1000);  // step clipper
MYStepper myStepper(STEPS_PER_ROTATE_ST42BYH1004, MOTOR_PIN1, MOTOR_PIN2, MOTOR_PIN3, MOTOR_PIN4);

void setup() { 
  Serial.begin(9600);      // シリアル通信の初期化 
  myStepper._setSpeed(INITIAL_RPM);  // rpmを設定 
} 

void loop() {
  if (Serial.available()){
    String command, value;
    int rotate_step, true_rotate_step;
    String str_input_step = Serial.readString();
    str_input_step.trim();
    split(str_input_step, ' ', command, value);

    if(command == "r"){
      // rotate motor at value step
      // value: int(rotate step) expected positive value
      // after rotataion, send "t"
      rotate_step = step_clipper.clip(value.toInt());
      true_rotate_step = myStepper._step(rotate_step, true);
      Serial.println("t "+String(true_rotate_step));
    }

    else if(command == "l"){
      // rotate motor at -1 * value step
      // value: int(rotate step) expected positive value
      // after rotataion, send "t"
      rotate_step = -1 * step_clipper.clip(value.toInt());
      true_rotate_step = myStepper._step(rotate_step, true);
      Serial.println("t "+String(true_rotate_step));
    }

    else if(command == "p"){
      myStepper._setSpeed(speed_clipper.clip(value.toInt()));
      Serial.println("t 0");
    }

    else{
      Serial.println("e 0");
    }
    delay(10);
    clear_buffer();    // バッファのクリア
  }
}
