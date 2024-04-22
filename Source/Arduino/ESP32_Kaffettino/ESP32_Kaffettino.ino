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

// Valori segreti (Username, password)
// Bisogna avere un file rinominato "arduino_secrets.h" che segue il modello dell'example.
// Quel file non verrà condiviso con github, in modo tale che le credenziali rimangano segrete.
#include "arduino_secrets.h"

// Lib lettore
#include <SPI.h>
#include <MFRC522.h> // MFRC522 by Github Community

// Lib wifi
#include "WiFi.h"
#include "esp_wpa2.h"

// Lib http
#include <HTTPClient.h>	 // Basilare con Esp32
#include <ArduinoJson.h> // Arduinojson by Benoit Blanchon
#include <LinkedList.h>	 // LinkedList by Ivan Seidel

// Lib Oled
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h> // Adafruit SSD1306 by Adafruit (Con dipendenze)

// Lib audio
#include <Arduino.h>
#include "DFRobotDFPlayerMini.h" // DFRobotDFPlayerMini by DFRobot

// Credenziali wifi
#define EAP_IDENTITY SECRET_USERNAME // Es: mario.rossi03
#define EAP_PASSWORD SECRET_PASSWORD
#define EAP_USERNAME SECRET_USERNAME // Stesso di EAP_IDENTITY
const char *ssid = "eduroam";		 // SSID WiFi

#define usingUniversityWifi false

// Rotte
const char *serverAddressPay = "http://204.216.213.203:8000/pay";
const char *serverAddressProdotti = "http://204.216.213.203:8000/prodotti";
WiFiClient wifiClient;

// Gestione prodotti
#define ID_AULETTA 1

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
#define PAGATO 0	  // Il pagamento è andato a buon fine
#define NOSALDO 1	  // Non hai abbastanza saldo nella carta per quel determinato prodotto
#define NOCARD 2	  // Non esiste la carta nel database
#define NOPROD 3	  // Non esiste il prodotto nel database (cosa che non dovrebbe comunque succedere)
#define STAMPAPROD 7  // Stampa il prodotto con id == currentProdotto
#define VIV 10		  // Codice di stampa vivere kaffettino
#define NOC 11		  // Non c'è connessione
#define CONNECTING 12 // Ci stiamo connettendo
#define HTTPERR 13	  // C'è satto un errore nella richiesta http
#define AUGURI 69	  // Il bro che ha acquistato ha compiuto gli anni

int alreadyPrint = 0; // Se abbiamo già printato qualcosa

// Periferiche
#define green 27  // Led verde
#define yellow 26 // Led Giallo
#define red 12	  // Led rosso
#define GND 14	  // Ground
#define GND2 35	  // 2° Ground
#define VCC 17	  // VCC
#define buzzer 16 // Buzzer signal

// Impostazione schermo
#define SCREEN_WIDTH 128	// OLED display width, in pixels
#define SCREEN_HEIGHT 64	// OLED display height, in pixels
#define OLED_RESET -1		// Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C // See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
#define VIV 6
#define PAG 0

// Creazione "oggetto" display
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
void stampaoled(int i);

// Impostazione lettore
constexpr uint8_t RST_PIN = 34;			  // Pin di reset
constexpr uint8_t SS_PIN = 5;			  // Pin dati
int controllo[12] = {195, 227, 250, 166}; // Codice UID di un tag
int verify = 0;							  // Variabile di controllo della differenza tra UID letto e salvato
MFRC522 mfrc522(SS_PIN, RST_PIN);		  // Create MFRC522 instance

// Impostazione audio
HardwareSerial mySoftwareSerial(1);
DFRobotDFPlayerMini myDFPlayer;

// Gestione temporale
long long int t;
bool flag = true;
#define attesa 3000
bool firstBoot = true;

long long int t3;  // variabile temporale per la pressione prolungata
int durata = 5000; // costante in ms per la pressione 5sec kaffettino, 10sec bella ciao, 15sec faccetta
int pressed = 0;   // variabile che controlla se il pulsante è premuto ed è già stato azzerato t3
int butt = 15;	   // pin del pulsante

