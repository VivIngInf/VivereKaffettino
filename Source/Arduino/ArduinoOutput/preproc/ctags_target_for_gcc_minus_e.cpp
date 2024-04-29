# 1 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino"
/*

  SPI-LETTORE:

  RST  - 34

  MISO - 19

  MOSI - 23

  SCK  - 18

  SDA  - 5



  I2C-SCHERMO:

  SCL - 22

  SDA - 21

*/
# 14 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino"
// Valori segreti (Username, password)
// Bisogna avere un file rinominato "arduino_secrets.h" che segue il modello dell'example.
// Quel file non verrà condiviso con github, in modo tale che le credenziali rimangano segrete.
# 18 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino" 2

// Lib lettore
# 21 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino" 2
# 22 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino" 2

// Lib wifi
# 25 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino" 2
# 26 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino" 2

// Lib http
# 29 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino" 2
# 30 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino" 2
# 31 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino" 2

// Lib Oled
# 34 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino" 2
# 35 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino" 2
# 36 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino" 2

// Lib audio
# 39 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino" 2
# 40 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino" 2

// Credenziali wifi



const char *ssid = "eduroam"; // SSID WiFi



// Rotte
const char *serverAddressPay = "http://204.216.213.203:8000/pay";
const char *serverAddressProdotti = "http://204.216.213.203:8000/prodotti";
WiFiClient wifiClient;

// Gestione prodotti


class Prodotto
{
public:
 String id;
 String nome;
 String prezzo;
};

LinkedList<Prodotto *> listaProdotti = LinkedList<Prodotto *>(); // Array dei prodotti disponibili
int currentProdotto = 0;

int pointer = 0;
int IDProdotto = 1;

JsonArray products;

// Codici di stampa per la funzione stampaOled()
# 85 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino"
int alreadyPrint = 0; // Se abbiamo già printato qualcosa

// Periferiche
# 96 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino"
// Impostazione schermo







// Creazione "oggetto" display
Adafruit_SSD1306 display(128 /* OLED display width, in pixels*/, 64 /* OLED display height, in pixels*/, &Wire, -1 /* Reset pin # (or -1 if sharing Arduino reset pin)*/);
void stampaoled(int i);

// Impostazione lettore
constexpr uint8_t RST_PIN = 34; // Pin di reset
constexpr uint8_t SS_PIN = 5; // Pin dati
int controllo[12] = {195, 227, 250, 166}; // Codice UID di un tag
int verify = 0; // Variabile di controllo della differenza tra UID letto e salvato
MFRC522 mfrc522(SS_PIN, RST_PIN); // Create MFRC522 instance

// Impostazione audio
HardwareSerial mySoftwareSerial(1);
DFRobotDFPlayerMini myDFPlayer;

// Gestione temporale
long long int t;
bool flag = true;

bool firstBoot = true;

long long int t3; // variabile temporale per la pressione prolungata
int durata = 5000; // costante in ms per la pressione 5sec kaffettino, 10sec bella ciao, 15sec faccetta
int pressed = 0; // variabile che controlla se il pulsante è premuto ed è già stato azzerato t3
int butt = 15; // pin del pulsante

void setup()
{

 mySoftwareSerial.begin(9600, SERIAL_8N1, 32, 33); // speed, type, RX, TX
 Serial.begin(115200); // Initialize serial communications with the PC
 delay(1000);
 Serial.println("Setup");

 pinMode(butt, 0x05);
 pinMode(14 /* Ground*/, 0x03);
 digitalWrite(14 /* Ground*/, 0x0);
 // pinMode(GND2, OUTPUT);  digitalWrite(GND2, LOW);
 // pinMode(VCC, OUTPUT);   digitalWrite(VCC, HIGH);

 pinMode(16 /* Buzzer signal*/, 0x03);
 pinMode(4, 0x03); // pin 4 usato temporaneamente come ground
 pinMode(26 /* Led Giallo*/, 0x03);
 pinMode(27 /* Led verde*/, 0x03);
 pinMode(12 /* Led rosso*/, 0x03);
 digitalWrite(16 /* Buzzer signal*/, 0x0);
 digitalWrite(4, 0x0); // pin 14 usato temporaneamente come ground
 Serial.println("Buzzer Test...");

 //  debouncer.attach(butt);
 //  debouncer.interval(10);
 pinMode(butt, 0x05);
 t3 = millis();
 while (!Serial)
  ; // Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)
 SPI.begin(); // Init SPI bus
 mfrc522.PCD_Init(); // Init MFRC522
 mfrc522.PCD_DumpVersionToSerial(); // Show details of PCD - MFRC522 Card Reader details
 Serial.println(((reinterpret_cast<const __FlashStringHelper *>(("Scan PICC to see UID, SAK, type, and data blocks...")))));

 if (!display.begin(0x02 /*|< Gen. display voltage from 3.3V*/, 0x3C /* See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32*/))
 {
  Serial.println(((reinterpret_cast<const __FlashStringHelper *>(("SSD1306 allocation failed")))));
  while (true) // non procedere, cicla all'infinito
  {
   delay(1000);
   digitalWrite(12 /* Led rosso*/, 0x1);
   delay(1000);
   digitalWrite(12 /* Led rosso*/, 0x0);
  }
 }

 connettiWifi(); // Ci connettiamo al wifi

 setupAudio(); // Setup modulo sd audio

 getProdotti(); // Chiediamo al server di mandarci i prodotti dell'auletta

 setupDisplay(); // Stato di default del display
}

