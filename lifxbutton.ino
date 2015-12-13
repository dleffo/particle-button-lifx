
// This #include statement was automatically added by the Particle IDE.
// Version 0.2
// App to detect if a button is pressed on the Particle Internet Button and publish to MQTT.
#include "MQTT/MQTT.h"
#include "InternetButton/InternetButton.h"

InternetButton b = InternetButton();
char server[] = "mqtt.home.local";



void callback(char* topic, byte* payload, unsigned int length);

void callback(char* topic, byte* payload, unsigned int length) {

    int mred = 50;
    int mgreen = 50;
    int mblue = 50;
    String strred;
    String strblue;
    String strgreen;
    int led;
    char p[length + 1];
    memcpy(p, payload, length);
    p[length] = NULL;
    String message(p);
    String power;

//    String strtopic = topic;
    Serial.begin(9600);
    String a;
    String output;
    String command;
    String light;

    Serial.println(topic);
    Serial.println(message);
    String strtopic = topic;
    if(strtopic.startsWith("particle/InternetButton/buttons/")){
        Serial.println("Topic Found");
        strtopic = strtopic.substring(strtopic.lastIndexOf("/")+1);
        Serial.write("strtopic is: ");
        Serial.println(strtopic);
        int button = strtopic.toInt();
        Serial.println(button);
        if (button == 1){
            led = 12;
        }
        if (button == 2){
            led = 3;
        }
        if (button == 3){
            led = 6;
        }
        if (button == 4){
            led = 9;
        }
        Serial.write("Led: ");
        Serial.println(led);
        if(message.indexOf("Power:") != -1){
            power = message.substring(message.indexOf("Power:") + 6);
            power = power.substring(0,power.indexOf("/"));
            Serial.write("Power is: ");
            Serial.println(power);
            if(power == "True"){
                if(message.indexOf("Red:") != -1){
                    strred = message.substring(message.indexOf("Red:") + 4);
                    strred = strred.substring(0,strred.indexOf("/"));
                    mred = strred.toInt();
                }
                if(message.indexOf("Green:") != -1){
                    strgreen = message.substring(message.indexOf("Green:") + 6);
                    strgreen = strgreen.substring(0,strgreen.indexOf("/"));
                    mgreen = strgreen.toInt();
                }
                if(message.indexOf("Blue:") != -1){
                    strblue = message.substring(message.indexOf("Blue:") + 5);
                    strblue = strblue.substring(0,strblue.indexOf("/"));
                    mblue = strblue.toInt();
                }

                b.ledOn(led, mred, mgreen, mblue);
            }
            if(power == "False"){
                b.ledOff(led);
            }
        }
    }
    if(strtopic.equals("particle/InternetButton")){
        if(message.indexOf("Reset") != -1){
            Serial.println("Resetting");
            System.reset();
        }
    }
    if(strtopic.equals("particle/infrared/sensors/temp")){
        int button = 2;
        int min = 16;
        int max = 30;
        int brightness = 100;
        led = 3;
        float temp = message.toFloat();
        char* chartopic;
        Serial.write("Temp:");
        Serial.println(temp);
        temp = constrain(min, temp, max);
        mred = (temp-min)*brightness/(max-min);
        mblue = (max-temp)*brightness/(max-min);
        if (temp < (max+min)/2){
            mgreen = brightness/2 - ((brightness/2) * ((max + min)/2 - temp) / ((max - min)/2));
        }
        else{
            mgreen = brightness/2 - ((brightness/2 * (temp - (max + min)/2))/ ((max - min)/2));
        }
        Serial.write("Red:");
        Serial.println(mred);
        Serial.write("Blue:");
        Serial.println(mblue);
        Serial.write("Green:");
        Serial.println(mgreen);
        b.ledOn(led, mred, mgreen, mblue);
    }

}







MQTT client(server, 1883, callback);
int lastButtonState[5] = {LOW,LOW,LOW,LOW,LOW};
int connected = FALSE;
int lastconnected = FALSE;
String deviceID = "InternetButton";
char name[] = "button.home.local";

std::string topic = "";
char* chrtopic;

void setup() {
    b.begin();
        b.ledOn(3, 10, 0, 0);
        b.ledOn(6, 10, 0, 0);
        b.ledOn(9, 10, 0, 0);
        b.ledOn(12, 10, 0, 0);
    // Connect mqtt to broker
    while(client.isConnected() == FALSE){
        client.connect(name);
        delay(1000);
    }
    topic = "particle/" + deviceID + "/#";
    chrtopic = strdup(topic.c_str());
    client.subscribe(chrtopic);
    topic = "particle/infrared/sensors/temp";
    chrtopic = strdup(topic.c_str());
    client.subscribe(chrtopic);

}

