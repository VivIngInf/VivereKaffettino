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

// Lib lettore NFC
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
#include <U8g2lib.h> // Font per schermo UTF8

U8G2_SSD1306_128X64_NONAME_F_HW_I2C display(U8G2_R0, /*reset=*/ U8X8_PIN_NONE);

// Lib audio
#include <Arduino.h>
#include "DFRobotDFPlayerMini.h" // DFRobotDFPlayerMini by DFRobot

// Credenziali wifi
#define WIFI_SSID SECRET_SSID                   // Nome del WiFi
#define WIFI_IDENTITY SECRET_USERNAME           // Username in caso di EAP
#define WIFI_PASSWORD SECRET_PASSWORD           // Password del WIFI
#define WIFI_USERNAME SECRET_USERNAME           // Altro username in caso di EAP

// Secrets

#define IS_EAP SECRET_IS_EAP                    // Se siamo collegati ad una rete EAP
#define PAY_ROUTE SECRET_PAY
#define PRODUCTS_ROUTE SECRET_PRODUCTS
#define ID_AULETTA SECRET_ID_AULETTA // Gestione prodotti
#define TOKEN_HEADER_NAME SECRET_HEADER_NAME
#define TOKEN_HEADER_VALUE SECRET_HEADER_VALUE

// Rotte
const char *serverAddressPay = PAY_ROUTE;
const char *serverAddressProdotti = PRODUCTS_ROUTE;
WiFiClient wifiClient;

// Definiamo la classe prodotto per come viene ritornata dal server in JSON
class Prodotto
{
public:
	String id;
	String nome;
	String prezzo;
};

LinkedList<Prodotto *> listaProdotti = LinkedList<Prodotto *>(); // Array dei prodotti disponibili
int currentProdotto = -1;

JsonArray products; // Array di elementi json che conterrà i prodotti

// Codici di stampa per la funzione stampaOled()

#define VISUALIZZA_ERRORE_HW -6		// C'è stato un errore hardware, è importante!
#define CONNESSIONE_IN_CORSO -5		// Stiamo provando a connetterci
#define CONNESSIONE_NON_RIUSCITA -4	// Non siamo riusciti a connetterci al server
#define CONNESSIONE_RIUSCITA -3		// Siamo riusciti a connetterci al server
#define RICHIESTA_IN_CORSO -2		// Stiamo contattando il server
#define VISUALIZZA_ERRORE -1 		// C'è stato un errore nella richiesta http

#define VISUALIZZA_PAGATO 0	  		// Il pagamento è andato a buon fine
#define VISUALIZZA_NOSALDO 1		// Non hai abbastanza saldo nella carta per quel determinato prodotto
#define VISUALIZZA_NOCARD 2	  		// Non esiste la carta nel database
#define VISUALIZZA_NOPROD 3	  		// Non esiste il prodotto nel database (cosa che non dovrebbe comunque succedere)
#define VISUALIZZA_NOSELECTION 4	// Non è stato selezionato alcun prodotto
#define VISUALIZZA_STAMPAPROD 7  	// Stampa il prodotto con id == currentProdotto
#define VISUALIZZA_VIVERE 10		// Codice di stampa vivere kaffettino

#define AUGURI 69	  				// Il bro che ha acquistato ha compiuto gli anni
#define UNVERIFIED 70 				// Il bro non ha la card abilitata

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
bool canReadCards = true;
#define attesa 3000
bool firstBoot = true;
bool firstBootError = true; 

long long int t3;  // variabile temporale per la pressione prolungata
int durata = 5000; // costante in ms per la pressione 5sec kaffettino, 10sec bella ciao, 15sec faccetta
int buttonBeenPressed = 0;   // variabile che controlla se il pulsante è premuto ed è già stato azzerato t3
int butt = 15;	   // pin del pulsante

int timerResetProd = 0;		// timer reset selezione prodotto
int durataResetProd = 5000; // durata della selezione prodotto
bool startedTimer = false;

// Funzione utilizzata quando è necessario brickare l'arduino perché
// determinate interfacce non si sono inizializzate correttamente
void errorBricker(String s)
{
	if(Serial)
		Serial.println(s);

	tone(buzzer, 500, 5000); // Il suono della morte

	while (true) // non procedere, cicla all'infinito
	{
		delay(1000);
		digitalWrite(red, HIGH);
		delay(1000);
		digitalWrite(red, LOW);
	}
}