void loop()
{
 // Se non siamo connessi allora blocca tutto
 if (WiFi.status() != WL_CONNECTED)
 {
  Serial.println("Connessione WiFi mancante, riprovo a connettermi...");
  stampaoled(11 /* Non c'è connessione*/);

  digitalWrite(27 /* Led verde*/, 0x0);
  digitalWrite(26 /* Led Giallo*/, 0x0);

  digitalWrite(12 /* Led rosso*/, 0x1);
  delay(1000);
  digitalWrite(12 /* Led rosso*/, 0x0);
  delay(1000);

  t = millis();
  flag = 0;

  return;
 }

 // Se non siamo riusciti a connetterci al server ma il wifi c'è vuol dire che c'è stato un problema al server
 while (verify == 13 /* C'è satto un errore nella richiesta http*/)
 {
  flag = 0; // Disabilitiamo tutto

  if (!digitalRead(butt)) // Se il pulsante è premuto riproviamo
  {
   digitalWrite(16 /* Buzzer signal*/, 1);
   delay(1000);
   digitalWrite(16 /* Buzzer signal*/, 0);
   delay(500);
   getProdotti(); // Chiediamo al server di mandarci i prodotti dell'auletta
  }

  if (verify == 13 /* C'è satto un errore nella richiesta http*/ && alreadyPrint == 0)
  {
   digitalWrite(27 /* Led verde*/, 0x0);
   digitalWrite(26 /* Led Giallo*/, 0x0);
   digitalWrite(12 /* Led rosso*/, 0x1);

   stampaoled(13 /* C'è satto un errore nella richiesta http*/);
   alreadyPrint = 1;

   Serial.println("ERRORE HTTP!!!");
  }
  else if (verify != 13 /* C'è satto un errore nella richiesta http*/)
  {
   Serial.println("ABEMUS PRODOTTI!!!");
   flag = 1;

   if (verify != 69)
    stampaoled(6);
   else
    stampaoled(69 /* Il bro che ha acquistato ha compiuto gli anni*/);

   delay(2000);
   break;
  }
 }

 // if(!firstBoot)
 //   checkButtonPressed();

 if (!digitalRead(butt) && pressed == 0) // Pressione del tasto
 {
  pressed = 1; // metto ad 1 per non far rientrare in questo if durante la pressione
  t3 = millis(); //"azzero" t3 rispetto  millis per avere un punto temporale di partenza
  Serial.println("Premuto");
  buttRoutine(); // alla pressione richiamo la funziona per il cambio prodotto
 }

 if (digitalRead(butt) && pressed == 1) // Rilascio del tasto
 {
  pressed = 0; // Riazzero per riabilitare la lettura della pressione
  if (millis() > (t3 + durata) && millis() < (t3 + (2 * durata))) // Se sono passati 5 secondi
  {
   myDFPlayer.play(1); // Play the first mp3
   Serial.println("Play caffettino");
   stampaoled(6);
   currentProdotto = 0; // se parte la musica resetto il prodotto
  }
  else if (millis() > (t3 + (2 * durata)) /*&& millis() < (t3 + (3 * durata))*/) // Se sono passati 10 secondi
  {
   playCompleanno();
   stampaoled(6);
   currentProdotto = 0; // se parte la musica resetto il prodotto
  }
  /*else if(millis() > (t3 + (3 * durata)) )  //Se sono passati 15 secondi

		{

		  myDFPlayer.play(2);  //Play the first mp3

		  Serial.println("Faccetta nera");

		  stampaoled(VIV);

		  currentProdotto = 0; //se parte la musica resetto il prodotto

		}*/
# 281 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino"
  Serial.println("Rilasciato");
 }

 if (firstBoot == true)
 {
  stampaoled(6);
  myDFPlayer.play(1);
  firstBoot = false;
 }

 if (millis() == (t + 3000)) // Vero solo se dall'ultimo tag è passato più di "attesa"
 {
  flag = true;
  stampaoled(6);
 }

 if (flag == true) // riattiva la lettura delle carte
 {

  // reset led
  digitalWrite(27 /* Led verde*/, 0x1);
  digitalWrite(26 /* Led Giallo*/, 0x0);
  digitalWrite(12 /* Led rosso*/, 0x0);

  // Se non rileva la card o la card non ha un numero seriale
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial())
  {
   return; // Ritorna all'inizio del loop
  }

  verify = 0; // reset variabile di controllo, il valore deve essere il ritorno del server

  logCard(); // Siccome è stata riconosciuta una card, logghiamo le sue caratteristiche.

  pay();

  currentProdotto = 0; // Resettiamo il prodottoCorrente al primo della lista.
  flag = false; // Reset flag per impedire la lettura di carte durante l'invio al server/lampeggio/beep
  t = millis(); // Reset t perché è stata letta una carta

  if (verify != 0) // Se il codice di ritorno non è 0 questo vuol dire che c'è stato un errore.
  {
   stampaoled(verify); // Mandiamo a schermo l'errore

   digitalWrite(27 /* Led verde*/, 0x0);
   digitalWrite(26 /* Led Giallo*/, 0x0);
   digitalWrite(12 /* Led rosso*/, 0x1); // Led rosso simboleggia errore

   // Segnale acustico
   digitalWrite(16 /* Buzzer signal*/, 1);
   delay(300);
   digitalWrite(16 /* Buzzer signal*/, 0);

   t = millis();

   return;
  }

  // Se è stato pagato

  stampaoled(0);
  digitalWrite(27 /* Led verde*/, 0x0);
  digitalWrite(26 /* Led Giallo*/, 0x1);

  digitalWrite(16 /* Buzzer signal*/, 1);
  delay(500);
  digitalWrite(16 /* Buzzer signal*/, 0);
  delay(100);
  digitalWrite(16 /* Buzzer signal*/, 1);
  delay(1000);
  digitalWrite(16 /* Buzzer signal*/, 0);
 }
}

