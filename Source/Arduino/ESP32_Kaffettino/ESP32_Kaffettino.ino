/**
SPI-LETTORE:
RST  - 34
MISO - 19
MOSI - 23
SCK  - 18
SDA  - 5
Installare MFRC522 by Community

I2C-SCHERMO:
SCL - 22
SDA - 21
Installare Adafruit SSD1306 by Adafruit (Con dipendenze)

*/

//Lib lettore
  #include <SPI.h>
  #include <MFRC522.h>


//Lib Oled
  #include <Wire.h>
  #include <Adafruit_GFX.h>
  #include <Adafruit_SSD1306.h>

//Lib audio
  #include <Arduino.h>
  #include "DFRobotDFPlayerMini.h"

//PERIFERICHE  
  #define green 27
  #define yellow 26 
  #define red 12
  #define GND 14
  #define GND2 35
  #define VCC 17
  
  #define buzzer 16


//Impostazione schermo
  #define SCREEN_WIDTH 128 // OLED display width, in pixels
  #define SCREEN_HEIGHT 64 // OLED display height, in pixels
  #define OLED_RESET     -1 // Reset pin # (or -1 if sharing Arduino reset pin)
  #define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
  #define VIV 6
  #define PAG 0
//Creazione "oggetto" display  
  Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
  void stampaoled(int i);


//Impostazione lettore
  constexpr uint8_t RST_PIN =  34;         //Pin di reset
  constexpr uint8_t SS_PIN =  5;         // Pin dati
  int controllo[12]={195,227,250,166};    // Codice UID di un tag
  int verify = 0;                         //variabile di controllo della differenza tra UID letto e salvato
  MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

//Impostazione audio
  HardwareSerial mySoftwareSerial(1);
  DFRobotDFPlayerMini myDFPlayer;

//Gestione temporale
  long long int t;
//  long long int t2;
  bool flag = true;
  #define attesa 3000

//Pulsante-Interrupt
  #define butt 25
  int state = 0; //0=caffe' 1=acqua


void setup() {

  mySoftwareSerial.begin(9600 , SERIAL_8N1, 32, 33);  // speed, type, RX, TX
  Serial.begin(115200);   // Initialize serial communications with the PC
  delay(1000);
  Serial.println("Setup");
  

  pinMode(butt, INPUT_PULLUP);
  pinMode(GND, OUTPUT);   digitalWrite(GND, LOW);  
  //pinMode(GND2, OUTPUT);  digitalWrite(GND2, LOW);
  //pinMode(VCC, OUTPUT);   digitalWrite(VCC, HIGH);

  pinMode(buzzer, OUTPUT);  pinMode(4, OUTPUT); //pin 4 usato temporaneamente come ground
  pinMode(yellow, OUTPUT);
  pinMode(green, OUTPUT);  
  pinMode(red, OUTPUT);
  digitalWrite(buzzer, LOW); digitalWrite(4, LOW);  //pin 14 usato temporaneamente come ground
  Serial.println("Buzzer Test...");

  while (!Serial);    // Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)
  SPI.begin();      // Init SPI bus
  mfrc522.PCD_Init();   // Init MFRC522
  mfrc522.PCD_DumpVersionToSerial();  // Show details of PCD - MFRC522 Card Reader details
  Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));

  delay(1000);

  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) 
  {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }

  stampaoled(VIV);    //Inizia la stampa continua
  digitalWrite(green, HIGH);  //impostazione iniziale led
  digitalWrite(yellow, LOW);
  digitalWrite(red, LOW);
  t=millis();
  Serial.println("Setup done");
//Setup audio
  Serial.println(F("DFRobot DFPlayer Mini Demo"));
  Serial.println(F("Initializing DFPlayer ... (May take 3~5 seconds)"));
  
  if (!myDFPlayer.begin(mySoftwareSerial)) {  //Use softwareSerial to communicate with mp3.
    
    Serial.println(myDFPlayer.readType(),HEX);
    Serial.println(F("Unable to begin:"));
    Serial.println(F("1.Please recheck the connection!"));
    Serial.println(F("2.Please insert the SD card!"));
    while(true);
  }
  Serial.println(F("DFPlayer Mini online."));
  myDFPlayer.setTimeOut(500); //Set serial communictaion time out 500ms
  
  //----Set volume----
  myDFPlayer.volume(25);  //Set volume value (0~30).
  myDFPlayer.volumeUp(); //Volume Up
  myDFPlayer.volumeDown(); //Volume Down
  myDFPlayer.outputDevice(DFPLAYER_DEVICE_SD);


}

