# library_app/routes/main.py
# Blueprint für allgemeine Routen wie die Startseite, Berichte und CSV-Exporte.

import csv
from io import StringIO
import datetime

from flask import Blueprint, render_template, make_response

from ..decorators import admin_required
from ..db import loans_collection, books_collection, users_collection, authors_collection

main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/reports')
@admin_required
def reports():
    now = datetime.datetime.now(datetime.timezone.utc)

    top_books_pipeline = [
        {'$group': {'_id': '$book_id', 'loan_count': {'$sum': 1}}},
        {'$sort': {'loan_count': -1}}, {'$limit': 5},
        {'$lookup': {'from': 'books', 'localField': '_id', 'foreignField': '_id', 'as': 'book_details'}},
        {'$unwind': '$book_details'},
        {'$project': {'title': '$book_details.title', 'author_name': '$book_details.author_name', 'loan_count': 1}}
    ]
    top_books = list(loans_collection.aggregate(top_books_pipeline))

    top_users_pipeline = [
        {'$group': {'_id': '$user_id', 'loan_count': {'$sum': 1}}},
        {'$sort': {'loan_count': -1}}, {'$limit': 5},
        {'$lookup': {'from': 'users', 'localField': '_id', 'foreignField': '_id', 'as': 'user_details'}},
        {'$unwind': '$user_details'},
        {'$project': {'username': '$user_details.username', 'loan_count': 1}}
    ]
    top_users = list(loans_collection.aggregate(top_users_pipeline))

    overdue_books_pipeline = [
        {'$match': {'return_date': None, 'due_date': {'$lt': now}}},
        {'$lookup': {'from': 'books', 'localField': 'book_id', 'foreignField': '_id', 'as': 'book_details'}},
        {'$lookup': {'from': 'users', 'localField': 'user_id', 'foreignField': '_id', 'as': 'user_details'}},
        {'$unwind': '$book_details'}, {'$unwind': '$user_details'},
        {'$project': {
            '_id': 0, 'username': '$user_details.username', 'book_title': '$book_details.title',
            'due_date': '$due_date',
            'days_overdue': {'$floor': {'$divide': [{'$subtract': [now, '$due_date']}, 1000 * 60 * 60 * 24]}}
        }},
        {'$sort': {'due_date': 1}}
    ]
    overdue_loans = list(loans_collection.aggregate(overdue_books_pipeline))

    return render_template('reports.html', 
                           top_books=top_books, 
                           top_users=top_users,
                           overdue_loans=overdue_loans)

@main_bp.route('/export/books/csv')
@admin_required
def export_books_csv():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Titel', 'Autor', 'ISBN', 'Status'])
    
    for book in books_collection.find():
        status = f"{book.get('available_copies', 0)} / {book.get('total_copies', 0)}"
        writer.writerow([book['title'], book['author_name'], book['isbn'], status])
   
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=buecher_export.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response

@main_bp.route('/export/users/csv')
@admin_required
def export_users_csv():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Benutzername', 'Rolle', 'Registriert am (UTC)'])
    
    for user in users_collection.find():
        writer.writerow([user['username'], user['role'], user['registered_on'].strftime('%Y-%m-%d %H:%M:%S')])
    
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=benutzer_export.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response

@main_bp.route('/export/authors/csv')
@admin_required
def export_authors_csv():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Biografie'])
    for author in authors_collection.find():
        writer.writerow([author.get('name'), author.get('biography', '')])
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=autoren_export.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response

@main_bp.route('/export/report/top_books/csv')
@admin_required
def export_top_books_report_csv():
    pipeline = [
        {'$group': {'_id': '$book_id', 'loan_count': {'$sum': 1}}},
        {'$sort': {'loan_count': -1}},
        {'$lookup': {'from': 'books', 'localField': '_id', 'foreignField': '_id', 'as': 'book_details'}},
        {'$unwind': '$book_details'},
        {'$project': {'title': '$book_details.title', 'author_name': '$book_details.author_name', 'loan_count': 1, '_id': 0}}
    ]
    report_data = list(loans_collection.aggregate(pipeline))
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Titel', 'Autor', 'Anzahl Ausleihen'])
    
    for row in report_data:
        writer.writerow([row.get('title'), row.get('author_name'), row.get('loan_count')])
        
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=bericht_top_buecher.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response

@main_bp.route('/export/report/top_users/csv')
@admin_required
def export_top_users_report_csv():
    pipeline = [
        {'$group': {'_id': '$user_id', 'loan_count': {'$sum': 1}}},
        {'$sort': {'loan_count': -1}},
        {'$lookup': {'from': 'users', 'localField': '_id', 'foreignField': '_id', 'as': 'user_details'}},
        {'$unwind': '$user_details'},
        {'$project': {'username': '$user_details.username', 'loan_count': 1, '_id': 0}}
    ]
    report_data = list(loans_collection.aggregate(pipeline))

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Benutzername', 'Anzahl Ausleihen'])
    
    for row in report_data:
        writer.writerow([row.get('username'), row.get('loan_count')])
        
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=bericht_top_nutzer.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response

@main_bp.route('/export/report/overdue_books/csv')
@admin_required
def export_overdue_books_report_csv():
    now = datetime.datetime.now(datetime.timezone.utc)

    pipeline = [
        {'$match': {'return_date': None, 'due_date': {'$lt': now}}},
        {'$lookup': {'from': 'books', 'localField': 'book_id', 'foreignField': '_id', 'as': 'book_details'}},
        {'$lookup': {'from': 'users', 'localField': 'user_id', 'foreignField': '_id', 'as': 'user_details'}},
        {'$unwind': '$book_details'}, {'$unwind': '$user_details'},
        {'$project': {
            '_id': 0, 'username': '$user_details.username', 'book_title': '$book_details.title',
            'due_date': '$due_date',
            'days_overdue': {'$floor': {'$divide': [{'$subtract': [now, '$due_date']}, 1000 * 60 * 60 * 24]}}
        }},
        {'$sort': {'due_date': 1}}
    ]
    report_data = list(loans_collection.aggregate(pipeline))
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Nutzername', 'Buchtitel', 'Fällig am', 'Tage überfällig'])
    
    for row in report_data:
        due_date_str = row['due_date'].strftime('%d.%m.%Y')
        writer.writerow([row.get('username'), row.get('book_title'), due_date_str, row.get('days_overdue')])
        
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=bericht_ueberfaellige_buecher.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response