void connettiWifi()
{
 if (true)
 {
  WiFi.begin(ssid, WPA2_AUTH_PEAP, "danieleorazio.susino" /* Es: mario.rossi03*/ /* Es: mario.rossi03*/, "danieleorazio.susino" /* Es: mario.rossi03*/ /* Stesso di EAP_IDENTITY*/, "#Matricola25!#"); // Passiamo le credenziali e istanziamo una nuova connessione
 }
 else
 {
  WiFi.begin("", "");
 }

 while (WiFi.status() != WL_CONNECTED) // Se non siamo ancora connessi
 {
  Serial.println("Connessione WiFi in corso...");

  digitalWrite(27 /* Led verde*/, 0x0);
  digitalWrite(12 /* Led rosso*/, 0x0); // Accendiamo solo il LED rosso
  digitalWrite(26 /* Led Giallo*/, 0x0);

  delay(1000);
  digitalWrite(26 /* Led Giallo*/, 0x1);
  delay(1000);

  stampaoled(12 /* Ci stiamo connettendo*/); // Stampiamo che non c'è connessione

  if (flag == 1)
  {
   flag = 0;
  }
 }

 flag = 1;

 Serial.println("Connesso alla rete WiFi");
}

// Helper routine to dump a byte array as hex values to Serial
void dump_byte_array(byte *buffer, byte bufferSize)
{

 for (byte i = 0; i < bufferSize; i++)
 {
  Serial.print(buffer[i]); // stampo in decimale
  Serial.print("  ");

  if (controllo[i] != buffer[i])
   verify++; // verifica dello UID sostituire con invio al server
 }
}

void logCard()
{
 // Show some details of the PICC (that is: the tag/card)
 Serial.print(((reinterpret_cast<const __FlashStringHelper *>(("Card UID:")))));
 dump_byte_array(mfrc522.uid.uidByte, mfrc522.uid.size); // stampa lo uid sul monitor seriale
 Serial.println();
 Serial.println(verify); // stampa di controllo dell'errore
}