// Funzione per inizializzare i seriali di comunicazione
void initSerial(){
	Serial.begin(115200);	// Initialize serial communications with the PC
	mySoftwareSerial.begin(9600, SERIAL_8N1, 32, 33); // speed, type, RX, TX

	// Se le connessioni seriali non sono state inizializzate correttamente,
	// stoppiamo l'esecuzione e tiriamo un errore
	if (!Serial || !mySoftwareSerial) 
		errorBricker("Allocazione seriale fallita!");	   
}

// Inizializziamo il lettore card NFC
void initNFC(){
	SPI.begin();					   // Init SPI bus
	mfrc522.PCD_Init();				   // Init MFRC522
	mfrc522.PCD_DumpVersionToSerial(); // Show details of PCD - MFRC522 Card Reader details
	Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));

	// Se le connessioni seriali non sono state inizializzate correttamente,
	// stoppiamo l'esecuzione e tiriamo un errore
	byte v = mfrc522.PCD_ReadRegister(MFRC522::VersionReg);
	if (v == 0x00 || v == 0xFF) {
		errorBricker(F("MFRC522 non rilevato (controlla cablaggio/SPI/RST)."));
	}
}

// Inizializziamo il seriale dello schermo
void initSchermo(){
  	display.begin();
  	display.enableUTF8Print();                       // abilita UTF-8 per print()
  	display.setFont(u8g2_font_logisoso20_tf);    // font che include "€" (e tanti simboli)
	display.clearBuffer();   
}

// Inizializziamo tutti i pin in input ed output
void initPins(){
	pinMode(butt, INPUT_PULLUP);
	pinMode(GND, OUTPUT);
	digitalWrite(GND, LOW);

	pinMode(buzzer, OUTPUT);
	pinMode(4, OUTPUT); // pin 4 usato temporaneamente come ground
	pinMode(yellow, OUTPUT);
	pinMode(green, OUTPUT);
	pinMode(red, OUTPUT);
	digitalWrite(buzzer, LOW);
	digitalWrite(4, LOW); // pin 14 usato temporaneamente come ground

	pinMode(butt, INPUT_PULLUP);
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
	}

	Serial.println(F("DFPlayer Mini online."));
	//myDFPlayer.setTimeOut(500); // Set serial communictaion time out 500ms

	//----Set volume----
	//myDFPlayer.volume(25);	 // Set volume value (0~30).
	//myDFPlayer.volumeUp();	 // Volume Up
	//myDFPlayer.volumeDown(); // Volume Down
	//myDFPlayer.outputDevice(DFPLAYER_DEVICE_SD);
}

void handleWifi()
{

	connettiWifi(); // Ci connettiamo al wifi

	if(WiFi.status() != WL_CONNECTED)
	{
		Serial.println("Connessione WiFi mancante, riprovo a connettermi...");
		stampaoled(CONNESSIONE_NON_RIUSCITA);
		
		digitalWrite(green, LOW);
		digitalWrite(yellow, LOW);
		digitalWrite(red, HIGH);

		if(firstBootError)
		{
			tone(buzzer, 500, 2000); // Il suono della morte lo riproduciamo solo la prima volta per farlo attenzionare!
			firstBootError = false;
		}
	}

	delay(3000);

	digitalWrite(green, LOW);
	digitalWrite(yellow, LOW);
	digitalWrite(red, LOW);
	
	return;

	t = millis();
	canReadCards = 0;

	return;

}

