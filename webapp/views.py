from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from webapp.models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
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

def index_libros(request):
    # Obtener el carrito de la sesión
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())

    search_query = request.GET.get('search', '').strip()
    search_type = request.GET.get('type', 'nombre')

    libros = Libro.objects.filter(libStatus='ACT')

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

def index_cartas(request):
    # Obtener el carrito de la sesión
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())

    # Capturamos los parámetros de búsqueda
    search_query = request.GET.get('search', '').strip()
    search_type = request.GET.get('type', 'nombre')  # Por defecto, buscar por nombre

    # Filtro base: Cartas activas
    cartas = Carta.objects.filter(carStatus='ACT')

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
            'cartas': cartas,
            'total_items': total_items,
            'search_query': search_query,
            'search_type': search_type,
            'media_url': settings.MEDIA_URL,
        },
    )

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


def index_carrito(request):
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    return render(request, 'webapp/carrito.html', {'carrito': carrito, 'total': total, 'total_items': total_items})


def index_panel_usuario(request):
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


def index_panel_administrador(request):
    """
    Vista para mostrar el panel del administrador
    """
    usuario = request.user  # Usuario autenticado
    return render(request, 'webapp/panel_administrador.html', {
        'usuario': usuario,
    })


# Funcionalidades del panel de administrador

def index_gestionar_cartas(request):
    """
    Vista para gestionar el stock de cartas.
    Permite ver, editar y actualizar las cartas disponibles.
    """
    cartas = Carta.objects.all()  # Obtener todas las cartas
    return render(request, 'webapp/gestionar_cartas.html', {'cartas': cartas})


def editar_carta(request, carta_codigo):
    """
    Vista para editar una carta específica.
    """
    carta = get_object_or_404(Carta, carCodigo=carta_codigo)

    if request.method == "POST":
        # Capturar datos del formulario
        carta.carNombre = request.POST.get("nombre", carta.carNombre)
        carta.carDescripcion = request.POST.get("descripcion", carta.carDescripcion)
        carta.carPrecio = request.POST.get("precio", carta.carPrecio)
        carta.carCantidad = request.POST.get("cantidad", carta.carCantidad)
        carta.carStatus = request.POST.get("status", carta.carStatus)

        try:
            carta.save()
            messages.success(request, "¡La carta se actualizó correctamente!")
            return redirect('gestionar_cartas')
        except Exception as e:
            messages.error(request, f"Error al actualizar la carta: {e}")

    return render(request, 'webapp/editar_carta.html', {'carta': carta})


def eliminar_carta(request, carta_codigo):
    """
    Vista para eliminar una carta específica.
    """
    carta = get_object_or_404(Carta, carCodigo=carta_codigo)

    if request.method == "POST":
        try:
            carta.delete()
            messages.success(request, "¡La carta fue eliminada correctamente!")
        except Exception as e:
            messages.error(request, f"Error al eliminar la carta: {e}")
        return redirect('gestionar_cartas')

    return render(request, 'webapp/eliminar_carta_confirmacion.html', {'carta': carta})


def index_gestionar_libros(request):
    """
    Vista para gestionar el stock de libros.
    Permite ver, editar y actualizar los libros disponibles.
    """
    libros = Libro.objects.all()  # Obtener todos los libros
    return render(request, 'webapp/gestionar_libros.html', {'libros': libros})


def editar_libro(request, libro_codigo):
    """
    Vista para editar un libro específico.
    """
    libro = get_object_or_404(Libro, libCodigo=libro_codigo)

    if request.method == "POST":
        # Capturar datos del formulario
        libro.libNombre = request.POST.get("nombre", libro.libNombre)
        libro.libAutor = request.POST.get("autor", libro.libAutor)
        libro.libSinopsis = request.POST.get("sinopsis", libro.libSinopsis)
        libro.libCantidad = request.POST.get("cantidad", libro.libCantidad)
        libro.libPrecio = request.POST.get("precio", libro.libPrecio)
        libro.libStatus = request.POST.get("status", libro.libStatus)

        try:
            libro.save()
            messages.success(request, "¡El libro se actualizó correctamente!")
            return redirect('gestionar_libros')
        except Exception as e:
            messages.error(request, f"Error al actualizar el libro: {e}")

    return render(request, 'webapp/editar_libro.html', {'libro': libro})


def eliminar_libro(request, libro_codigo):
    """
    Vista para eliminar un libro específico.
    """
    libro = get_object_or_404(Libro, libCodigo=libro_codigo)

    if request.method == "POST":
        try:
            libro.delete()
            messages.success(request, "¡El libro fue eliminado correctamente!")
        except Exception as e:
            messages.error(request, f"Error al eliminar el libro: {e}")
        return redirect('gestionar_libros')

    return render(request, 'webapp/eliminar_libro_confirmacion.html', {'libro': libro})


def index_gestionar_ordenes(request):
    """
    Vista para gestionar las órdenes de los usuarios.
    Permite ver y actualizar el estado de las órdenes.
    """
    ordenes = Carrito.objects.filter(carStatus__in=["ACT", "FIN"]).order_by('-carCodigo')  # Obtener órdenes activas o finalizadas
    return render(request, 'webapp/gestionar_ordenes.html', {'ordenes': ordenes})


