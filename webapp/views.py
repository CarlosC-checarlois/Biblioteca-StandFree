import re
from webapp.models import *
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db import connection  # Para ejecutar SQL directamente


def index(request):
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    return render(request, 'webapp/index.html', {'total_items': total_items})


def index_cartas(request):
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    # Obtener las cartas desde la base de datos
    cartas = Carta.objects.all()
    return render(request, 'webapp/cartas.html', {'productos': cartas, 'total_items': total_items})


def index_libros(request):
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    libros = Libro.objects.all()
    print(libros)
    return render(request, 'webapp/libros.html', {'libros': libros, 'total_items': total_items})


def index_contacto(request):
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    return render(request, 'webapp/contactos.html', {'total_items': total_items})


def index_login(request):
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    return render(request, 'webapp/login.html', {'total_items': total_items})


def index_register(request):
    # Obtener el carrito de la sesión
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())

    if request.method == 'POST':
        # Recibir datos del formulario
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        apodo = request.POST.get('usuario')
        contraseña = request.POST.get('contraseña')
        confirmar_contraseña = request.POST.get('confirmar_contraseña')

        # Validaciones
        if not nombre or not email or not apodo or not contraseña or not confirmar_contraseña:
            messages.error(request, "Todos los campos son requeridos.")
            return render(request, 'webapp/register.html', {'total_items': total_items})

        if contraseña != confirmar_contraseña:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'webapp/register.html', {'total_items': total_items})

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            messages.error(request, "Correo electrónico no válido.")
            return render(request, 'webapp/register.html', {'total_items': total_items})
        # Comprobar si el correo o usuario ya existen
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM webapp_usuario WHERE usuCorreo = %s OR usuCodigo = %s", [email, usuario])
            if cursor.fetchone()[0] > 0:
                messages.error(request, "El correo o usuario ya están en uso.")
                return render(request, 'webapp/register.html', {'total_items': total_items})

        # Insertar el usuario en la base de datos
        try:
            contraseña_encriptada = make_password(contraseña)  # Encriptar la contraseña
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO webapp_usuario (usuCodigo, usuNombre, usuCorreo, usuClave, usuStatus)
                    VALUES (%s, %s, %s, %s, %s)
                """, [apodo, nombre, email, contraseña_encriptada, 'ACT'])

            messages.success(request, "Cuenta creada con éxito. ¡Bienvenido!")
            return redirect('index_login')  # Redirigir al login tras el registro exitoso

        except Exception as e:
            messages.error(request, f"Error al registrar el usuario: {str(e)}")
            return render(request, 'webapp/register.html', {'total_items': total_items})

    return render(request, 'webapp/register.html', {'total_items': total_items})

def agregar_al_carrito(request, producto_id, tipo_producto):
    if "carrito" not in request.session:
        request.session["carrito"] = {}

    carrito = request.session["carrito"]

    if tipo_producto == "carta":
        producto = Carta.objects.get(carCodigo=producto_id)
        nombre = producto.carNombre
        precio = producto.carPrecio  # Cambia a carPrecio
        imagen = producto.carFoto.url
    elif tipo_producto == "libro":
        producto = Libro.objects.get(libCodigo=producto_id)
        nombre = producto.libNombre
        precio = producto.libPrecio  # Aquí está el cambio: usa libPrecio
        imagen = producto.libFoto.url

    if str(producto_id) in carrito:
        carrito[str(producto_id)]['cantidad'] += 1
    else:
        carrito[str(producto_id)] = {
            'id': producto_id,
            'nombre': nombre,
            'precio': float(precio),  # Asegúrate de que el precio se asigne correctamente
            'cantidad': 1,
            'tipo': tipo_producto,
            'imagen': imagen,
        }

    request.session["carrito"] = carrito
    request.session.modified = True
    return redirect('index_carrito')


# Ver el carrito
def index_carrito(request):
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    return render(request, 'webapp/carrito.html', {'carrito': carrito, 'total': total, 'total_items': total_items})


def eliminar_del_carrito(request, producto_id, tipo_producto):
    carrito = request.session.get("carrito", {})

    if str(producto_id) in carrito:
        del carrito[str(producto_id)]
        request.session["carrito"] = carrito
        request.session.modified = True

    return redirect('index_carrito')
