import re
from http.client import HTTPResponse
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from webapp.models import *
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db import connection
from django.conf import settings
from django.utils.timezone import now
from .models import Usuario, Carrito, UsuarioXCarrito, Libro, Carta, LibrosXCarrito, CartaXCarrito
from django.db import transaction

from django.db.models import F

def index(request):
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    return render(request, 'webapp/index.html', {'total_items': total_items, 'media_url': settings.MEDIA_URL})


def index_cartas(request):
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    # Obtener las cartas desde la base de datos
    cartas = Carta.objects.all()
    return render(request, 'webapp/cartas.html', {'productos': cartas, 'total_items': total_items, 'media_url': settings.MEDIA_URL})


def index_libros(request):
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    libros = Libro.objects.all()
    print(libros)
    return render(request, 'webapp/libros.html',
                  {'libros': libros, 'total_items': total_items, 'media_url': settings.MEDIA_URL})


def index_contacto(request):
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    return render(request, 'webapp/contactos.html', {'total_items': total_items})


def index_logout(request):
    request.session.flush()  # Eliminar todos los datos de sesión
    messages.success(request, "Has cerrado sesión exitosamente.")
    return redirect('index_login')


def index_login(request):
    """
    Vista para manejar el inicio de sesión de usuarios.
    """
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())

    if request.method == "POST":
        # Obtener datos del formulario
        email = request.POST.get("usuario")  # Campo 'usuario' es el correo electrónico
        password = request.POST.get("contraseña")

        print(f"Intento de inicio de sesión: email: {email}")

        # Autenticar al usuario
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Si el usuario es válido, iniciar sesión
            login(request, user)
            messages.success(request, "Inicio de sesión exitoso.")
            print(f"Usuario autenticado: {email}")

            # Redirigir al panel de usuario
            return redirect('index_panel')
        else:
            # Si las credenciales no son válidas
            print("Credenciales incorrectas.")
            messages.error(request, "Correo o contraseña incorrectos.")

    return render(request, 'webapp/login.html', {'total_items': total_items})



def panel_usuario(request):
    """
    Vista para mostrar los carritos del usuario desde UsuarioXCarrito.
    """
    usuario = request.user  # Usuario autenticado

    # Obtener todos los carritos relacionados al usuario actual
    carritos_usuario = (
        UsuarioXCarrito.objects.filter(usuario_id=usuario.id)
        .annotate(
            carrito_codigo=F('carrito__carCodigo'),
            fecha=F('usuxcarFechaModificacion'),
            estado=F('usuxcarStatus'),
        )
        .values('carrito_codigo', 'fecha', 'estado')
    )

    # Ordenar los carritos por fecha de modificación en orden descendente
    carritos_ordenados = sorted(carritos_usuario, key=lambda x: x['fecha'], reverse=True)

    return render(request, 'webapp/panel_usuario.html', {
        'usuario': usuario,
        'carritos': carritos_ordenados,
    })


def index_register(request):
    # Obtener el carrito de la sesión
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())

    if request.method == "POST":
        # Obtener los datos del formulario
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido", "Sin Apellido")
        nacimiento = request.POST.get("nacimiento")
        genero = request.POST.get("genero")
        telefono = request.POST.get("telefono")
        email = request.POST.get("email")
        usuario = request.POST.get("usuario")
        contraseña = request.POST.get("contraseña")
        confirmar_contraseña = request.POST.get("confirmar_contraseña")
        anuncios = request.POST.get("anuncios") == "True"  # Convertir a booleano

        # Validar contraseñas
        if contraseña != confirmar_contraseña:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'webapp/register.html')

        # Verificar si el correo ya existe
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "El correo electrónico ya está registrado.")
            return render(request, 'webapp/register.html')

        # Verificar si el apodo ya existe
        if Usuario.objects.filter(usuApodo=usuario).exists():
            messages.error(request, "El nombre de usuario ya está registrado.")
            return render(request, 'webapp/register.html')

        try:
            # Crear y guardar el usuario
            nuevo_usuario = Usuario(
                usuNombre=nombre,
                usuApellido=apellido,
                usuFechaNacimiento=nacimiento if nacimiento else None,
                usuGenero=genero if genero else None,
                usuTelefono=telefono if telefono else None,
                email=email,
                usuApodo=usuario,
                usuPreferenciaAnuncios=anuncios,
                date_joined=now(),
            )
            nuevo_usuario.set_password(contraseña)  # Encriptar la contraseña
            nuevo_usuario.save()

            # Mostrar mensaje de éxito y redirigir al login
            messages.success(request, "Cuenta creada exitosamente. Inicia sesión ahora.")
            return redirect('index_login')

        except Exception as e:
            # Manejar errores y mostrar un mensaje al usuario
            messages.error(request, f"Hubo un error al crear la cuenta: {str(e)}")
            return render(request, 'webapp/register.html')

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