/*void checkButtonPressed()

{

  debouncer.update();  // Aggiorna lo stato del pulsante



  int reading = debouncer.read();  // Leggi lo stato del pulsante

  if (reading != lastButtonState) {

	lastDebounceTime = millis();

  }



  if ((millis() - lastDebounceTime) > 50) {

	// Se è trascorso abbastanza tempo dal debounce

	if (reading != buttonState)

	{

	  buttonState = reading;



	  if (buttonState == HIGH)

	  {

		// Se il pulsante è stato rilasciato

		unsigned long pressDuration = millis() - pressStartTime;



		if (pressDuration >= 4000 && pressDuration < 10000)

		{

		  // Se il pulsante è stato tenuto premuto per almeno 4 secondi

		  Serial.println("Pulsante tenuto premuto per 4 secondi");

		  myDFPlayer.play(1);  //Play the first mp3

		  Serial.println("Play caffettino");

		}

		else if(pressDuration >= 10000 && pressDuration < 15000)

		{

		  // Se il pulsante è stato tenuto premuto per almeno 10 secondi

		  Serial.println("Pulsante tenuto premuto per 10 secondi");

		  myDFPlayer.play(3);  //Play the first mp3

		  Serial.println("Play bella ciao");

		}

		else if(pressDuration >= 15000)

		{

		  // Se il pulsante è stato tenuto premuto per almeno 15 secondi

		  Serial.println("Pulsante tenuto premuto per 15 secondi");

		  myDFPlayer.play(2);  //Play the first mp3

		  Serial.println("Play faccetta nera");

		}

		else

		{

		  // Altrimenti è stato eseguito solo un click

		  Serial.println("Click del pulsante");

		  buttRoutine(); // Il pulsante è solo stato clicckato

		}

	  }

	  else

	  {

		pressStartTime = millis();

	  }

	}

  }



  lastButtonState = reading;

}

*/
# 472 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino"
void buttRoutine()
{
 currentProdotto++;

 if (currentProdotto >= listaProdotti.size())
  currentProdotto = 0;

 stampaoled(7); // 7 per avere un offset rispetto alle stampe di pagato ed errori 6 in tot
}

void setupAudio() // Funzione che inizializza il playermp3
{
 Serial.println(((reinterpret_cast<const __FlashStringHelper *>(("DFRobot DFPlayer Mini Demo")))));
 Serial.println(((reinterpret_cast<const __FlashStringHelper *>(("Initializing DFPlayer ... (May take 3~5 seconds)")))));

 if (!myDFPlayer.begin(mySoftwareSerial))
 { // Use softwareSerial to communicate with mp3.

  Serial.println(myDFPlayer.readType(), 16);
  Serial.println(((reinterpret_cast<const __FlashStringHelper *>(("Unable to begin:")))));
  Serial.println(((reinterpret_cast<const __FlashStringHelper *>(("1.Please recheck the connection!")))));
  Serial.println(((reinterpret_cast<const __FlashStringHelper *>(("2.Please insert the SD card!")))));
  while (true)
   ;
 }

 Serial.println(((reinterpret_cast<const __FlashStringHelper *>(("DFPlayer Mini online.")))));
 myDFPlayer.setTimeOut(500); // Set serial communictaion time out 500ms

 //----Set volume----
 myDFPlayer.volume(25); // Set volume value (0~30).
 myDFPlayer.volumeUp(); // Volume Up
 myDFPlayer.volumeDown(); // Volume Down
 myDFPlayer.outputDevice(2);
}

void setupDisplay()
{
 digitalWrite(27 /* Led verde*/, 0x1); // impostazione iniziale led
 digitalWrite(26 /* Led Giallo*/, 0x0);
 digitalWrite(12 /* Led rosso*/, 0x0);
 t = millis();
 Serial.println("Setup done");
}

