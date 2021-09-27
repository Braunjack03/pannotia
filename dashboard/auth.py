from bcrypt import hashpw, checkpw, gensalt
from flask import Blueprint, current_app, render_template, redirect, url_for, request, flash, send_file
from flask_login import login_user, logout_user, current_user
from .models import User
from . import public_route

auth = Blueprint('auth', __name__, template_folder='templates', static_url_path='', static_folder='static')


@auth.route('/bulma.css')
@public_route
def css():
    return send_file('bulma.css')


@auth.route('/login')
@public_route
def login():
    current_app.logger.info(request)
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    current_app.logger.info(f'Request from {ip}')
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
@public_route
def login_post():
    current_app.logger.info(request)
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    current_app.logger.info(f'Login attempt from {ip}')
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query(email=email, table=f"{current_app.config['USER']}Users")

    if not user or not checkpw(password.encode(), user.password.encode()):
        current_app.logger.warning(f'Login attempt for {email} failed')
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    current_app.logger.info(f'Login for {email}')
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))


@auth.route('/signup')
def signup():
    current_app.logger.info(request)
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    current_app.logger.info(request)
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    current_app.logger.info(f'Signup attempt from {ip}')
    if current_user.level != 1234:
        flash('Insufficient permissions.')
        return redirect(url_for('auth.signup'))

    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    level = request.form.get('level')

    # User already exists
    user = User.query(email=email, table=f"{current_app.config['USER']}User")
    if user:
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    new_user = User(email=email, name=name, password=hashpw(password.encode(), gensalt()).decode(), level=level)
    new_user.add(table=f"{current_app.config['USER']}User")

    flash(f'User {name} created.')
    return redirect(url_for('auth.signup'))


@auth.route('/logout')
def logout():
    current_app.logger.info(request)
    logout_user()
    return redirect(url_for('auth.login'))