@transaction.atomic
def finalizar_compra(request):
    if request.method == "POST" and request.user.is_authenticated:
        try:
            # Obtener el carrito desde la sesión
            carrito = request.session.get("carrito", {})
            print(f'Objetos del carrito: {str(carrito)}')

            if not carrito:
                return JsonResponse({"success": False, "error": "El carrito está vacío."})

            # Calcular el total del carrito
            total = sum(item['precio'] * item['cantidad'] for item in carrito.values())

            # Generar código único para el carrito
            numero_carritos = Carrito.objects.count()
            codigo_carrito = f"C-{numero_carritos + 1:05d}"  # Ejemplo: C-00001

            # Crear el carrito
            nuevo_carrito = Carrito.objects.create(
                carCodigo=codigo_carrito,
                carSubtotal=total / 1.15,  # Calcular subtotal antes de IVA
                carIva=total * 0.15,      # IVA del 15%
                carTotal=total,
                carStatus="ACT",
            )

            # Relacionar el carrito con el usuario actual
            UsuarioXCarrito.objects.create(
                usuario_id=request.user.id,
                carrito=nuevo_carrito,
                usuxcarStatus="ACT",
                usuxcarFechaModificacion=now(),
            )

            # Función para obtener el producto y su tipo
            def obtener_producto(codigo_objeto):
                try:
                    carta = Carta.objects.get(carCodigo=codigo_objeto)
                    return carta, "carta"
                except Carta.DoesNotExist:
                    try:
                        libro = Libro.objects.get(libCodigo=codigo_objeto)
                        return libro, "libro"
                    except Libro.DoesNotExist:
                        raise ValueError(f"No existe ningún producto con el código {codigo_objeto}")

            # Procesar cada producto en el carrito
            for item in carrito.values():
                print(f"Procesando item: {item}")
                codigo = item["id"]
                cantidad = item["cantidad"]
                precio_unitario = float(item["precio"])
                total_item = precio_unitario * cantidad
                producto, tipo = obtener_producto(codigo)

                if tipo == "libro":
                    # Insertar en LibrosXCarrito
                    LibrosXCarrito.objects.create(
                        carrito=nuevo_carrito,
                        libro=producto,
                        libxcarCantidad=cantidad,
                        libxcarTotal=total_item,  # Total por este libro
                    )
                elif tipo == "carta":
                    # Insertar en CartaXCarrito
                    CartaXCarrito.objects.create(
                        carrito=nuevo_carrito,
                        carta=producto,
                        carxcarCantidad=cantidad,
                        carxcarTotal=total_item,  # Total por este producto
                    )

            # Limpiar el carrito de la sesión
            request.session["carrito"] = {}
            request.session.modified = True

            return redirect('index_carrito')
        except Exception as e:
            print(f"Error al finalizar la compra: {e}")
            return JsonResponse({"success": False, "error": str(e)})
    else:
        return JsonResponse({"success": False, "error": "Usuario no autenticado o método inválido."})
