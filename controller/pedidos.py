from flask import Blueprint, request, session, flash, redirect, url_for
from models.model import Venta, DetallePizza, IngredientePizza,db
from forms import ClienteForm

pedidos_page = Blueprint('pedidos', __name__, static_folder="static", template_folder="templates")


@pedidos_page.route('/finalizarPedido', methods=['GET', 'POST'])
def finalizarPedido():
    cliente_form = ClienteForm()
    pizzas = cargarCarrito()

    if not pizzas:
        flash("No hay pizzas en el carrito", "danger")
        return redirect(url_for('pizza'))

    if request.method == 'POST':
        if cliente_form.validate_on_submit():
            nombre = cliente_form.nombre.data
            direccion = cliente_form.direccion.data
            telefono = cliente_form.telefono.data

            session['cliente_data'] = {
                'nombre': nombre,
                'direccion': direccion,
                'telefono': telefono
            }
        elif 'cliente_data' in session:
            nombre = session['cliente_data'].get('nombre')
            direccion = session['cliente_data'].get('direccion')
            telefono = session['cliente_data'].get('telefono')
        else:
            flash("Por favor complete los datos del cliente", "danger")
            return redirect(url_for('pizza'))

        if not nombre or not direccion or not telefono:
            flash("Por favor complete todos los datos del cliente", "danger")
            return redirect(url_for('pizza'))

        subtotal_total = 0
        for pizza in pizzas:
            precio_inicial = PRECIOS[pizza["tamano"]]
            precio_ingredientes = len(
                pizza["ingredientes"]) * COSTO_INGREDIENTE
            subtotal_pieza = precio_inicial + precio_ingredientes
            subtotal_total += subtotal_pieza * int(pizza["cantidad"])

        nueva_venta = Venta(
            nombre_cliente=nombre,
            direccion_cliente=direccion,
            telefono_cliente=telefono,
            total_venta=subtotal_total
        )

        db.session.add(nueva_venta)
        db.session.flush()

        for pizza in pizzas:
            precio_inicial = PRECIOS[pizza["tamano"]]
            precio_ingredientes = len(
                pizza["ingredientes"]) * COSTO_INGREDIENTE
            subtotal_pieza = precio_inicial + precio_ingredientes
            subtotal_total_pizza = subtotal_pieza * int(pizza["cantidad"])

            detalle = DetallePizza(
                venta_id=nueva_venta.id,
                tamano=pizza["tamano"],
                cantidad=pizza["cantidad"],
                subtotal=subtotal_total_pizza
            )

            db.session.add(detalle)
            db.session.flush()

            for ingrediente in pizza["ingredientes"]:
                ing = IngredientePizza(
                    detalle_pizza_id=detalle.id,
                    nombre_ingrediente=ingrediente
                )
                db.session.add(ing)

        try:
            db.session.commit()
            vaciarCarrito()
            flash("Pedido finalizado correctamente", "success")
            return redirect(url_for('pizza'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al procesar el pedido: {str(e)}", "danger")
            return redirect(url_for('pizza'))

    return redirect(url_for('pizza'))


@pedidos_page.route("/eliminar/<int:indice>", methods=["POST"])
def eliminar_pizza(indice):
    if eliminarPizzaEspecifica(indice):
        flash("Pizza eliminada del carrito", "success")
    else:
        flash("No se pudo eliminar la pizza", "danger")
    return redirect(url_for("pizza"))

def agregarPizza(tamano, cantidad, ingredientes):
    with open("pedidos.txt", "a", encoding="utf-8") as archivo:
        archivo.write(f"{tamano}|{cantidad}|{','.join(ingredientes)}\n")

def cargarCarrito():
    carrito = []
    try:
        with open("pedidos.txt", "r", encoding="utf-8") as archivo:
            carrito = [{"tamano": l.split("|")[0], "cantidad": l.split("|")[1], "ingredientes": l.split("|")[2].split(",")} for l in archivo.readlines()]
    except FileNotFoundError:
        pass
    return carrito

def vaciarCarrito():
    open("pedidos.txt", "w").close()

def eliminarPizzaEspecifica(indice):
    carrito = cargarCarrito()
    if 0 <= indice < len(carrito):
        carrito.pop(indice)
        with open("pedidos.txt", "w", encoding="utf-8") as archivo:
            for pizza in carrito:
                ingredientes_lista = ",".join(pizza["ingredientes"])
                archivo.write(
                    f"{pizza['tamano']}|{pizza['cantidad']}|{ingredientes_lista}\n")
        return True
    return False



PRECIOS = {
    'pequena': 40,
    'mediana': 80,
    'grande': 120
}

COSTO_INGREDIENTE = 10
