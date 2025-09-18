# Bibliotheksverwaltung (Python, Flask, MongoDB, HTML, Java, CSS)
Einsendeaufgabencode: Ersatzleistung berufspraktische Phase im Fachbereich Informatik

## Aufgabe
Es soll eine Datenbankanwendung für ein Bibliotheksverwaltungssystem auf Basis von MongoDB entwickelt werden.

Die Anwendung muss folgende Funktionalitäten implementieren:
1. Anlegen einer Datenbank zur Verwaltung von Büchern, Autoren, und Nutzern der Bibliothek

2. Hinzufügen, Bearbeiten und Löschen von Büchern, Autoren und Nutzern

3. Implementierung von Suchfunktionen:
    -	Suche nach Büchern anhand von Titel, Autor oder ISBN
    -	Suche nach ausgeliehenen Büchern pro Nutzer
    -	Verleih- und Rückgabefunktionalität
    -	Verwaltung von Ausleihfristen und Erinnerungsfunktionen für überfällige Bücher
    -	Generierung von Berichten über die meist ausgeliehenen Bücher, häufigste Nutzer etc.
    -	Export der Daten in CSV-Format
    -	Benutzeroberfläche mit grafischer Navigation für die Interaktion mit der Datenbank
    -	Zeitstempel für Buchausleihen und -rückgaben
    -	Authentifizierung und Rollenverwaltung (Admin, Bibliothekar, Nutzer)


## Anleitung
1. Die Datenbankanwendung erfordert die Installation von:
   - Python 3
   - MongoDB Community Server

2. Virtuelle Umgebung erstellen und aktivieren

3. Bibliotheken aus requirements.txt mit Hilfe von pip install -r requirements.txt installieren

4. Sicherstellen, dass der MongoDB-Server läuft

5. Im Terminal, wo die virtuelle Umgebung aktiv ist, mit Hilfe des Befehls python run.py die Datenbankanwendung starten

6. Entweder den angezeigten Link im Terminal anklicken oder direkt im Browser die Adresse http://127.0.0.1:5000 eingeben. 
