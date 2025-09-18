# run.py
# Startpunkt der Anwendung. Erstellt die Flask-App und startet den Entwicklungs-Server.
# Im Terminal mit python run.py starten. 

from library_app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)