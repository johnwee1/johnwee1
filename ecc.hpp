#include <stdint.h>
#include <Arduino.h>

class ECCSerial
{
        uint16_t calculate(char* message);
        void begin(int rate);
        void write(char* message);
        char* read();

};