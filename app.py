from functools import wraps
from werkzeug.security import check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from flask import abort, flash
from flask_wtf.csrf import CSRFProtect
from flask import Flask, render_template, request, redirect, url_for, session
from config import DevelopmentConfig
from flask import g
from forms import PizzaForm, ClienteForm, loginForm, logoutForm
from models.model import Venta, DetallePizza, IngredientePizza, Usuario, db
from controller.auth import role_required
import json
from controller.pedidos import agregarPizza, cargarCarrito, pedidos_page, vaciarCarrito
from controller.auth import auth_page
from controller.provedorController import provedor_page

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
csrf = CSRFProtect()
login_manager_app = LoginManager(app)
app.register_blueprint(pedidos_page, url_prefix="/pedidos")
app.register_blueprint(auth_page, url_prefix="/auth")
app.register_blueprint(provedor_page, url_prefix="/provedor")


@login_manager_app.user_loader
def load_user(id):
    return Usuario.query.get(int(id))

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404




@app.route("/pizza", methods=['GET', 'POST'])
@login_required
@role_required(1)
def pizza():
    
    pizza_form = PizzaForm()
    cliente_form = ClienteForm()

    if 'cliente_data' in session:
        cliente_form.nombre.data = session['cliente_data'].get('nombre', '')
        cliente_form.direccion.data = session['cliente_data'].get(
            'direccion', '')
        cliente_form.telefono.data = session['cliente_data'].get(
            'telefono', '')

    if request.method == 'POST' and pizza_form.validate_on_submit():
        session['cliente_data'] = {
            'nombre': cliente_form.nombre.data,
            'direccion': cliente_form.direccion.data,
            'telefono': cliente_form.telefono.data
        }

        if not pizza_form.ingredientes.data:
            flash('Debes seleccionar al menos un ingrediente', 'danger')
            return redirect(url_for('pizza'))

        agregarPizza(pizza_form.tamano.data, pizza_form.numPizzas.data,
                     pizza_form.ingredientes.data)
        flash('Pizza agregada al carrito', 'success')
        return redirect(url_for('pizza'))

    carrito = cargarCarrito()

    ventas_hoy = []
    ventas_mes = []
    total_ventas_hoy = 0
    total_ventas_mes = 0
    
    try:

        ventas_hoy = Venta.query.filter(db.func.date(
            Venta.fecha) == db.func.current_date()).all()
        total_ventas_hoy = sum(venta.total_venta for venta in ventas_hoy)
        ventas_mes = Venta.query.filter(
        db.func.extract('year', Venta.fecha) == db.func.extract('year', db.func.current_date()),
        db.func.extract('month', Venta.fecha) == db.func.extract('month', db.func.current_date())
        ).all()
        total_ventas_mes = sum(venta.total_venta for venta in ventas_mes)
        
    except:
        ventas_hoy = []
        ventas_mes = []
        

    return render_template('index.html',
                           pizza_form=pizza_form,
                           cliente_form=cliente_form,
                           carrito=carrito,
                           ventas_hoy=ventas_hoy,
                           ventas_mes=ventas_mes,
                           total_ventas_mes=total_ventas_mes,
                           total_ventas_hoy=total_ventas_hoy)


@app.route('/eliminar_carrito', methods=['POST'])
def eliminar_carrito():
    vaciarCarrito()
    flash("Carrito vaciado correctamente", "info")
    return redirect(url_for('pizza'))

def status_401(error):
    return redirect(url_for('login'))



if __name__ == '__main__':
    csrf.init_app(app)
    db.init_app(app)
    app.register_error_handler(401,status_401)
    with app.app_context():
        db.create_all()
    app.run()