void setup()
{

	mySoftwareSerial.begin(9600, SERIAL_8N1, 32, 33); // speed, type, RX, TX
	Serial.begin(115200);							  // Initialize serial communications with the PC
	delay(1000);
	Serial.println("Setup");

	pinMode(butt, INPUT_PULLUP);
	pinMode(GND, OUTPUT);
	digitalWrite(GND, LOW);
	// pinMode(GND2, OUTPUT);  digitalWrite(GND2, LOW);
	// pinMode(VCC, OUTPUT);   digitalWrite(VCC, HIGH);

	pinMode(buzzer, OUTPUT);
	pinMode(4, OUTPUT); // pin 4 usato temporaneamente come ground
	pinMode(yellow, OUTPUT);
	pinMode(green, OUTPUT);
	pinMode(red, OUTPUT);
	digitalWrite(buzzer, LOW);
	digitalWrite(4, LOW); // pin 14 usato temporaneamente come ground
	Serial.println("Buzzer Test...");

	//  debouncer.attach(butt);
	//  debouncer.interval(10);
	pinMode(butt, INPUT_PULLUP);
	t3 = millis();
	while (!Serial)
		;							   // Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)
	SPI.begin();					   // Init SPI bus
	mfrc522.PCD_Init();				   // Init MFRC522
	mfrc522.PCD_DumpVersionToSerial(); // Show details of PCD - MFRC522 Card Reader details
	Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));

	if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS))
	{
		Serial.println(F("SSD1306 allocation failed"));
		while (true) // non procedere, cicla all'infinito
		{
			delay(1000);
			digitalWrite(red, HIGH);
			delay(1000);
			digitalWrite(red, LOW);
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
		stampaoled(NOC);

		digitalWrite(green, LOW);
		digitalWrite(yellow, LOW);

		digitalWrite(red, HIGH);
		delay(1000);
		digitalWrite(red, LOW);
		delay(1000);

		t = millis();
		flag = 0;

		return;
	}

	// Se non siamo riusciti a connetterci al server ma il wifi c'è vuol dire che c'è stato un problema al server
	while (verify == HTTPERR)
	{
		flag = 0; // Disabilitiamo tutto

		if (!digitalRead(butt)) // Se il pulsante è premuto riproviamo
		{
			digitalWrite(buzzer, 1);
			delay(1000);
			digitalWrite(buzzer, 0);
			delay(500);
			getProdotti(); // Chiediamo al server di mandarci i prodotti dell'auletta
		}

		if (verify == HTTPERR && alreadyPrint == 0)
		{
			digitalWrite(green, LOW);
			digitalWrite(yellow, LOW);
			digitalWrite(red, HIGH);

			stampaoled(HTTPERR);
			alreadyPrint = 1;

			Serial.println("ERRORE HTTP!!!");
		}
		else if (verify != HTTPERR)
		{
			Serial.println("ABEMUS PRODOTTI!!!");
			flag = 1;

			if (verify != 69)
				stampaoled(VIV);
			else
				stampaoled(AUGURI);

			delay(2000);
			break;
		}
	}

	// if(!firstBoot)
	//   checkButtonPressed();

	if (!digitalRead(butt) && pressed == 0) // Pressione del tasto
	{
		pressed = 1;   // metto ad 1 per non far rientrare in questo if durante la pressione
		t3 = millis(); //"azzero" t3 rispetto  millis per avere un punto temporale di partenza
		Serial.println("Premuto");
		buttRoutine(); // alla pressione richiamo la funziona per il cambio prodotto
	}

	if (digitalRead(butt) && pressed == 1) // Rilascio del tasto
	{
		pressed = 0;													// Riazzero per riabilitare la lettura della pressione
		if (millis() > (t3 + durata) && millis() < (t3 + (2 * durata))) // Se sono passati 5 secondi
		{
			myDFPlayer.play(1); // Play the first mp3
			Serial.println("Play caffettino");
			stampaoled(VIV);
			currentProdotto = 0; // se parte la musica resetto il prodotto
		}
		else if (millis() > (t3 + (2 * durata)) /*&& millis() < (t3 + (3 * durata))*/) // Se sono passati 10 secondi
		{
			playCompleanno();
			stampaoled(VIV);
			currentProdotto = 0; // se parte la musica resetto il prodotto
		}
		/*else if(millis() > (t3 + (3 * durata)) )  //Se sono passati 15 secondi
		{
		  myDFPlayer.play(2);  //Play the first mp3
		  Serial.println("Faccetta nera");
		  stampaoled(VIV);
		  currentProdotto = 0; //se parte la musica resetto il prodotto
		}*/
		Serial.println("Rilasciato");
	}

	if (firstBoot == true)
	{
		stampaoled(VIV);
		myDFPlayer.play(1);
		firstBoot = false;
	}

	if (millis() == (t + attesa)) // Vero solo se dall'ultimo tag è passato più di "attesa"
	{
		flag = true;
		stampaoled(VIV);
	}

	if (flag == true) // riattiva la lettura delle carte
	{

		// reset led
		digitalWrite(green, HIGH);
		digitalWrite(yellow, LOW);
		digitalWrite(red, LOW);

		// Se non rileva la card o la card non ha un numero seriale
		if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial())
		{
			return; // Ritorna all'inizio del loop
		}

		verify = 0; // reset variabile di controllo, il valore deve essere il ritorno del server

		logCard(); // Siccome è stata riconosciuta una card, logghiamo le sue caratteristiche.

		pay();

		currentProdotto = 0; // Resettiamo il prodottoCorrente al primo della lista.
		flag = false;		 // Reset flag per impedire la lettura di carte durante l'invio al server/lampeggio/beep
		t = millis();		 // Reset t perché è stata letta una carta

		if (verify != 0) // Se il codice di ritorno non è 0 questo vuol dire che c'è stato un errore.
		{
			stampaoled(verify); // Mandiamo a schermo l'errore

			digitalWrite(green, LOW);
			digitalWrite(yellow, LOW);
			digitalWrite(red, HIGH); // Led rosso simboleggia errore

			// Segnale acustico
			digitalWrite(buzzer, 1);
			delay(300);
			digitalWrite(buzzer, 0);

			t = millis();

			return;
		}

		// Se è stato pagato

		stampaoled(PAG);
		digitalWrite(green, LOW);
		digitalWrite(yellow, HIGH);

		digitalWrite(buzzer, 1);
		delay(500);
		digitalWrite(buzzer, 0);
		delay(100);
		digitalWrite(buzzer, 1);
		delay(1000);
		digitalWrite(buzzer, 0);
	}
}