void loop(){
    if (client.isConnected()){
        client.loop();
        connected = TRUE;
        if (connected != lastconnected){
            Spark.publish("reconnected", NULL, 60, PRIVATE);    //publish the event for IFTTT to consume
            topic = "particle/" + deviceID;
            chrtopic = strdup(topic.c_str());
            client.publish(chrtopic, "I'm back in business baby!");
            topic = topic + "/#";
            chrtopic = strdup(topic.c_str());
            client.subscribe(chrtopic);
            topic = "particle/infrared/sensors/temp";
            chrtopic = strdup(topic.c_str());
            client.subscribe(chrtopic);
            lastconnected = connected;
        }

        // Process individual buttons and LED response
        if (b.buttonOn(1) != lastButtonState[1]) {                              //Button state has changed.  For edge detection.
            if (b.buttonOn(1)){                                                 //The button is clicked.
                b.ledOn(12, 0, 0, 255);                                         //Turn button bright blue when pressed
                topic = "particle/" + deviceID + "/buttons";                    //build topic
                char* chrtopic = strdup(topic.c_str());                         //need to convert string to char
                client.publish(chrtopic, "Button 1 Pressed");                   //publish click to MQTT.
                free(chrtopic);                                                 //free memory. Not sure if this is needed.
                Spark.publish("Pressed", "Button 1 Pressed", 60, PRIVATE);      //publish button press to particle cloud for IFTTT to consume.
                lastButtonState[1] = b.buttonOn(1);                             //for edge detection
                delay(20);                                                      //debounce
            }
            else{                                                               //The button is not clicked.
//                b.ledOn(12, red, green, blue);                                  //colour for the button not pressed
                lastButtonState[1] = b.buttonOn(1);                             //for edge detection
            }
        }
        else{
            if (lastButtonState[1]){                                            //button is still clicked.  Don't take action, but keep the button red.
                b.ledOn(12, 0, 0,255);                                          //Red
            }
            else{
//                b.ledOn(12, red, green, blue);                                  //button is still not clicked.  Make/keep button default colour.
            }
        }

        if (b.buttonOn(2) != lastButtonState[2]) {
            if (b.buttonOn(2)){
                b.ledOn(3, 0, 0, 255);
                topic = "particle/" + deviceID + "/buttons";
                char* chrtopic = strdup(topic.c_str());
                client.publish(chrtopic, "Button 2 Pressed");
                free(chrtopic);
                Spark.publish("Pressed", "Button 2 Pressed", 60, PRIVATE);
                lastButtonState[2] = b.buttonOn(2);
                delay(20);
            }
            else{
//                b.ledOn(3, red, green, blue);
                lastButtonState[2] = b.buttonOn(2);
            }
        }
        else{
            if (lastButtonState[2]){
                b.ledOn(3, 0, 0,255);
            }
            else{
//                b.ledOn(3, red, green, blue);
            }
        }

        if (b.buttonOn(3) != lastButtonState[3]) {
            if (b.buttonOn(3)){
                b.ledOn(6, 0, 0, 255); // Red
                topic = "particle/" + deviceID + "/buttons";
                char* chrtopic = strdup(topic.c_str());
                client.publish(chrtopic, "Button 3 Pressed");
                free(chrtopic);
                Spark.publish("Pressed", "Button 3 Pressed", 60, PRIVATE);
                lastButtonState[3] = b.buttonOn(3);
                delay(20);
            }
            else{
//                b.ledOn(6, red, green, blue);
                lastButtonState[3] = b.buttonOn(3);
            }
        }
        else{
            if (lastButtonState[3]){
                b.ledOn(6, 0, 0, 255);
            }
            else{
//                b.ledOn(6, red, green, blue);
            }
        }

        if (b.buttonOn(4) != lastButtonState[4]) {
            if (b.buttonOn(4)){
                b.ledOn(9, 0, 0, 255);
                topic = "particle/" + deviceID + "/buttons";
                char* chrtopic = strdup(topic.c_str());
                client.publish(chrtopic, "Button 4 Pressed");
                free(chrtopic);
                Spark.publish("Pressed", "Button 4 Pressed", 60, PRIVATE);
                lastButtonState[4] = b.buttonOn(4);
                delay(20);
            }
            else{
//                b.ledOn(9, red, green, blue);
                lastButtonState[4] = b.buttonOn(4);
            }
        }
        else{
            if (lastButtonState[4]){
                b.ledOn(9, 0, 0,255);
            }
            else{
//                b.ledOn(9, red, green, blue);
            }
        }
    }
    else{
        client.connect(server);
        b.ledOn(3, 10, 0, 0);
        b.ledOn(6, 10, 0, 0);
        b.ledOn(9, 10, 0, 0);
        b.ledOn(12, 10, 0, 0);
        connected = FALSE;
        if (connected != lastconnected){
            Spark.publish("disconnected", NULL, 60, PRIVATE);
            lastconnected = connected;

        }


    }
}





// This #include statement was automatically added by the Particle IDE.
// Version 0.2
// App to detect if a button is pressed on the Particle Internet Button and publish to MQTT.
#include "MQTT/MQTT.h"
#include "InternetButton/InternetButton.h"


void callback(char* topic, byte* payload, unsigned int length);

void callback(char* topic, byte* payload, unsigned int length) {

}




/**
 * if want to use IP address,
 * byte server[] = { XXX,XXX,XXX,XXX };
 * MQTT client(server, 1883, callback);
 * want to use domain name,
 * MQTT client("www.sample.com", 1883, callback);
 **/
