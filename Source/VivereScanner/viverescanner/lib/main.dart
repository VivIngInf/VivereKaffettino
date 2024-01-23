import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_nfc_kit/flutter_nfc_kit.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Vivere Scanner',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
            seedColor: const Color.fromARGB(255, 7, 29, 153)),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: 'Vivere Scanner'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String _tagId = 'Nessun tag rilevato!';
  String desc = "Scannerizza la card!";

  @override
  void initState() {
    super.initState();
    _startNFCReader();
  }

  Future<void> _startNFCReader() async {
    try {
      var availability = await FlutterNfcKit.nfcAvailability;

      if (availability != NFCAvailability.available) {
        // oh-no
      }

      NFCTag tag = await FlutterNfcKit.poll(androidCheckNDEF: false);

      setState(() {
        _tagId = tag.id.toString();
        desc = "L'ID della card è:";
      });

      FlutterNfcKit.finish();
    } on PlatformException catch (_) {
      _startNFCReader();
    } on Exception catch (_) {
      setState(() {
        _tagId = "Errore, riprova!";
        desc = "Ops!";
      });
      _startNFCReader();
    }
  }

  void _resetTagId() {
    setState(() {
      _tagId = "Nessun tag rilevato!";
      desc = "Scannerizza la card!";
    });
    _startNFCReader();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
          backgroundColor: Theme.of(context).colorScheme.primary,
          title: const Row(
            children: [
              Image(
                image: AssetImage("resources/images/ingegneria.png"),
                width: 45,
              ),
              Padding(
                padding: EdgeInsets.only(left: 10),
                child: Text(
                  "Vivere",
                  style: TextStyle(
                      color: Colors.white,
                      fontFamily: 'Montserrat',
                      fontWeight: FontWeight.w300),
                ),
              ),
              Text(
                " Scanner",
                style: TextStyle(
                    color: Colors.white,
                    fontFamily: 'Montserrat',
                    fontWeight: FontWeight.bold),
              )
            ],
          )),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(
              desc,
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(0, 15, 0, 30),
              child: SelectableText(
                _tagId,
                style: Theme.of(context).textTheme.headlineMedium,
              ),
            ),
            ElevatedButton(
                onPressed: _resetTagId, child: const Text("Resetta scritta"))
          ],
        ),
      ),
    );
  }
}