void connettiWifi()
{
	if (usingUniversityWifi)
	{
		WiFi.begin(ssid, WPA2_AUTH_PEAP, EAP_IDENTITY, EAP_USERNAME, EAP_PASSWORD); // Passiamo le credenziali e istanziamo una nuova connessione
	}
	else
	{
		WiFi.begin(SECRET_SSID, SECRET_WifiPwd);
	}

	while (WiFi.status() != WL_CONNECTED) // Se non siamo ancora connessi
	{
		Serial.println("Connessione WiFi in corso...");

		digitalWrite(green, LOW);
		digitalWrite(red, LOW); // Accendiamo solo il LED rosso
		digitalWrite(yellow, LOW);

		delay(1000);
		digitalWrite(yellow, HIGH);
		delay(1000);

		stampaoled(CONNECTING); // Stampiamo che non c'è connessione

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
	Serial.print(F("Card UID:"));
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
void buttRoutine()
{
	currentProdotto++;

	if (currentProdotto >= listaProdotti.size())
		currentProdotto = 0;

	stampaoled(7); // 7 per avere un offset rispetto alle stampe di pagato ed errori 6 in tot
}

void setupAudio() // Funzione che inizializza il playermp3
{
	Serial.println(F("DFRobot DFPlayer Mini Demo"));
	Serial.println(F("Initializing DFPlayer ... (May take 3~5 seconds)"));

	if (!myDFPlayer.begin(mySoftwareSerial))
	{ // Use softwareSerial to communicate with mp3.

		Serial.println(myDFPlayer.readType(), HEX);
		Serial.println(F("Unable to begin:"));
		Serial.println(F("1.Please recheck the connection!"));
		Serial.println(F("2.Please insert the SD card!"));
		while (true)
			;
	}

	Serial.println(F("DFPlayer Mini online."));
	myDFPlayer.setTimeOut(500); // Set serial communictaion time out 500ms

	//----Set volume----
	myDFPlayer.volume(25);	 // Set volume value (0~30).
	myDFPlayer.volumeUp();	 // Volume Up
	myDFPlayer.volumeDown(); // Volume Down
	myDFPlayer.outputDevice(DFPLAYER_DEVICE_SD);
}

void setupDisplay()
{
	digitalWrite(green, HIGH); // impostazione iniziale led
	digitalWrite(yellow, LOW);
	digitalWrite(red, LOW);
	t = millis();
	Serial.println("Setup done");
}

void getProdotti()
{
	const size_t bufferSize = JSON_OBJECT_SIZE(1);
	DynamicJsonDocument doc(bufferSize);

	// Passiamo alla richiesta get il parametro ID_AULETTA
	doc["ID_Auletta"] = ID_AULETTA;

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
		verify = HTTPERR;
	}

	// Free resources
	http.end();

	if (verify == HTTPERR)
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
	const size_t bufferSize = JSON_OBJECT_SIZE(1);
	DynamicJsonDocument doc(bufferSize);

	// ID_Card che manderemo al server
	String ID_Card = "";
	for (int i = 0; i < mfrc522.uid.size; i++)
	{
		ID_Card += String(mfrc522.uid.uidByte[i]);
	}

	// Passiamo alla richiesta POST i parametri
	doc["ID_Card"] = ID_Card;
	doc["ID_Auletta"] = ID_AULETTA;
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
		verify = HTTPERR;
	}

	// Free resources
	http.end();
}

