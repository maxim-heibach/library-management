# library_app/routes/authors.py
# Blueprint für alle Routen, die die Verwaltung von Autoren betreffen (CRUD und Suche).

from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId

from ..db import authors_collection, books_collection
from ..decorators import librarian_required

authors_bp = Blueprint('authors', __name__, template_folder='templates')

@authors_bp.route('/authors')
@librarian_required
def list_authors():
    search_query = request.args.get('search', None)
    query = {}
    
    if search_query:
        query = {
            '$or': [
                {'name': {'$regex': search_query, '$options': 'i'}},
                {'biography': {'$regex': search_query, '$options': 'i'}}
            ]
        }
   
    all_authors = list(authors_collection.find(query).sort('name', 1))
    
    return render_template('authors.html', authors=all_authors)

@authors_bp.route('/author/add', methods=['GET', 'POST'])
@librarian_required
def add_author():
    if request.method == 'POST':
        name = request.form.get('name')
        biography = request.form.get('biography')
        if authors_collection.find_one({'name': name}):
            flash('Ein Autor mit diesem Namen existiert bereits.', 'warning')
        else:
            authors_collection.insert_one({'name': name, 'biography': biography})
            flash('Autor erfolgreich hinzugefügt.', 'success')
        
        return redirect(url_for('authors.list_authors'))
    
    return render_template('author_form.html', action='hinzufügen', author={})

@authors_bp.route('/author/edit/<author_id>', methods=['GET', 'POST'])
@librarian_required
def edit_author(author_id):
    author = authors_collection.find_one({'_id': ObjectId(author_id)})
    
    if request.method == 'POST':
        name = request.form.get('name')
        biography = request.form.get('biography')
        authors_collection.update_one({'_id': ObjectId(author_id)}, {'$set': {'name': name, 'biography': biography}})
        books_collection.update_many({'author_id': ObjectId(author_id)}, {'$set': {'author_name': name}})
        
        flash('Autor erfolgreich aktualisiert.', 'success')
        
        return redirect(url_for('authors.list_authors'))
    
    return render_template('author_form.html', action='bearbeiten', author=author)

@authors_bp.route('/author/delete/<author_id>')
@librarian_required
def delete_author(author_id):
    author_object_id = ObjectId(author_id)
    books_collection.delete_many({'author_id': author_object_id})
    authors_collection.delete_one({'_id': author_object_id})
    
    flash('Autor und alle zugehörigen Bücher wurden gelöscht.', 'success')
    
    return redirect(url_for('authors.list_authors'))