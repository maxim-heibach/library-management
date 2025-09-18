# library_app/routes/auth.py
# Blueprint für die Benutzer-Authentifizierung (Registrierung, Login, Logout).

import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from ..db import users_collection
from ..models import User

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if users_collection.find_one({'username': username}):
            flash('Benutzername bereits vergeben.', 'danger')
            return redirect(url_for('auth.register'))
        
        hashed_password = generate_password_hash(password)
        role = 'admin' if users_collection.count_documents({}) == 0 else 'user'
        users_collection.insert_one({
            'username': username, 
            'password': hashed_password, 
            'role': role,
            'registered_on': datetime.datetime.now(datetime.timezone.utc)
        })
       
        flash(f'Registrierung erfolgreich! Sie haben die Rolle "{role}". Bitte anmelden.', 'success')
        
        return redirect(url_for('auth.login'))
   
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_data = users_collection.find_one({'username': username})
       
        if user_data and check_password_hash(user_data['password'], password):
            user_obj = User(user_data)
            login_user(user_obj)
            return redirect(url_for('main.index'))
        else:
            flash('Ungültiger Benutzername oder Passwort.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))