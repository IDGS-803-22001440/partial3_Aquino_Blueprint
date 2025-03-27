from functools import wraps
from flask import Blueprint, abort, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash
from models.usuario import Usuario
from forms import loginForm


auth_page = Blueprint('auth', __name__, static_folder="static", template_folder="templates")  


@auth_page.route('/login', methods=['GET', 'POST'])
def login():
    form = loginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = Usuario.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['id'] = user.id
            session['username'] = user.username
            session['id_rol'] = user.id_rol
            login_user(user)
            flash('Login exitoso', 'success')

            # Redirección según el rol del usuario
            if user.id_rol == 1:
                return redirect(url_for('pizza'))  # Ruta del panel de admin
            elif user.id_rol == 2:
                return redirect(url_for('provedor.provedores'))  # Ruta del dashboard usuario
            else:
                flash('Rol no reconocido', 'danger')
                return redirect(url_for('auth.login'))

        else:
            flash('Usuario o contraseña incorrectos', 'danger')

    return render_template('auth/login.html', form=form)

@auth_page.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Has cerrado sesión exitosamente", "success")
    return redirect(url_for('auth.login'))