void getProdotti()
{
 const size_t bufferSize =
# 519 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino"

# 519 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino"
 
# 519 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino" 3
                          (ArduinoJson::detail::sizeofObject(
# 519 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino"
                          1
# 519 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino" 3
                          ))
# 519 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino"
                                             ;
 DynamicJsonDocument doc(bufferSize);

 // Passiamo alla richiesta get il parametro ID_AULETTA
 doc["ID_Auletta"] = 1;

 // Formattiamo il parametro in json
 String jsonString;
 serializeJson(doc, jsonString);

 // Avviamo la richiesta HTTP
 HTTPClient http;
 http.begin(wifiClient, serverAddressProdotti);
 http.addHeader("Content-Type", "application/json");
 int httpResponseCode = http.POST(jsonString); // Passiamo come body il json

 Serial.print("HTTP Response code: ");
 Serial.println(httpResponseCode); // Stampiamo il codice di risposta
 String response;

 // Se il codice di risposta è maggiore di 0 vuol dire che è stato un successo e possiamo mostrare la response
 if (httpResponseCode > 0)
 {
  response = http.getString();
  Serial.print("Response Body: ");
  Serial.println(response);
  verify = 0; // resettiamo verify
 }
 else
 {
  Serial.println("Errore nella richiesta HTTP");
  verify = 13 /* C'è satto un errore nella richiesta http*/;
 }

 // Free resources
 http.end();

 if (verify == 13 /* C'è satto un errore nella richiesta http*/)
  return;

 // Trasformiamo in json la rispsota che ci ha dato il server
 DynamicJsonDocument docResponse(1024);
 DeserializationError error = deserializeJson(docResponse, response);

 // Se c'è stato un errore nel deserializzare la risposta ritorniamo
 if (error)
 {
  Serial.print("deserializeJson() failed: ");
  Serial.println(error.f_str());
  return;
 }

 // La risposta in json la trasformiamo in un array
 products = docResponse.as<JsonArray>();

 // Per ogni prodotto nella lista di json objects ne creiamo uno con la nostra struct Prodotto
 for (JsonObject product : products)
 {
  Prodotto *prodotto = new Prodotto();
  prodotto->id = product["ID_Prodotto"].as<String>().c_str();
  prodotto->nome = product["descrizione"].as<String>().c_str();
  prodotto->prezzo = product["costo"].as<String>().c_str();

  listaProdotti.add(prodotto);
 }

 // Stampiamo in seriale i prodotti che questa auletta vende
 for (int i = 0; i < listaProdotti.size(); i++)
 {
  Prodotto *p = listaProdotti.get(i);
  Serial.print(p->id);
  Serial.print("\t");
  Serial.print(p->nome);
  Serial.print("\t");
  Serial.print(p->prezzo);
  Serial.println("");
 }
}

void pay()
{
 const size_t bufferSize =
# 600 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino"

# 600 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino"
 
# 600 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino" 3
                          (ArduinoJson::detail::sizeofObject(
# 600 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino"
                          1
# 600 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino" 3
                          ))
# 600 "D:\\Programmazione\\Vivere\\VivereKaffettino\\Source\\Arduino\\ESP32_Kaffettino\\ESP32_Kaffettino.ino"
                                             ;
 DynamicJsonDocument doc(bufferSize);

 // ID_Card che manderemo al server
 String ID_Card = "";
 for (int i = 0; i < mfrc522.uid.size; i++)
 {
  ID_Card += String(mfrc522.uid.uidByte[i]);
 }

 // Passiamo alla richiesta POST i parametri
 doc["ID_Card"] = ID_Card;
 doc["ID_Auletta"] = 1;
 doc["ID_Prodotto"] = listaProdotti.get(currentProdotto)->id;

 // Formattiamo i parametri in json
 String jsonString;
 serializeJson(doc, jsonString);

 // Avviamo la richiesta HTTP
 HTTPClient http;
 http.begin(wifiClient, serverAddressPay);
 http.addHeader("Content-Type", "application/json");
 int httpResponseCode = http.POST(jsonString); // Passiamo come body il json

 Serial.print("HTTP Response code: ");
 Serial.println(httpResponseCode); // Stampiamo il codice di risposta
 String response;

 // Se il codice di risposta è maggiore di 0 vuol dire che è stato un successo e possiamo mostrare la response
 if (httpResponseCode > 0)
 {
  response = http.getString();

  Serial.print("Response Body: ");
  Serial.println(response);

  verify = response.toInt(); // Settiamo verify a response perché così possiamo gestire i vari casi della risposta
 }
 else
 {
  Serial.println("Errore nella richiesta HTTP");
  verify = 13 /* C'è satto un errore nella richiesta http*/;
 }

 // Free resources
 http.end();
}

