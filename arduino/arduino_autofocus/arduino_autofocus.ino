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
  /*
  Clipper class
    clip value by min and max
  Args:
    min: int, expected positive value
    max: int, expected positive value
  Methods:
    clip: int, clip value by min and max
  Attributes:
    min: int, expected positive value
    max: int, expected positive value
  */
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
  /*
  MYStepper class
    MYStepper class is a wrapper class of Stepper class in Arduino library.

  Args:
    steps_per_rotate: int, expected positive value
    pin1: int. It corresponds to MOTOR_PIN1 of Stepper in Arduino library
    pin2: int, It corresponds to MOTOR_PIN2 of Stepper in Arduino library
    pin3: int, It corresponds to MOTOR_PIN3 of Stepper in Arduino library
    pin4: int, It corresponds to MOTOR_PIN4 of Stepper in Arduino library

  Methods:
    _setSpeed: void, set speed of motor
    _step: int, rotate motor at steps. if stoppableflag is true, stoppable by serial input "s"
    getSpeed: int, get speed of motor
    
  Attributes:
    steps_per_rotate: int, expected positive value
    rpm: int, expected positive value
    steps_per_sec: int, expected positive value
    super_stepper: Stepper, Stepper class in Arduino library
  */
  public:
    MYStepper(int steps_per_rotate, int pin1, int pin2, int pin3, int pin4)
      : super_stepper(steps_per_rotate, pin1, pin2, pin3, pin4) {//construct Stepper class in Arduino library as a name of super_stepper
      this->steps_per_rotate = steps_per_rotate;
    }
    int _setSpeed(int rpm){
      /*
      set speed of motor
      Args:
        rpm: int, expected positive value
      */
      this->rpm = rpm;
      this->super_stepper.setSpeed(this->rpm);
      this->steps_per_sec = this->steps_per_rotate * this->rpm / 60;
      return this -> rpm;
    }
    int _step(int steps, bool stoppableflag){
      /*
      rotate motor at steps. if stoppableflag is true, stoppable by serial input "s"
      This function is monitoring serial input every 1-second, before and after rotate motor by steps_per_sec steps.
      This function is blocking function
      Args:
        steps: int, expected rotate steps, positive or negative value
        stoppableflag: bool. if true, stoppable by serial input "s".  else, not stoppable
      Return:
        int, truly rotated steps
      */
      if(steps >= 0){//if steps is positive, rotate motor at positive direction
        for(int rotatedsteps = 0; rotatedsteps < steps; rotatedsteps += this->steps_per_sec){
          if(stoppableflag && Serial.available()){
            String str_input = Serial.readString();
            str_input.trim();
            clear_buffer();
            if(str_input == "s") return rotatedsteps;//if input "s", return rotated steps
          }
          this->super_stepper.step(min(this->steps_per_sec, steps - rotatedsteps));
        }
        return steps;
      }
      else{//if steps is negative, rotate motor at negative direction
        for(int rotatedsteps = 0; rotatedsteps > steps; rotatedsteps -= this->steps_per_sec){
          if(stoppableflag && Serial.available()){
            String str_input = Serial.readString();
            str_input.trim();
            clear_buffer();
            if(str_input == "s") return rotatedsteps;//if input "s", force stop and return rotated steps
          }
          this->super_stepper.step(max(-1 * this->steps_per_sec, steps - rotatedsteps));
        }
        return steps;
      }
    }
    int getSpeed(){
      return this->rpm;
    }

  private:
    int steps_per_rotate; //steps per 1-rotation. It depends on motor. positive value
    int rpm;//rotate per minute. speed. positive value
    int steps_per_sec;// steps per 1-second. It calculated by steps_per_rotate * rpm / 60. positive value
    Stepper super_stepper;// Stepper class in Arduino library
};


Clipper speed_clipper(0, 80);  // speed clipper
Clipper step_clipper(0, 1000);  // step clipper
MYStepper myStepper(STEPS_PER_ROTATE_ST42BYH1004, MOTOR_PIN1, MOTOR_PIN2, MOTOR_PIN3, MOTOR_PIN4);

void setup() { 
  Serial.begin(9600);      // シリアル通信の初期化 
  myStepper._setSpeed(INITIAL_RPM);  // rpmを設定 
} 

void loop() {
  /*
  command table
    r value: rotate motor at value step. blocking function. 
              after rotataion, send "t value". value is truly rotated steps
      ex) r 100
    l value: rotate motor at -1 * value step. blocking function. 
              after rotataion, send "t value". value is truly rotated steps
      ex) l 100
    p value: set speed of motor at value rpm
              after setting speed, send "t 0"
      ex) p 10
    s:       if input "s", stop motor and return truly rotated steps, while moving motor
      ex) s
    
    if command is not in command table, send "e 0" as error message
  */
  if (Serial.available()){
    String command, value;
    int rotate_step, true_rotate_step, rpm;
    String str_input_step = Serial.readString();
    str_input_step.trim();
    split(str_input_step, ' ', command, value);

    if(command == "u"){
      // rotate motor at value step
      // value: int(rotate step) expected positive value
      // after rotataion, send "t"
      rotate_step = step_clipper.clip(value.toInt());
      true_rotate_step = myStepper._step(rotate_step, true);
      Serial.println("t "+String(true_rotate_step));
    }

    else if(command == "d"){
      // rotate motor at -1 * value step
      // value: int(rotate step) expected positive value
      // after rotataion, send "t"
      rotate_step = -1 * step_clipper.clip(value.toInt());
      true_rotate_step = myStepper._step(rotate_step, true);
      Serial.println("t "+String(true_rotate_step));
    }

    else if(command == "p"){
      rpm = myStepper._setSpeed(speed_clipper.clip(value.toInt()));
      Serial.println("t " + String(rpm));
    }

    else{
      // send error message
      Serial.println("e 0");
    }
    delay(10);
    clear_buffer();    // バッファのクリア
  }
}
