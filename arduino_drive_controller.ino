#include <AFMotor.h>

char in_command_array[7]; 
int napr = 0;
int ugol = 0;
int error = 0;
int speed_ = 0;

AF_DCMotor motor1(1);
AF_DCMotor motor2(2);
AF_DCMotor motor3(3);

void setup() {
  Serial.begin(115200);           

  motor1.setSpeed(200);
  motor1.run(RELEASE);
  motor2.setSpeed(200);
  motor2.run(RELEASE);
  motor3.setSpeed(0);
  motor3.run(FORWARD);
  delay(5000);
}

void loop() {
  String inString = "";
  String ServoNapr = "";
  String ServoUgol = "";
  String MotorNapr = "";
  String MotorSpeed = "";
  char in_command_array[7];
  
  while (Serial.available()) { 
    in_command_array[0] = Serial.read();
    if (ServoNapr == 'L' || ServoNapr == 'R') { 
      inString = "";
      for (int i=0;i<3;i++) {
        delay(1);
        char inChar = Serial.read(); 
        if (isDigit(inChar)) in_command_array[i+1] = (char)inChar; 
      }  
      int ServoUgol = inString.toInt();

    in_command_array[3] = Serial.read(); 
    inString = "";
    for (int i=0;i<3;i++) {
      delay(1);
      char inChar = Serial.read(); 
      if (isDigit(inChar)) in_command_array[i+4] = (char)inChar; 
    }  
    int MotorSpeed = inString.toInt();

    Serial.println(in_command_array);
    }
  }  

    if(in_command_array[0] == 76) { napr = -1; }
    else if(in_command_array[0] == 82) { napr = 1; }
    else if(in_command_array[0] == 48) { napr = 0; }
    else { error++; }

    Serial.println();
    Serial.print("napr = ");
    Serial.println(napr); 
    Serial.print("error = ");
    Serial.println(error); 

    int ugol_num1 = in_command_array[1] - 48;
    int ugol_num2 = in_command_array[2] - 48;

    Serial.print("ugol_num1 = ");
    Serial.println(ugol_num1); 
    Serial.print("ugol_num2 = ");
    Serial.println(ugol_num2); 

    if(ugol_num1 == 0) { ugol = ugol_num2; }
    else if(ugol_num1 != 0) { ugol = ugol_num1*10 + ugol_num2; }
    else { error++; }

    Serial.print("ugol = ");
    Serial.println(ugol);
    Serial.print("error = ");
    Serial.println(error);

    int speed_num1 = in_command_array[4] - 48;
    int speed_num2 = in_command_array[5] - 48;
    int speed_num3 = in_command_array[6] - 48;

    Serial.print("speed_num1 = ");
    Serial.println(speed_num1); 
    Serial.print("speed_num2 = ");
    Serial.println(speed_num2); 
    Serial.print("speed_num3 = ");
    Serial.println(speed_num3);

    if(speed_num1 == 0 && speed_num2 == 0) { speed_ = speed_num3; }
    else if(speed_num1 == 0) { speed_ = ugol_num2*10 + speed_num3; }
    else if(speed_num1 != 0) { speed_ = speed_num1*100 + speed_num2*10 + speed_num3; }
    else { error++; }

    Serial.print("speed = ");
    Serial.println(speed_);
    Serial.print("error = ");
    Serial.println(error);

    if(speed_ >= 255) {
      speed_ = speed_ - 255;
      motor1.run(FORWARD);
      motor1.setSpeed(speed_);
      motor2.run(FORWARD);
      motor2.setSpeed(speed_);
    }
    else {
      motor1.run(BACKWARD);
      motor1.setSpeed(speed_);
      motor2.run(BACKWARD);
      motor2.setSpeed(speed_);
    }

    if(speed_ == 255) {
      motor1.run(RELEASE);
      motor2.run(RELEASE);
    }

    if(napr == 1) { motor3.run(FORWARD); }
    else if(napr == -1) { motor3.run(BACKWARD); }

    motor3.setSpeed(ugol*2.83);
}

