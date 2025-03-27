from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from flask_login import login_required
from forms import PersonaForm
from models.provedor import Provedor, db

provedor_page = Blueprint('provedor', __name__, static_folder="static", template_folder="templates")


@provedor_page.route('/')
@login_required
def provedores():
    personas = Provedor.query.all()
    return render_template('provedor/provedor.html', personas=personas, )

@provedor_page.route('/agregar', methods=['GET', 'POST'])
@login_required
def agregar():
    form = PersonaForm()
    if form.validate_on_submit():
        nuevo_provedor = Provedor(nombre=form.nombre.data, telefono=form.telefono.data)
        db.session.add(nuevo_provedor)
        db.session.commit()
        flash('Persona agregada con éxito', 'success')
        return redirect(url_for('provedor'))
    return render_template('provedor/provedores_form.html', form=form, titulo='Agregar Provedor')

@provedor_page.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    provedors = Provedor.query.get_or_404(id)
    form = PersonaForm(obj=provedors)
    if form.validate_on_submit():
        Provedor.nombre = form.nombre.data
        Provedor.telefono = form.telefono.data
        db.session.commit()
        flash('Persona actualizada con éxito', 'success')
        return redirect(url_for('provedor'))
    return render_template('provedor.provedores_form.html', form=form, titulo='Editar Provedor')

@provedor_page.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    provedors = Provedor.query.get_or_404(id)
    db.session.delete(provedors)
    db.session.commit()
    flash('Provedor eliminado con éxito', 'danger')
    return redirect(url_for('provedor'))