void connettiWifi()
{
	canReadCards = 0; // Se la lettura delle cards è abilitata, la disabilitamo

	if (IS_EAP) // Per WiFi Unipa
		WiFi.begin(WIFI_SSID, WPA2_AUTH_PEAP, WIFI_USERNAME, WIFI_USERNAME, WIFI_PASSWORD); // Passiamo le credenziali e istanziamo una nuova connessione
	else		// Per altri wifi senza credenziali singole
		WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

	digitalWrite(green, LOW);
	digitalWrite(red, LOW);
	digitalWrite(yellow, HIGH);

    stampaoled(CONNESSIONE_IN_CORSO); // Mostriamo lo stato di connessione
    Serial.println("Connessione WiFi in corso...");

	delay(1000);

	if (WiFi.status() != WL_CONNECTED) // Se non siamo ancora connessi
	{
		delay(5000); // Aspettiamo altri 5 secondi per collegarci

        // Se ancora non ci siamo collegati torniamo indietro
        if(WiFi.status() != WL_CONNECTED)
            return;
	}

	digitalWrite(green, HIGH);
	digitalWrite(red, LOW);
	digitalWrite(yellow, LOW);

	canReadCards = 1; // Riabilitiamo le carte se ci siamo collegati
	stampaoled(CONNESSIONE_RIUSCITA); // Stampiamo che ci siamo connessi

    tone(buzzer, 500, 250);     // Tono gioviale
    tone(buzzer, 1500, 500);    // E molto felice

    delay(500);

	digitalWrite(green, LOW);
	digitalWrite(red, LOW);
	digitalWrite(yellow, HIGH);

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

void changeProduct()
{
	currentProdotto++;

	if (currentProdotto >= listaProdotti.size())
		currentProdotto = 0;

	stampaoled(VISUALIZZA_STAMPAPROD); // 7 per avere un offset rispetto alle stampe di pagato ed errori 6 in tot
}

void getProdotti() // Funzione che effettua una chiamata al server e riceve i prodotti vendibili nell'auletta di riferimento
{

	digitalWrite(green, LOW);
	digitalWrite(red, LOW);
	digitalWrite(yellow, HIGH);

	stampaoled(RICHIESTA_IN_CORSO);

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
	http.addHeader(TOKEN_HEADER_NAME, TOKEN_HEADER_VALUE);
	int httpResponseCode = http.POST(jsonString); // Passiamo come body il json

	Serial.print("HTTP Response code: ");
	Serial.println(httpResponseCode); // Stampiamo il codice di risposta
	String response;

	// Se il codice di risposta è maggiore di 0 vuol dire che è stato un successo e possiamo mostrare la response
	if (httpResponseCode > 0 && httpResponseCode < 400)
	{
		response = http.getString();
		Serial.print("Response Body: ");
		Serial.println(response);
		verify = 0; // resettiamo verify
	}
	else
	{
		Serial.println("Errore nella richiesta HTTP");
		stampaoled(VISUALIZZA_ERRORE);
		verify = VISUALIZZA_ERRORE;
		
		digitalWrite(green, LOW);
		digitalWrite(red, HIGH);
		digitalWrite(yellow, LOW);

		if(firstBootError)
		{
			tone(buzzer, 500, 2000); // Il suono della morte lo riproduciamo solo la prima volta per farlo attenzionare!
			firstBootError = false;
		}

		delay(5000);
	}

	// Free resources
	http.end();

	delay(2000);

	if (verify == VISUALIZZA_ERRORE)
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
		// Il prodotto è visibile all'auletta?
		bool isVisible = product["isVisible"].as<bool>();

		// Se no allora skippiamo, non vogliamo aggiungerlo nella lista.
		if (!isVisible)
			continue;

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
	http.addHeader(TOKEN_HEADER_NAME, TOKEN_HEADER_VALUE);

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
		verify = VISUALIZZA_ERRORE;
	}

	// Free resources
	http.end();
}