def finalizar_orden(request, codigo_orden):
    """
    Vista para finalizar una orden, cambiando su estado a 'ENT' (Entregado).
    """
    try:
        # Buscar la orden por código
        orden = get_object_or_404(Carrito, carCodigo=codigo_orden)

        # Cambiar estado solo si no está ya entregada
        if orden.carStatus != "ENT":
            orden.carStatus = "ENT"  # Cambiar a "Entregado"
            orden.save()  # Guardar cambios en la base de datos
            messages.success(request, f"La orden {codigo_orden} ha sido marcada como entregada.")
        else:
            messages.info(request, f"La orden {codigo_orden} ya estaba entregada.")
    except Exception as e:
        messages.error(request, f"Hubo un problema al finalizar la orden: {e}")

    # Redirigir a la página de gestión de órdenes
    return redirect('gestionar_ordenes')


def detalle_orden(request, codigo_orden):
    """
    Vista para mostrar los detalles de una orden específica.
    Incluye:
    - Usuario que realizó la orden
    - Libros asociados
    - Productos de la carta asociados
    """
    # Obtener la orden (Carrito)
    orden = get_object_or_404(Carrito, carCodigo=codigo_orden)

    # Obtener los libros y productos de carta asociados a la orden
    libros_en_orden = orden.libros.all()  # Relación con LibrosXCarrito
    cartas_en_orden = orden.carta.all()  # Relación con CartaXCarrito

    # Obtener el usuario que realizó la orden, si existe
    usuario_orden = None
    relacion_usuario = UsuarioXCarrito.objects.filter(carrito=orden).first()
    if relacion_usuario:
        usuario_orden = relacion_usuario.usuario

    return render(request, 'webapp/detalle_orden.html', {
        'orden': orden,
        'libros': libros_en_orden,
        'cartas': cartas_en_orden,
        'usuario_orden': usuario_orden,
    })

# Autenticacion - Operaciones Login / Logut / Register


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
            return redirect('index_panel_usuario')
        else:
            # Si las credenciales no son válidas
            print("Credenciales incorrectas.")
            messages.error(request, "Correo o contraseña incorrectos.")

    return render(request, 'webapp/login.html', {'total_items': total_items})


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


# Carrito - Operaciones Create / Delete / Transaction


def agregar_al_carrito(request, producto_id, cantidad_producto, tipo_producto):
    """
    Agrega un producto al carrito y valida que la cantidad no exceda el stock disponible.
    """

    # Inicializar carrito si no existe en la sesión
    if "carrito" not in request.session:
        request.session["carrito"] = {}

    carrito = request.session["carrito"]

    # Función para obtener datos del producto
    def obtener_datos_producto():
        if tipo_producto == "carta":
            producto = Carta.objects.get(carCodigo=producto_id)
            return {
                "nombre": producto.carNombre,
                "precio": producto.carPrecio,
                "imagen": producto.carFoto.url,
                "stock_disponible": producto.carCantidad,
            }
        elif tipo_producto == "libro":
            producto = Libro.objects.get(libCodigo=producto_id)
            return {
                "nombre": producto.libNombre,
                "precio": producto.libPrecio,
                "imagen": producto.libFoto.url,
                "stock_disponible": producto.libCantidad,
            }

    # Función para validar si hay suficiente stock disponible
    def validar_stock(stock_disponible, cantidad_total):
        stock_restante = stock_disponible - cantidad_total
        if stock_restante < 0:
            messages.error(
                request,
                f"No se puede agregar {cantidad_producto} unidades del producto '{datos_producto['nombre']}' al carrito. "
                f"Stock disponible: {stock_disponible}. Ya tienes {cantidad_actual_en_carrito} en el carrito.",
            )
            # Redirigir al catálogo correspondiente
            return redirect("index_libros" if tipo_producto == "libro" else "index_cartas")
        return None

    # Función para actualizar el carrito en la sesión
    def actualizar_carrito():
        if producto_id in carrito:
            carrito[producto_id]["cantidad"] = cantidad_total
        else:
            carrito[producto_id] = {
                "id": producto_id,
                "nombre": datos_producto["nombre"],
                "precio": float(datos_producto["precio"]),
                "cantidad": cantidad_producto,
                "tipo": tipo_producto,
                "imagen": datos_producto["imagen"],
            }
        messages.success(
            request,
            f"{cantidad_producto} unidad(es) del producto '{datos_producto['nombre']}' añadidas al carrito. ✅",
        )

    # Obtener los datos del producto desde la base de datos
    try:
        datos_producto = obtener_datos_producto()
    except (Carta.DoesNotExist, Libro.DoesNotExist):
        messages.error(request, "El producto solicitado no existe.")
        return redirect("index_libros" if tipo_producto == "libro" else "index_cartas")

    # Obtener la cantidad actual en el carrito
    cantidad_actual_en_carrito = carrito.get(producto_id, {}).get("cantidad", 0)
    cantidad_total = cantidad_actual_en_carrito + int(cantidad_producto)

    # Validar el stock antes de agregar al carrito
    redireccion = validar_stock(datos_producto["stock_disponible"], cantidad_total)
    if redireccion:
        return redireccion

    # Actualizar el carrito con la cantidad válida
    actualizar_carrito()

    # Guardar los cambios en la sesión
    request.session["carrito"] = carrito
    request.session.modified = True

    # Redirigir al carrito
    return redirect("index_carrito")


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
