# library_app/routes/api.py
# Blueprint für API-Endpunkte, die Daten im JSON-Format für Frontend-Interaktionen bereitstellen.

from flask import Blueprint, request, jsonify
from flask_login import login_required 

from ..db import authors_collection

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/search_authors')
@login_required
def search_authors():
    query = request.args.get('q', '') 
   
    if not query:
        return jsonify([])
        
    # Das '^'-Zeichen sorgt dafür, dass nur der Anfang des Namens zählt.
    regex_query = f"^{query}"

    authors = authors_collection.find(
        {'name': {'$regex': regex_query, '$options': 'i'}},
        {'name': 1, '_id': 0} # Nur das 'name'-Feld zurückgeben
    ).limit(10)
    
    author_names = [author['name'] for author in authors]
    
    return jsonify(author_names)