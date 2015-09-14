// This #include statement was automatically added by the Particle IDE.
// Version 0.2
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


/* Here's a nice combination of features that I like to use.
Note the use of the allButtons function. */

InternetButton b = InternetButton();
int red = 5;
int green = 5;
int blue = 0;
int lastButtonState[5] = {LOW,LOW,LOW,LOW,LOW};
int connected = FALSE;
int lastconnected = FALSE;
std::string deviceID = "2b001e001647343339383037";
std::string topic = "";
char* chrtopic;

void setup() {
    // Tell b to get everything ready to go
    // Use b.begin(1); if you have the original SparkButton, which does not have a buzzer or a plastic enclosure
    // to use, just add a '1' between the parentheses in the code above.
    b.begin();
    client.connect("mqtt.home.local");
}

void loop(){
    if (client.isConnected()){
        client.loop();
        connected = TRUE;
        if (connected != lastconnected){
            Spark.publish("reconnected", NULL, 60, PRIVATE);
            lastconnected = connected;
        }

        // Process individual buttons and LED response
        if (b.buttonOn(1) != lastButtonState[1]) {
            if (b.buttonOn(1)){
                b.ledOn(12, 255, 0, 0); // Red
                // Publish the event "button1" for other services like IFTTT to use
                topic = "particle/" + deviceID + "/lights/Bedroom/button";
                char* chrtopic = strdup(topic.c_str());     //need to convert string to char*
                client.publish(chrtopic, "button for Bedroom clicked");
                free(chrtopic);     //free memory for chrtopic
                Spark.publish("Pressed", "Bedroom lights toggled.", 60, PRIVATE);
                lastButtonState[1] = b.buttonOn(1);
                delay(20);
            }
            else{
                b.ledOn(12, red, green, blue);
                lastButtonState[1] = b.buttonOn(1);
            }
        }
        else{
            if (lastButtonState[1]){
                b.ledOn(12, 255, 0,0);
            }
            else{
                b.ledOn(12, red, green, blue);
            }
        }

        if (b.buttonOn(2) != lastButtonState[2]) {
            if (b.buttonOn(2)){
                b.ledOn(3, 255, 0, 0); // Red
                // Publish the event "button1" for other services like IFTTT to use
                topic = "particle/" + deviceID + "/lights/button";
                char* chrtopic = strdup(topic.c_str());
                client.publish(chrtopic, "Set default colour");
                Spark.publish("Pressed", "Lights set to default colours.", 60, PRIVATE);
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
                // Publish the event "button1" for other services like IFTTT to use
                client.publish("particle/2b001e001647343339383037/lights/Study/button", "button for Study clicked");
                Spark.publish("Pressed", "Study light toggled.", 60, PRIVATE);
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
                // Publish the event "button1" for other services like IFTTT to use
                client.publish("particle/2b001e001647343339383037/lights/Lounge/button", "button for Lounge clicked");
                Spark.publish("Pressed", "Lounge lights toggled", 60, PRIVATE);
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
