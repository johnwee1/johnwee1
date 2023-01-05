#include "ecc.hpp"

//Still need to request retransmission if the code turns out to have an error
char* retrans = "^^^"; // '^' is the code that requests for retransmission, sending it thrice (?)
void ECCSerial::begin(int num){
    Serial.begin(num);
}
void ECCSerial::write(char* message){
    uint16_t crc = ECCSerial::calculate(message); //Calculate the CRC
    char eccmessage[strlen(message) + 6]; //+1 for null char, +1 for colon ":", +4 for hexadecimal CRC
    sprintf(eccmessage, "%s:%04X\0");
    Serial.write(eccmessage);
    //start listening for retransmission
    if (Serial.available()){
        char buf[4];
        memset(buf,0,4);
        Serial.readBytes(buf,3);
        int counter = 0;
        for(int i=0;i<2;i++){
            if (buf[i] == '^') counter++;
        }
        if (counter>=2) write(message); //recursive
        return;
    }
}
char* ECCSerial::read(){
    /**Returns a char* array if message is found, and NULL if serial buffer is empty.**/
    if (Serial.available()>0){
        char incomingmsg[65];                       //Max buffer size of arduino's serial is 64
        memset(incomingmsg,0,64);                   //empty array
        Serial.readBytesUntil('\0',incomingmsg,64);
        incomingmsg[64] = '\0';                     //Set null terminator, although I don't think there's really a need to.
        char* crc_ptr = strrchr(incomingmsg, ':');
        if (crc_ptr==NULL){
            Serial.write(retrans, 3);
            return read();
        }
        *crc_ptr = '\0';                            //inserts a null termination, break the string in two.
        char* message = &incomingmsg[0];            //Stops at the null terminator in the midpoint
        crc_ptr++;
        uint16_t crc = ECCSerial::calculate(message);          //Compute CRC on receiving end
        uint16_t received_crc = strtoul(crc_ptr, NULL, 16); //convert from char array to uint16_t
        if (crc != received_crc){
            Serial.write(retrans,3);
            return read();
        } else return message;
    }
    else return NULL;
}

uint16_t ECCSerial::calculate(char* data) {
    uint16_t crc = 0xFFFF;
    int length = strlen(data);
    for (int i = 0; i < length; i++) {
      crc = (crc >> 8) | (crc << 8);
      crc ^= data[i];
      crc ^= (crc & 0xFF) >> 4;
      crc ^= crc << 12;
      crc ^= (crc & 0xFF) << 5;
    }
  return crc;
}