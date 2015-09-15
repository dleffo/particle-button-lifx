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
