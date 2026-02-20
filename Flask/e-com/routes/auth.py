from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import User
from db import db

routes = Blueprint('auth', __name__)

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first() is None:
            flash('Invalid username or password!', 'error')
            return redirect(url_for('auth.login'))
        elif not User.query.filter_by(username=username).first().check_password(password):
            flash('Invalid username or password!', 'error')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(username=username).first()
        session['user_id'] = user.id
        session['user_type'] = user.user_type.value
        session['username'] = username
        flash('Login successful!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')


@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('auth.register'))
        elif User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('auth.register'))
        # create new user
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))  

    return render_template('register.html')


@routes.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))