void loop() {

  if(millis()==(t+attesa))  //Vero solo se dall'ultimo tag è passato più di "attesa"
  {
    flag = true;
    stampaoled(VIV);
  }

  if(!digitalRead(butt))  //leggo il pulsante e richiamo la sua routine
  {
    ButtRoutine();
    delay(300);
  }

  if(flag == true)  //riattiva la lettura delle carte
  {
    {//Reset led
      digitalWrite(green, HIGH);  //reset led
      digitalWrite(yellow, LOW);
      digitalWrite(red, LOW);
    }

  
    if ( ! mfrc522.PICC_IsNewCardPresent()) //ricerca carta
    {
      return;               //se non rileva card ritorna all'inizio del loop
    }
    if ( ! mfrc522.PICC_ReadCardSerial()) {  // Select one of the cards
      return;               //se non rileva lo UID della card ritorna all'inizio del loop
    }

    verify=0; //reset variabile di controllo, il valore deve essere il ritorno del server

    // Show some details of the PICC (that is: the tag/card)
    Serial.print(F("Card UID:")); 
    dump_byte_array(mfrc522.uid.uidByte, mfrc522.uid.size);//stampa lo uid sul monitor seriale
    Serial.println();
    Serial.println(verify);   //stampa di controllo dell'errore


    if(verify==0) //se 0 pagato, altrimenti manda l'errore con il rispettivo numero
    {
      stampaoled(PAG);
      myDFPlayer.play(1);  //Play the first mp3
      Serial.println("Play caffettino");
      digitalWrite(green, LOW);
      digitalWrite(yellow, HIGH);  

      digitalWrite(buzzer, 1);
      delay(500);
      digitalWrite(buzzer, 0);
      delay(100);
      digitalWrite(buzzer, 1);    
      delay(1000);
      digitalWrite(buzzer, 0);
   
      t = millis();
      flag = false; //reset flag per impedire la lettura di carte durante l'invio al server/lampeggio/beep
    }  
    else //come sopra, ma per gli errori
    {
      stampaoled(verify); 
      digitalWrite(green, LOW);
      digitalWrite(yellow, LOW);
      digitalWrite(red, HIGH);  

      digitalWrite(buzzer, 1);
      delay(300);
      digitalWrite(buzzer, 0);
      t = millis();
      flag = false;
    }
    state = 0;
  }

}

// Helper routine to dump a byte array as hex values to Serial
void dump_byte_array(byte *buffer, byte bufferSize) {

  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i]);      //stampo in decimale
    Serial.print("  ");

    if(controllo[i]!=buffer[i]) verify++; //verifica dello UID sostituire con invio al server
  }  
 
}

void ButtRoutine()
{
   state ^= 1;  //varia da 0 a 1 e da 1 a 0 per ogni richiamo della routine
   stampaoled(state + 7); //7 per avere un offset rispetto alle stampe di pagato ed errori 6 in tot
}
void stampaoled(int i) 
{
  switch (i)
  {

    case PAG:
    {
      display.stopscroll(); //ferma lo spostamento del testo
      display.clearDisplay(); //elimina la scritta
      delay(10);
      display.setTextSize(3); //Dimeensione font
      display.setTextColor(SSD1306_WHITE);  //colore, ma il nostro è monocromo (le prima righe gialle)
      display.setCursor(0, 22); //inizio del testo, pixel in alto a sinista, serve per centrare
      display.print("PAGATO");
      display.display();      //Attiva il testo 
      break;
    }
    case 1:
    {
      display.stopscroll();
      display.clearDisplay();
      delay(10);
      display.setTextSize(3); 
      display.setTextColor(SSD1306_WHITE);
      display.setCursor(0, 22);
      display.print("ERRORE\n\t1");
      display.display();      
      break;
    }
    case 2:
    {
      display.stopscroll();
      display.clearDisplay();
      delay(10);
      display.setTextSize(3); 
      display.setTextColor(SSD1306_WHITE);
      display.setCursor(0, 22);
      display.print("ERRORE\n\t2");
      display.display();      
      break;
    }
    case 3:
    {
      display.stopscroll();
      display.clearDisplay();
      delay(10);
      display.setTextSize(3); 
      display.setTextColor(SSD1306_WHITE);
      display.setCursor(0, 22);
      display.print("ERRORE\n\t3");
      display.display();      
      break;
    }
    case 4:
    {
      display.stopscroll();
      display.clearDisplay();
      delay(10);
      display.setTextSize(3); 
      display.setTextColor(SSD1306_WHITE);
      display.setCursor(0, 22);
      display.print("ERRORE\n\t4");
      display.display();      
      break;
    }
    case 5:
    {
      display.stopscroll();
      display.clearDisplay();
      delay(10);
      display.setTextSize(3); 
      display.setTextColor(SSD1306_WHITE);
      display.setCursor(0, 22);
      display.print("ERRORE\n\t5");
      display.display();      
      break;
    }
    case VIV:
    {
      display.clearDisplay();
      delay(10);
      display.setTextSize(2); 
      display.setTextColor(SSD1306_WHITE);
      display.setCursor(1, 17);
      display.print("  VIVERE\nCAFFETTINO");
      display.display();      
      display.startscrollleft(0x00, 0x0F);  //riattiva lo spostamento del testo con le coordinate di inizio e fine
      break;
    }    
    case 7:
    {
      display.stopscroll();
      display.clearDisplay();
      display.setTextSize(2); 
      display.setTextColor(SSD1306_WHITE);
      display.setCursor(0, 22);
      display.print("CAFFE'");
      display.display();      
      break;
    }
    case 8:
    {
      display.stopscroll();
      display.clearDisplay();
      display.setTextSize(2); 
      display.setTextColor(SSD1306_WHITE);
      display.setCursor(0, 22);
      display.print("ACQUA");
      display.display();      
      break;
    }        
  }
}

