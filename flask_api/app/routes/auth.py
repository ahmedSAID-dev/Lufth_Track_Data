from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required
from ..models import User

auth_blueprint = Blueprint('auth', __name__, template_folder='../../templates', static_folder='../static')

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'password':
            user = User(username)
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