void stampaoled(int i)
{
	switch (i)
	{

	case VISUALIZZA_PAGATO:
	{
		display.clearBuffer(); // elimina la scritta
		delay(10);
		display.setCursor(25, 30);			 // inizio del testo, pixel in alto a sinista, serve per centrare
		display.print("PAGATO");
		display.sendBuffer(); // Attiva il testo
		break;
	}
	case VISUALIZZA_NOSALDO:
	{
		// Segnale acustico
		digitalWrite(buzzer, 1);
		delay(300);
		digitalWrite(buzzer, 0);

		display.clearBuffer();
		delay(10);
		display.setCursor(20, 12);
		display.print("SALDO NON");
		display.setCursor(10, 35);
		display.print("SUFF.");
		display.sendBuffer();
		break;
	}
	case VISUALIZZA_NOCARD:
	{
		// Segnale acustico
		digitalWrite(buzzer, 1);
		delay(300);
		digitalWrite(buzzer, 0);

		display.clearBuffer();
		delay(10);

		display.setCursor(17, 15);
		display.print("CARD NON");
		display.setCursor(10, 35);
		display.print("ESISTENTE");
		display.sendBuffer();
		break;
	}
	case VISUALIZZA_NOPROD:
	{
		// Segnale acustico
		digitalWrite(buzzer, 1);
		delay(300);
		digitalWrite(buzzer, 0);

		display.clearBuffer();
		delay(10);

		display.setCursor(20, 15);
		display.print("PROD NON");
		display.setCursor(10, 35);
		display.print("ESISTENTE");
		display.sendBuffer();
		break;
	}
	case VISUALIZZA_NOSELECTION:
	{
		// Segnale acustico
		digitalWrite(buzzer, 1);
		delay(300);
		digitalWrite(buzzer, 0);

		display.clearBuffer();
		delay(10);

		display.setCursor(10, 30);
		display.print("SCEGLI IL");
		display.setCursor(12, 55);
		display.print("PRODOTTO!");
		display.sendBuffer();
		break;
	}
	case VISUALIZZA_VIVERE:
	{
		display.clearBuffer();
		delay(10);
		
		display.setCursor(25, 30);
		display.print("VIVERE");
		display.setCursor(1, 60);
		display.print("KAFFETTINO");
		display.sendBuffer();

		break;
	}
	case VISUALIZZA_STAMPAPROD:
	{
		Prodotto *p = listaProdotti.get(currentProdotto);
		display.clearBuffer();
		delay(10);
		display.setCursor(30, 30);
		display.print(p->nome);
		display.setCursor(40, 60);
		display.print(p->prezzo.toFloat());
		display.sendBuffer();
		break;
	}
	case CONNESSIONE_IN_CORSO:
	{
		display.clearBuffer();

		display.setCursor(0, 30);
		display.print("CONNECTING");
		display.sendBuffer(); // Show text

		delay(300);
		display.setCursor(35, 55);
		display.setFont(u8g2_font_unifont_h_symbols);
		display.print("○ ");
		delay(300);
		display.sendBuffer(); // Show text

		display.print(" ○ ");
		delay(300);
		display.sendBuffer(); // Show text

		display.print(" ○");
		delay(300);
		display.sendBuffer(); // Show initial text

		display.setFont(u8g2_font_logisoso20_tf);

		break;
	}
	case CONNESSIONE_NON_RIUSCITA:
    {
        display.clearBuffer(); // elimina la scritta
        delay(10);
        display.setCursor(0, 30);
        display.print("CONNECTION");
        display.setCursor(30, 55);
        display.print("FAILED");
        display.sendBuffer(); // Attiva il testo
        break;
    }
    case CONNESSIONE_RIUSCITA:
    {
        display.clearBuffer(); // elimina la scritta
        delay(10);
        display.setCursor(13, 40);
        display.print("CONNESSO");
        display.sendBuffer(); // Attiva il testo
        break;
    }
    case RICHIESTA_IN_CORSO:
    {
        display.clearBuffer(); // elimina la scritta
        delay(10);
        display.setCursor(10, 20);
        display.print("SCARICO I");
        display.setCursor(15, 45);
        display.print("PRODOTTI");
        
		delay(300);
        display.setCursor(35, 60);
		display.setFont(u8g2_font_unifont_h_symbols);
		display.print("○ ");
		delay(300);
		display.sendBuffer(); // Show text

		display.print(" ○ ");
		delay(300);
		display.sendBuffer(); // Show text

		display.print(" ○");
		delay(300);
		display.sendBuffer(); // Show initial text

		display.setFont(u8g2_font_logisoso20_tf);
        display.sendBuffer(); // Attiva il testo
        break;
    }
	case AUGURI:
	{
		Serial.println("AUGURIIIIII!");

		display.clearBuffer();

		display.setCursor(25, 30);
		display.print("AUGURI!");
		display.sendBuffer(); // Show text

		playCompleanno();

		break;
	}
	case UNVERIFIED:
	{
		Serial.println("Card disabilitata");

		display.clearBuffer();

		display.setCursor(52, 5);
		display.print("CARD");
		display.sendBuffer();		// Show text

		display.setCursor(30, 25);
		display.print("DISABILITATA");
		display.setCursor(40, 45);
		display.print("PEZZENTE");
		digitalWrite(red, HIGH);
		delay(200);
		display.sendBuffer(); // Show text

		for (size_t i = 0; i < 10; i++)
		{
			// Segnale acustico
			digitalWrite(buzzer, 1);
			delay(500);
			digitalWrite(buzzer, 0);
			delay(500);
		}

		break;
	}
	case VISUALIZZA_ERRORE:
	{
		display.clearBuffer();

        display.setCursor(25, 30);
        display.print("SERVER");
        display.setCursor(32, 55);
        display.print("ERROR");
		display.sendBuffer(); // Show text

		delay(200);
		display.sendBuffer(); // Show text

		break;
	}
	}
}