void stampaoled(int i)
{
 switch (i)
 {

 case 0:
 {
  display.stopscroll(); // ferma lo spostamento del testo
  display.clearDisplay(); // elimina la scritta
  delay(10);
  display.setTextSize(3); // Dimensione font
  display.setTextColor(1 /*|< Draw 'on' pixels*/); // colore, ma il nostro è monocromo (le prima righe gialle)
  display.setCursor(13, 22); // inizio del testo, pixel in alto a sinista, serve per centrare
  display.print("PAGATO");
  display.display(); // Attiva il testo
  break;
 }
 case 1 /* Non hai abbastanza saldo nella carta per quel determinato prodotto*/:
 {
  display.stopscroll();
  display.clearDisplay();
  delay(10);
  display.setTextSize(2);
  display.setTextColor(1 /*|< Draw 'on' pixels*/);
  display.setCursor(20, 12);
  display.print("SALDO NON");
  display.setCursor(10, 35);
  display.print("SUFF.");
  display.display();
  break;
 }
 case 2 /* Non esiste la carta nel database*/:
 {
  display.stopscroll();
  display.clearDisplay();
  delay(10);
  display.setTextSize(2);
  display.setTextColor(1 /*|< Draw 'on' pixels*/);
  display.setCursor(17, 15);
  display.print("CARD NON");
  display.setCursor(10, 35);
  display.print("ESISTENTE");
  display.display();
  break;
 }
 case 3 /* Non esiste il prodotto nel database (cosa che non dovrebbe comunque succedere)*/:
 {
  display.stopscroll();
  display.clearDisplay();
  delay(10);
  display.setTextSize(2);
  display.setTextColor(1 /*|< Draw 'on' pixels*/);
  display.setCursor(20, 15);
  display.print("PROD NON");
  display.setCursor(10, 35);
  display.print("ESISTENTE");
  display.display();
  break;
 }
 case 6:
 {
  display.clearDisplay();
  delay(10);
  display.setTextSize(2);
  display.setTextColor(1 /*|< Draw 'on' pixels*/);
  display.setCursor(1, 17);
  display.print("  VIVERE\nKAFFETTINO");
  display.display();
  display.startscrollleft(0x00, 0x0F); // riattiva lo spostamento del testo con le coordinate di inizio e fine
  break;
 }
 case 7 /* Stampa il prodotto con id == currentProdotto*/:
 {
  Prodotto *p = listaProdotti.get(currentProdotto);
  display.stopscroll();
  display.clearDisplay();
  delay(10);
  display.setTextSize(2);
  display.setTextColor(1 /*|< Draw 'on' pixels*/);
  display.setCursor(35, 15);
  display.print(p->nome);
  display.setCursor(45, 35);
  display.print(p->prezzo);
  display.display();
  break;
 }
 case 12 /* Ci stiamo connettendo*/:
 {
  display.stopscroll();
  display.clearDisplay();
  display.setTextSize(2); // Draw 2X-scale text
  display.setTextColor(1 /*|< Draw 'on' pixels*/);

  display.setCursor(5, 17);
  display.print("CONNECTING");
  display.display(); // Show text

  display.setCursor(46, 40);
  display.print(".");
  delay(200);
  display.display(); // Show text

  display.print(".");
  delay(200);
  display.display(); // Show text

  display.print(".");
  delay(200);
  display.display(); // Show initial text

  break;
 }
 case 69 /* Il bro che ha acquistato ha compiuto gli anni*/:
 {
  Serial.println("AUGURIIIIII!");

  display.stopscroll();
  display.clearDisplay();
  display.setTextSize(2); // Draw 2X-scale text
  display.setTextColor(1 /*|< Draw 'on' pixels*/);

  display.setCursor(25, 30);
  display.print("AUGURI!");
  display.display(); // Show text

  playCompleanno();

  break;
 }
 case 13 /* C'è satto un errore nella richiesta http*/:
 {
  display.stopscroll();
  display.clearDisplay();
  display.setTextSize(2); // Draw 2X-scale text
  display.setTextColor(1 /*|< Draw 'on' pixels*/);

  display.setCursor(5, 5);
  display.print("SERV ERROR");
  display.display(); // Show text

  display.setCursor(17, 25);
  display.print("CONTATTA");
  display.setCursor(35, 45);
  display.print("ADMIN");
  delay(200);
  display.display(); // Show text

  break;
 }
 }
}

void playCompleanno()
{
 myDFPlayer.play(2); // Play the first mp3
 Serial.println("Play Bella Ciao");
}
