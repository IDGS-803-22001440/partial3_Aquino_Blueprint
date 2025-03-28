from functools import wraps
from flask import Blueprint, abort, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from models.model import Usuario, db
from forms import RegisterForm, loginForm


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


@auth_page.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        hashed_password = generate_password_hash(password)

        new_user = Usuario(username=username, password=hashed_password, id_rol=1)  # id_rol por defecto en 1
        db.session.add(new_user)
        db.session.commit()

        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for('auth.login'))

    return render_template('registro.html', form=form)




@auth_page.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Has cerrado sesión exitosamente", "success")
    return redirect(url_for('auth.login'))


def role_required(role_id):
    """ Decorador para restringir acceso según el id_rol del usuario """
    def decorator(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.id_rol != role_id:
                abort(404)  # Mostrar error 404 en lugar de redirigir a login
            return f(*args, **kwargs)
        return wrapped_function
    return decorator