void stampaoled(int i)
{
	switch (i)
	{

	case PAG:
	{
		display.stopscroll();	// ferma lo spostamento del testo
		display.clearDisplay(); // elimina la scritta
		delay(10);
		display.setTextSize(3);				 // Dimensione font
		display.setTextColor(SSD1306_WHITE); // colore, ma il nostro è monocromo (le prima righe gialle)
		display.setCursor(13, 22);			 // inizio del testo, pixel in alto a sinista, serve per centrare
		display.print("PAGATO");
		display.display(); // Attiva il testo
		break;
	}
	case NOSALDO:
	{
		display.stopscroll();
		display.clearDisplay();
		delay(10);
		display.setTextSize(2);
		display.setTextColor(SSD1306_WHITE);
		display.setCursor(20, 12);
		display.print("SALDO NON");
		display.setCursor(10, 35);
		display.print("SUFF.");
		display.display();
		break;
	}
	case NOCARD:
	{
		display.stopscroll();
		display.clearDisplay();
		delay(10);
		display.setTextSize(2);
		display.setTextColor(SSD1306_WHITE);
		display.setCursor(17, 15);
		display.print("CARD NON");
		display.setCursor(10, 35);
		display.print("ESISTENTE");
		display.display();
		break;
	}
	case NOPROD:
	{
		display.stopscroll();
		display.clearDisplay();
		delay(10);
		display.setTextSize(2);
		display.setTextColor(SSD1306_WHITE);
		display.setCursor(20, 15);
		display.print("PROD NON");
		display.setCursor(10, 35);
		display.print("ESISTENTE");
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
		display.print("  VIVERE\nKAFFETTINO");
		display.display();
		display.startscrollleft(0x00, 0x0F); // riattiva lo spostamento del testo con le coordinate di inizio e fine
		break;
	}
	case STAMPAPROD:
	{
		Prodotto *p = listaProdotti.get(currentProdotto);
		display.stopscroll();
		display.clearDisplay();
		delay(10);
		display.setTextSize(2);
		display.setTextColor(SSD1306_WHITE);
		display.setCursor(35, 15);
		display.print(p->nome);
		display.setCursor(45, 35);
		display.print(p->prezzo);
		display.display();
		break;
	}
	case CONNECTING:
	{
		display.stopscroll();
		display.clearDisplay();
		display.setTextSize(2); // Draw 2X-scale text
		display.setTextColor(SSD1306_WHITE);

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
	case AUGURI:
	{
		Serial.println("AUGURIIIIII!");

		display.stopscroll();
		display.clearDisplay();
		display.setTextSize(2); // Draw 2X-scale text
		display.setTextColor(SSD1306_WHITE);

		display.setCursor(25, 30);
		display.print("AUGURI!");
		display.display(); // Show text

		playCompleanno();

		break;
	}
	case HTTPERR:
	{
		display.stopscroll();
		display.clearDisplay();
		display.setTextSize(2); // Draw 2X-scale text
		display.setTextColor(SSD1306_WHITE);

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
