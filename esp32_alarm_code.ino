#include <WiFi.h>

// WiFi credentials for Station mode
const char* ssid_sta = "tect";
const char* password_sta = "underscore";

// Access Point credentials
const char* ssid_ap = "FLIESPOT_ESP32_AP";
const char* password_ap = "fliespotalarm";

// IP configuration for ESP32 AP
IPAddress local_IP(192, 168, 5, 1); // New AP IP address
IPAddress gateway(192, 168, 5, 1); // Gateway for the AP
IPAddress subnet(255, 255, 255, 0); // Subnet mask

// Password for triggering the alarm
bool passwordProtected = true;
const char* triggerPassword = "simplepassword";

WiFiServer server(80);  // Create a WiFi server listening on port 80
int ledPin = 2;         // The pin connected to the LED or buzzer
bool isBusy = false;    // Flag to indicate if the ESP32 is currently busy (busy beeping the alarm)

void setup() {
  pinMode(ledPin, OUTPUT);       // Set the LED pin as an output
  digitalWrite(ledPin, LOW);     // Ensure the LED is off initially

  Serial.begin(115200);          // Start the Serial Monitor for debugging

  // Start WiFi in Station mode
  WiFi.begin(ssid_sta, password_sta);
  Serial.println("Connecting to WiFi...");

  unsigned long startAttemptTime = millis();

  // Wait for STA connection for up to 10 seconds
  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 10000) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected to WiFi!");
    Serial.print("Station IP: ");
    Serial.println(WiFi.localIP());
  } else {
    stopWiFiReconnection = true;
    Serial.println("\nFailed to connect to WiFi.");
  }

  // Set the ESP32 as an Access Point with a custom IP
  WiFi.softAP(ssid_ap, password_ap);
  if (!WiFi.softAPConfig(local_IP, gateway, subnet)) {
    Serial.println("Failed to configure AP IP!");
  } else {
    Serial.print("AP IP address: ");
    Serial.println(WiFi.softAPIP());
  }

  // Start the server
  server.begin();
  Serial.println("Server started.");
}

void loop() {
  WiFiClient client = server.available();  // Check if a client has connected

  if (client) {                            // If a client is connected:
    String request = client.readStringUntil('\r'); // Read the client's request
    Serial.println(request);               // Print the request for debugging
    client.flush();                        // Clear the client's input buffer

    if (request.indexOf("/on") != -1 || request.indexOf("/info") != -1) { // If the request is for "/on" or "/info":

      if (isBusy && request.indexOf("/on") != -1) { // if busy, all client pending requests will not trigger the alarm and just be told that the server is busy
        client.println("HTTP/1.1 200 OK");
        client.println("Content-Type: text/plain");
        client.println("Connection: close");
        client.println();
        client.println("Triggered but server is busy. Someone already triggered the alarm. Try again later.");
        client.stop();
      } else { // if not busy, the one request that did this will trigger the alarm
        // System is not busy, proceed to check password
        if (request.indexOf("password=") != -1 || !passwordProtected) {
          int start = request.indexOf("password=") + 9; // Position after "password="
          int end = request.indexOf(' ', start);        // End of the password parameter
          String providedPassword = request.substring(start, end);

          if (triggerPassword == providedPassword || !passwordProtected) {
            if (request.indexOf("/on") != -1) {
              client.println("HTTP/1.1 200 OK");   // Respond with HTTP OK
              client.println("Content-Type: text/plain");
              client.println("Connection: close");
              client.println();
              client.println("You've triggered the alarm. Alarm pattern started.");
              client.stop();                       // Close the connection
              isBusy = true;
              // Perform the beeping pattern
              for (int i = 0; i < 3; i++) {        // Repeat 3 sequences
                for (int j = 0; j < 3; j++) {      // Beep 3 times per sequence
                  digitalWrite(ledPin, HIGH);      // Turn on the LED
                  delay(200);                      // Wait 200ms
                  digitalWrite(ledPin, LOW);       // Turn off the LED
                  delay(200);                      // Wait 200ms
                }
                delay(1000);                       // Wait 1 second between sequences
              }
            } else if (request.indexOf("/info") != -1) {
              client.println("HTTP/1.1 200 OK");   // Respond with HTTP OK
              client.println("Content-Type: text/plain");
              client.println("Connection: close");
              client.println();
              client.println("INFO:");
              client.println("");
              client.print("Station IP: ");
              if (WiFi.status() == WL_CONNECTED) {
                client.println(WiFi.localIP());
              } else {
                client.println("Not connected");
              }
              client.print("AP IP address: ");
              client.println(WiFi.softAPIP());
              client.stop();
            }
          } else {
              // Incorrect password
              client.println("HTTP/1.1 403 Forbidden");
              client.println("Content-Type: text/plain");
              client.println("Connection: close");
              client.println();
              client.println("Invalid password.");
              client.stop();
          }

        } else {
          // Password missing
          client.println("HTTP/1.1 400 Bad Request");
          client.println("Content-Type: text/plain");
          client.println("Connection: close");
          client.println();
          client.println("Password missing in the request.");
          client.stop();
        }

      }
    } else {
      // Respond with "404 Not Found" for unrecognized requests
      client.println("HTTP/1.1 404 Not Found");
      client.println("Content-Type: text/plain");
      client.println("Connection: close");
      client.println();
      client.println("Invalid request.");
      client.stop();                       // Close the connection
    }
  } else {
    isBusy = false; // if there is no client connections return flag into available again (not busy)
  }
}
