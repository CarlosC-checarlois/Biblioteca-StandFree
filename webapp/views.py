import re
from http.client import HTTPResponse
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from webapp.models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db import connection
from django.conf import settings
from django.utils.timezone import now
from .models import Usuario, Carrito, UsuarioXCarrito, Libro, Carta, LibrosXCarrito, CartaXCarrito
from django.db import transaction
from django.db.models import Q
from django.db.models import F


def index(request):
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    return render(request, 'webapp/index.html', {'total_items': total_items, 'media_url': settings.MEDIA_URL})


def index_cartas(request):
    # Obtener el carrito de la sesión
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())

    # Capturamos los parámetros de búsqueda
    search_query = request.GET.get('search', '').strip()
    search_type = request.GET.get('type', 'nombre')  # Por defecto, buscar por nombre

    # Filtro base: Cartas activas
    cartas = Carta.objects.filter(carStatus_1='ACT')

    # Aplicar filtros según el tipo de búsqueda
    if search_query:
        if search_type == 'nombre':
            cartas = cartas.filter(carNombre__icontains=search_query)
        elif search_type == 'precio':
            try:
                # Intentar filtrar por precio
                cartas = cartas.filter(carPrecio=float(search_query))
            except ValueError:
                # Si no es un precio válido, no devolver resultados
                cartas = Carta.objects.none()
        elif search_type == 'categoria':
            # Filtrar por categoría usando relaciones
            cartas = cartas.filter(
                Q(relcartacategoria__categoria__carxcatNombre__icontains=search_query),
                Q(relcartacategoria__categoria__carxcatStatus='ACT')  # Solo categorías activas
            )

    # Renderizar el template
    return render(
        request,
        'webapp/cartas.html',
        {
            'productos': cartas,
            'total_items': total_items,
            'search_query': search_query,
            'search_type': search_type,
            'media_url': settings.MEDIA_URL,
        },
    )
def index_libros(request):
    # Obtener el carrito de la sesión
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())

    # Capturamos los parámetros de búsqueda
    search_query = request.GET.get('search', '').strip()  # Eliminar espacios en blanco adicionales
    search_type = request.GET.get('type', 'nombre')  # Tipo de búsqueda (por defecto 'nombre')

    # Filtro base: Libros activos
    libros = Libro.objects.filter(libStatus=True)

    # Aplicamos los filtros según el tipo de búsqueda
    if search_query:
        if search_type == 'nombre':
            libros = libros.filter(libNombre__icontains=search_query)  # Buscar por nombre (contiene)
        elif search_type == 'precio':
            try:
                libros = libros.filter(libPrecio=float(search_query))  # Buscar por precio exacto
            except ValueError:
                libros = Libro.objects.none()  # No mostrar resultados si el precio no es válido
        elif search_type == 'categoria':
            # Filtrar libros asociados a la categoría
            libros = libros.filter(
                librosxlibreriacategoria__categoria__libxcatNombre__icontains=search_query
            )

    # Renderizar el template con el contexto
    return render(
        request,
        'webapp/libros.html',
        {
            'libros': libros,  # Lista de libros filtrada
            'total_items': total_items,  # Total de ítems en el carrito
            'search_query': search_query,  # Texto buscado
            'search_type': search_type,  # Tipo de búsqueda seleccionado
            'media_url': settings.MEDIA_URL,  # URL para los archivos de medios
        },
    )


def index_contacto(request):
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        email = request.POST.get("email")
        mensaje = request.POST.get("mensaje")

        if nombre and email and mensaje:
            # Guardar el mensaje en la base de datos
            Contacto.objects.create(nombre=nombre, email=email, mensaje=mensaje)
            # Mostrar un mensaje de éxito o redirigir a la misma página con una confirmación
            return render(request, 'webapp/contactos.html', {
                'total_items': total_items,
                'success_message': "¡Gracias por contactarnos! Tu mensaje ha sido enviado.",
            })

        # En caso de error en el formulario, mostrar un mensaje de error
        return render(request, 'webapp/contactos.html', {
            'total_items': total_items,
            'error_message': "Por favor, completa todos los campos correctamente.",
        })

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
                carIva=total * 0.15,  # IVA del 15%
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


def detalle_libro(request, libro_codigo):
    # Buscar el libro en la base de datos
    libro = get_object_or_404(Libro, libCodigo=libro_codigo)
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())

    # Renderizar el template con los detalles del libro
    return render(request, 'webapp/detalle_libros.html', {
        'libro': libro,
        'total_items': total_items
    })


def detalle_carta(request, carCodigo):
    # Obtener la carta basada en el código único
    carta = get_object_or_404(Carta, carCodigo=carCodigo)

    # Datos del carrito (si existen)
    total_items = sum(item['cantidad'] for item in request.session.get("carrito", {}).values())

    # Renderizar el template de detalle
    return render(request, 'webapp/detalle_cartas.html', {
        'carta': carta,
        'total_items': total_items,
    })