MQTT client("mqtt.home.local", 1883, callback);

// recieve message

InternetButton b = InternetButton();
int red = 5;
int green = 5;
int blue = 0;
int lastButtonState[5] = {LOW,LOW,LOW,LOW,LOW};
int connected = FALSE;
int lastconnected = FALSE;
String deviceID = System.deviceID();

std::string topic = "";
char* chrtopic;

void setup() {
    b.begin();
    // Connect mqtt to broker
    client.connect("mqtt.home.local");
}

void loop(){
    if (client.isConnected()){
        client.loop();
        connected = TRUE;
        if (connected != lastconnected){
            Spark.publish("reconnected", NULL, 60, PRIVATE);    //publish the event for IFTTT to consume
            lastconnected = connected;
        }

        // Process individual buttons and LED response
        if (b.buttonOn(1) != lastButtonState[1]) {                              //Button state has changed.  For edge detection.
            if (b.buttonOn(1)){                                                 //The button is clicked.
                b.ledOn(12, 255, 0, 0);                                         //Turn button bright red when pressed
                topic = "particle/" + deviceID + "/buttons";                    //build topic
                char* chrtopic = strdup(topic.c_str());                         //need to convert string to char
                client.publish(chrtopic, "Button 1 Pressed");                   //publish click to MQTT.
                free(chrtopic);                                                 //free memory. Not sure if this is needed.
                Spark.publish("Pressed", "Button 1 Pressed", 60, PRIVATE);      //publish button press to particle cloud for IFTTT to consume.
                lastButtonState[1] = b.buttonOn(1);                             //for edge detection
                delay(20);                                                      //debounce
            }
            else{                                                               //The button is not clicked.
                b.ledOn(12, red, green, blue);                                  //colour for the button not pressed
                lastButtonState[1] = b.buttonOn(1);                             //for edge detection
            }
        }
        else{
            if (lastButtonState[1]){                                            //button is still clicked.  Don't take action, but keep the button red.
                b.ledOn(12, 255, 0,0);                                          //Red
            }
            else{
                b.ledOn(12, red, green, blue);                                  //button is still not clicked.  Make/keep button default colour.
            }
        }

        if (b.buttonOn(2) != lastButtonState[2]) {
            if (b.buttonOn(2)){
                b.ledOn(3, 255, 0, 0); // Red
                topic = "particle/" + deviceID + "/buttons";
                char* chrtopic = strdup(topic.c_str());
                client.publish(chrtopic, "Button 2 Pressed");
                free(chrtopic);
                Spark.publish("Pressed", "Button 2 Pressed", 60, PRIVATE);
                lastButtonState[2] = b.buttonOn(2);
                delay(20);
            }
            else{
                b.ledOn(3, red, green, blue);
                lastButtonState[2] = b.buttonOn(2);
            }
        }
        else{
            if (lastButtonState[2]){
                b.ledOn(3, 255, 0,0);
            }
            else{
                b.ledOn(3, red, green, blue);
            }
        }

        if (b.buttonOn(3) != lastButtonState[3]) {
            if (b.buttonOn(3)){
                b.ledOn(6, 255, 0, 0); // Red
                topic = "particle/" + deviceID + "/buttons";
                char* chrtopic = strdup(topic.c_str());
                client.publish(chrtopic, "Button 3 Pressed");
                free(chrtopic);
                Spark.publish("Pressed", "Button 3 Pressed", 60, PRIVATE);
                lastButtonState[3] = b.buttonOn(3);
                delay(20);
            }
            else{
                b.ledOn(6, red, green, blue);
                lastButtonState[3] = b.buttonOn(3);
            }
        }
        else{
            if (lastButtonState[3]){
                b.ledOn(6, 255, 0,0);
            }
            else{
                b.ledOn(6, red, green, blue);
            }
        }

        if (b.buttonOn(4) != lastButtonState[4]) {
            if (b.buttonOn(4)){
                b.ledOn(9, 255, 0, 0); // Red
                topic = "particle/" + deviceID + "/buttons";
                char* chrtopic = strdup(topic.c_str());
                client.publish(chrtopic, "Button 4 Pressed");
                free(chrtopic);
                Spark.publish("Pressed", "Button 4 Pressed", 60, PRIVATE);
                lastButtonState[4] = b.buttonOn(4);
                delay(20);
            }
            else{
                b.ledOn(9, red, green, blue);
                lastButtonState[4] = b.buttonOn(4);
            }
        }
        else{
            if (lastButtonState[4]){
                b.ledOn(9, 255, 0,0);
            }
            else{
                b.ledOn(9, red, green, blue);
            }
        }
    }
    else{
        client.connect("mqtt.home.local");
        b.ledOn(3, 128, 0, 0);
        b.ledOn(6, 128, 0, 0);
        b.ledOn(9, 128, 0, 0);
        b.ledOn(12, 128, 0, 0);
        connected = FALSE;
        if (connected != lastconnected){
            Spark.publish("disconnected", NULL, 60, PRIVATE);
            lastconnected = connected;
        }


    }
}