void playCompleanno()
{
	//myDFPlayer.play(2); // Play compleanno mp3
	Serial.println("Play compleanno");
}

void setup()
{
	initPins();
	initSerial();

	delay(1000);
	Serial.println("Setup");

	initNFC();
	initSchermo();
	
	t3 = millis();

	setupAudio(); // Setup modulo sd audio

    tone(buzzer, 500, 250);     // Tono gioviale
}

void loop()
{
	// Se non siamo ancora collegati, o la connessione è esplosa, proviamo a collegarci al wifi
	while (WiFi.status() != WL_CONNECTED)
		handleWifi();

	// Se abbiamo acceso ora kaffettino, facciamo la richiesta per i prodotti
	if(firstBoot){

		// Continuiamo a provare a prendere i prodotti fino a quando non avremo i prodotti in lista
		while(listaProdotti.size() <= 0)
			getProdotti();

		stampaoled(VISUALIZZA_VIVERE);
		//myDFPlayer.play(1);
		firstBoot = false;
		firstBootError = false;

		Serial.println("Setup done");
	}

	// Adesso possiamo iniziare a prendere gli ordini!
	// Diamo il via con i led verdi!

	digitalWrite(green, HIGH); // impostazione iniziale led
	digitalWrite(yellow, LOW);
	digitalWrite(red, LOW);
	t = millis();

	// Se non siamo riusciti a connetterci al server ma il wifi c'è vuol dire che c'è stato un problema al server
	while (verify == VISUALIZZA_ERRORE)
	{
		canReadCards = 0; // Disabilitiamo tutto

		if (!digitalRead(butt)) // Se il pulsante è premuto riproviamo
		{
			digitalWrite(buzzer, 1);
			delay(1000);
			digitalWrite(buzzer, 0);
			delay(500);
			getProdotti(); // Chiediamo al server di mandarci i prodotti dell'auletta
		}

		if (verify == VISUALIZZA_ERRORE && alreadyPrint == 0)
		{
			digitalWrite(green, LOW);
			digitalWrite(yellow, LOW);
			digitalWrite(red, HIGH);

			stampaoled(VISUALIZZA_ERRORE);
			alreadyPrint = 1;

			Serial.println("ERRORE HTTP!!!");
		}
		else if (verify != VISUALIZZA_ERRORE)
		{
			Serial.println("ABEMUS PRODOTTI!!!");
			canReadCards = 1;

			if (verify != 69)
				stampaoled(VISUALIZZA_VIVERE);
			else
				stampaoled(AUGURI);

			delay(2000);
			break;
		}
	}

	// Quando premiamo il tasto per ciclare i prodotti e rilasciamo subito
	if (!digitalRead(butt) && buttonBeenPressed == 0)
	{
		buttonBeenPressed = 1;   // metto ad 1 per non far rientrare in questo if durante la pressione
		t3 = millis(); //"azzero" t3 rispetto  millis per avere un punto temporale di partenza
		Serial.println("Premuto");
		changeProduct(); // alla pressione richiamo la funziona per il cambio prodotto
	}

	// Se non è stato utilizzato il bottone o non è stato pagato
	// entro durataResetProd secondi allora resetta allo stato iniziale
	if (millis() >= timerResetProd + durataResetProd && currentProdotto != -1 && startedTimer == true)
	{
		Serial.println("Reset selezione prodotto");
		stampaoled(VISUALIZZA_VIVERE);
		currentProdotto = -1; // se parte la musica resettiamo il counter prodotto
		startedTimer = false;
	}

	// Se manteniamo premuto il pulsante e poi lo rilasciamo
	if (digitalRead(butt) && buttonBeenPressed == 1)
	{
		buttonBeenPressed = 0;													// Riazzero per riabilitare la lettura della pressione
		if (millis() > (t3 + durata) && millis() < (t3 + (2 * durata))) // Se sono passati 5 secondi
		{
			//myDFPlayer.play(1); // Play the first mp3
			Serial.println("Play caffettino");
			stampaoled(VISUALIZZA_VIVERE);
			currentProdotto = -1; // se parte la musica resettiamo il counter prodotto
		}
		else if (millis() > (t3 + (2 * durata)) /*&& millis() < (t3 + (3 * durata))*/) // Se sono passati 10 secondi
		{
			playCompleanno();
			stampaoled(VISUALIZZA_VIVERE);
			currentProdotto = -1; // se parte la musica resettiamo il counter prodotto
		}
		/*else if(millis() > (t3 + (3 * durata)) )  //Se sono passati 15 secondi
		{
		  myDFPlayer.play(2);  //Play the first mp3
		  Serial.println("Musica particolare");
		  stampaoled(VIV);
		  currentProdotto = 0; //se parte la musica resettiamo il counter prodotto
		}*/
		else
		{
			timerResetProd = millis();
			startedTimer = true;
		}
		Serial.println("Rilasciato");
	}

	if (millis() == (t + attesa)) // Vero solo se dall'ultimo tag è passato più di "attesa"
	{
		canReadCards = true;
		stampaoled(VISUALIZZA_VIVERE);
	}

	if (canReadCards == true) // Se possiamo leggere la carta, la leggiamo
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

		// Se non è stato selezionato nessun prodotto
		if (currentProdotto == -1)
		{
			digitalWrite(green, LOW);
			digitalWrite(red, HIGH);

			stampaoled(VISUALIZZA_NOSELECTION);

			digitalWrite(buzzer, 1);
			delay(100);
			digitalWrite(buzzer, 0);

			delay(100);
			digitalWrite(buzzer, 1);
			delay(100);
			digitalWrite(buzzer, 0);

			delay(100);
			digitalWrite(buzzer, 1);
			delay(100);
			digitalWrite(buzzer, 0);

			delay(100);
			digitalWrite(buzzer, 1);
			delay(100);
			digitalWrite(buzzer, 0);

			delay(1000);

			stampaoled(VISUALIZZA_VIVERE);

			digitalWrite(green, HIGH);
			digitalWrite(red, LOW);

			return;
		}

		verify = 0; // reset variabile di controllo, il valore deve essere il ritorno del server

		logCard(); // Siccome è stata riconosciuta una card, logghiamo le sue caratteristiche.

		pay();

		currentProdotto = -1; // Resettiamo il prodottoCorrente resettiamo il counter prodotto.
		canReadCards = false;		  // Reset flag per impedire la lettura di carte durante l'invio al server/lampeggio/beep
		t = millis();		  // Reset t perché è stata letta una carta

		if (verify != 0) // Se il codice di ritorno non è 0 questo vuol dire che c'è stato un errore.
		{
			stampaoled(verify); // Mandiamo a schermo l'errore

			digitalWrite(green, LOW);
			digitalWrite(yellow, LOW);
			digitalWrite(red, HIGH); // Led rosso simboleggia errore

			t = millis();

			return;
		}

		// Se è stato pagato

		stampaoled(VISUALIZZA_PAGATO);
		digitalWrite(green, HIGH);
		digitalWrite(yellow, LOW);
		digitalWrite(red, LOW);

		digitalWrite(buzzer, 1);
		delay(500);
		digitalWrite(buzzer, 0);
		delay(100);
		digitalWrite(buzzer, 1);
		delay(1000);
		digitalWrite(buzzer, 0);

		stampaoled(VISUALIZZA_VIVERE);
		digitalWrite(green, LOW);
		digitalWrite(yellow, HIGH);
		digitalWrite(red, LOW);

		canReadCards = true;

	}
}