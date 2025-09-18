# library_app/routes/books.py
# Blueprint für alle Routen, die die Verwaltung von Büchern betreffen (CRUD und Suche).

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from bson.objectid import ObjectId

from ..db import books_collection, authors_collection, loans_collection 
from ..decorators import librarian_required


books_bp = Blueprint('books', __name__, template_folder='templates')

@books_bp.route('/books')
@login_required
def list_books():
    search_query = request.args.get('search')
    query = {}
   
    if search_query:
        query = {
            '$or': [
                {'title': {'$regex': search_query, '$options': 'i'}},
                {'author_name': {'$regex': search_query, '$options': 'i'}},
                {'isbn': {'$regex': search_query, '$options': 'i'}}
            ]
        }
    all_books = list(books_collection.find(query).sort('title', 1))
    
    return render_template('books.html', books=all_books)

@books_bp.route('/book/add', methods=['GET', 'POST'])
@librarian_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        author_name = request.form.get('author_name')
        total_copies = int(request.form.get('total_copies', 1))

        author = authors_collection.find_one_and_update(
            {'name': author_name}, {'$setOnInsert': {'name': author_name, 'biography': ''}},
            upsert=True, return_document=True
        )
        
        books_collection.insert_one({
            'title': title, 
            'isbn': isbn, 
            'author_id': author['_id'], 
            'author_name': author['name'], 
            'total_copies': total_copies, 
            'available_copies': total_copies 
        })
        
        flash('Buch erfolgreich hinzugefügt.', 'success')
        
        return redirect(url_for('books.list_books'))
    
    return render_template('book_form.html', action='hinzufügen', book={})

@books_bp.route('/book/edit/<book_id>', methods=['GET', 'POST'])
@librarian_required
def edit_book(book_id):
    book = books_collection.find_one({'_id': ObjectId(book_id)})
    if request.method == 'POST':
        borrowed_count = loans_collection.count_documents({
            'book_id': ObjectId(book_id),
            'return_date': None
        })
        
        new_total_copies = int(request.form.get('total_copies'))

        if new_total_copies < borrowed_count:
            flash(f'Fehler: Es sind bereits {borrowed_count} Exemplare ausgeliehen. Die Gesamtanzahl kann nicht kleiner sein.', 'danger')
            return redirect(url_for('books.edit_book', book_id=book_id))

        new_available_copies = new_total_copies - borrowed_count

        books_collection.update_one({'_id': ObjectId(book_id)}, {'$set': {
            'title': request.form.get('title'),
            'isbn': request.form.get('isbn'),
            'author_name': request.form.get('author_name'),
            'total_copies': new_total_copies,
            'available_copies': new_available_copies
        }})
        
        flash('Buch erfolgreich aktualisiert.', 'success')
        
        return redirect(url_for('books.list_books'))
    
    return render_template('book_form.html', action='bearbeiten', book=book)

@books_bp.route('/book/delete/<book_id>')
@librarian_required
def delete_book(book_id):
    books_collection.delete_one({'_id': ObjectId(book_id)})
    
    flash('Buch erfolgreich gelöscht.', 'success')
    
    return redirect(url_for('books.list_books'))