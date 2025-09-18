# library_app/routes/users.py
# Blueprint für Routen zur Benutzerverwaltung und für Interaktionen wie Ausleihe und Rückgabe.

import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from bson.objectid import ObjectId

from ..db import users_collection, loans_collection, books_collection
from ..decorators import admin_required, librarian_required

users_bp = Blueprint('users', __name__, template_folder='templates')

@users_bp.route('/users')
@librarian_required
def list_users():
    search_query = request.args.get('search', None)
    query = {}
    if search_query:
        query = {
            '$or': [
                {'username': {'$regex': search_query, '$options': 'i'}},
                {'role': {'$regex': search_query, '$options': 'i'}}
            ]
        }
    all_users = list(users_collection.find(query).sort('username', 1))
   
    return render_template('users.html', users=all_users)

@users_bp.route('/user/edit/<user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user_to_edit = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user_to_edit:
        flash('Benutzer nicht gefunden.', 'danger')
        return redirect(url_for('users.list_users'))

    if request.method == 'POST':
        new_role = request.form.get('role')

        # Prüfen, ob der zu bearbeitende Benutzer der letzte Admin ist und seine Rolle geändert werden soll. 
        # Falls er der letzte ist, wird dies verhindert
        if user_to_edit['role'] == 'admin' and new_role != 'admin':
            admin_count = users_collection.count_documents({'role': 'admin'})
            if admin_count <= 1:
                flash('Aktion blockiert: Der letzte Administrator kann nicht zu einer anderen Rolle herabgestuft werden.', 'danger')
                return redirect(url_for('users.list_users'))

        if new_role in ['user', 'librarian', 'admin']:
            users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': {'role': new_role}})
            flash(f"Rolle für {user_to_edit['username']} wurde zu '{new_role}' geändert.", 'success')
            return redirect(url_for('users.list_users'))
        else:
            flash('Ungültige Rolle ausgewählt.', 'danger')
            
    return render_template('user_edit_form.html', user=user_to_edit)

@users_bp.route('/user/delete/<user_id>')
@admin_required
def delete_user(user_id):
    user_to_delete = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user_to_delete:
        flash('Benutzer nicht gefunden.', 'danger')
        return redirect(url_for('users.list_users'))
    
    # Verhindert das Löschen des letzten Admins
    if user_to_delete['role'] == 'admin':
        admin_count = users_collection.count_documents({'role': 'admin'})
        if admin_count <= 1:
            flash('Aktion blockiert: Der letzte Administrator kann nicht gelöscht werden.', 'danger')
            return redirect(url_for('users.list_users'))

    users_collection.delete_one({'_id': ObjectId(user_id)})
    
    flash('Benutzer erfolgreich gelöscht.', 'success')
   
    return redirect(url_for('users.list_users'))

@users_bp.route('/profile')
@login_required
def user_profile():
    user_loans = list(loans_collection.find({'user_id': ObjectId(current_user.id), 'return_date': None}))
   
    for loan in user_loans:
        book = books_collection.find_one({'_id': loan['book_id']})
        loan['book_title'] = book['title'] if book else 'Unbekanntes Buch'
    
    return render_template('user_profile.html', loans=user_loans)

@users_bp.route('/user/<user_id>/loans')
@librarian_required
def view_user_loans(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})
   
    if not user:
        flash('Benutzer nicht gefunden', 'danger')
        return redirect(url_for('users.list_users'))
   
    user_loans = list(loans_collection.find({'user_id': ObjectId(user_id)}).sort('loan_date', -1))
   
    for loan in user_loans:
        book = books_collection.find_one({'_id': loan['book_id']})
        loan['book_title'] = book['title'] if book else 'Unbekanntes Buch'
   
    return render_template('user_loans.html', loans=user_loans, user=user)

@users_bp.route('/borrow/<book_id>')
@login_required
def borrow_book(book_id):
    book = books_collection.find_one({'_id': ObjectId(book_id)})

    if book and book.get('available_copies', 0) > 0:
        books_collection.update_one(
            {'_id': ObjectId(book_id)},
            {'$inc': {'available_copies': -1}}
        )

        loan_date = datetime.datetime.now(datetime.timezone.utc)
        due_date = loan_date + datetime.timedelta(days=21)
        loans_collection.insert_one({
            'book_id': ObjectId(book_id), 'user_id': ObjectId(current_user.id),
            'loan_date': loan_date, 'due_date': due_date, 'return_date': None
        })
        flash(f"Sie haben ein Exemplar von '{book['title']}' erfolgreich ausgeliehen.", 'success')
    else:
        flash('Dieses Buch ist leider nicht verfügbar oder alle Exemplare sind ausgeliehen.', 'danger')
        
    return redirect(url_for('books.list_books'))

@users_bp.route('/return/<loan_id>')
@login_required
def return_book(loan_id):
    loan = loans_collection.find_one({'_id': ObjectId(loan_id), 'return_date': None})

    if loan:
        loans_collection.update_one(
            {'_id': ObjectId(loan_id)}, 
            {'$set': {'return_date': datetime.datetime.now(datetime.timezone.utc)}}
        )

        books_collection.update_one(
            {'_id': loan['book_id']},
            {'$inc': {'available_copies': 1}}
        )
        
        flash('Buch erfolgreich zurückgegeben.', 'success')
    else:
        flash('Ausleihvorgang nicht gefunden oder bereits abgeschlossen.', 'danger')
        
    if 'source' in request.args and request.args.get('source') == 'user_loans':
        return redirect(url_for('users.view_user_loans', user_id=str(loan['user_id'])))
        
    return redirect(url_for('users.user_profile'))