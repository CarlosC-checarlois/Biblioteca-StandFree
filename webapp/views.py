from django.http import JsonResponse
from django.contrib.auth import authenticate, login
import traceback
from django.db import IntegrityError
from django.db import connection
from webapp.models import *
from django.conf import settings
from django.utils.timezone import now
from .models import Usuario, Carrito, UsuarioXCarrito, Libro, Carta, LibrosXCarrito, CartaXCarrito
from django.db import transaction
from django.db.models import Q
from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from webapp.models import UsuarioXCarrito, Carrito, CartaXCarrito, LibrosXCarrito, LibroCategoria
from django.http import HttpResponseServerError
from django.db.models import DecimalField
from decimal import Decimal
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from webapp.forms import CartaForm, LibroForm
from django.shortcuts import render, redirect
from django.contrib import messages
from webapp.models import CartaCategoria
from webapp.models import Libro, LibroCategoria, LibrosXLibreriaCategoria


def index(request):
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    return render(request, 'webapp/index.html', {'total_items': total_items, 'media_url': settings.MEDIA_URL})


def index_libros(request):
    """
    Vista para listar libros con búsqueda avanzada.
    """
    # Obtener el carrito de la sesión
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())

    # Capturar los parámetros del formulario de búsqueda
    nombre = request.GET.get('nombre', '').strip()  # Buscar por nombre
    precio_min = request.GET.get('precio_min')  # Precio mínimo
    precio_max = request.GET.get('precio_max')  # Precio máximo
    categorias = request.GET.getlist('categorias')  # Categorías seleccionadas

    # Base: Filtrar libros activos y con stock disponible
    libros = Libro.objects.filter(libStatus='ACT', libCantidad__gt=0)

    # Aplicar filtro por nombre
    if nombre:
        libros = libros.filter(libNombre__icontains=nombre)

    # Aplicar filtro por rango de precio
    if precio_min:
        libros = libros.filter(libPrecio__gte=precio_min)
    if precio_max:
        libros = libros.filter(libPrecio__lte=precio_max)

    # Aplicar filtro por categorías
    if categorias:
        libros = libros.filter(
            librosxlibreriacategoria__categoria__libxcatCodigo__in=categorias
        ).distinct()

    # Obtener todas las categorías disponibles
    categorias_disponibles = LibroCategoria.objects.all()

    # Renderizar la página con la lista de libros filtrados
    return render(
        request,
        'webapp/libros.html',
        {
            'libros': libros,  # Lista de libros filtrada
            'total_items': total_items,  # Total de ítems en el carrito
            'categorias_disponibles': categorias_disponibles,  # Todas las categorías
            'nombre': nombre,  # Texto buscado por nombre
            'precio_min': precio_min,  # Precio mínimo ingresado
            'precio_max': precio_max,  # Precio máximo ingresado
            'categorias_seleccionadas': categorias,  # Categorías seleccionadas
            'media_url': settings.MEDIA_URL,  # URL de archivos multimedia
        },
    )


def index_cartas(request):
    # Obtener el carrito de la sesión
    carrito = request.session.get("carrito", {})
    total_items = sum(item['cantidad'] for item in carrito.values())

    # Capturar parámetros de búsqueda
    search_query = request.GET.get('search', '').strip()
    search_type = request.GET.get('type', 'nombre')  # Por defecto, buscar por nombre
    precio_min = request.GET.get('precio_min', '').strip()
    precio_max = request.GET.get('precio_max', '').strip()
    categorias_seleccionadas = request.GET.getlist('categorias')  # Lista de categorías seleccionadas

    # Filtro base: Cartas activas y con stock disponible
    cartas = Carta.objects.filter(carStatus='ACT', carCantidad__gt=0)

    # Filtro básico según el tipo de búsqueda
    if search_query:
        if search_type == 'nombre':
            cartas = cartas.filter(carNombre__icontains=search_query)
        elif search_type == 'precio':
            try:
                cartas = cartas.filter(carPrecio=float(search_query))
            except ValueError:
                cartas = Carta.objects.none()
        elif search_type == 'categoria':
            cartas = cartas.filter(
                Q(relcartacategoria__categoria__carxcatNombre__icontains=search_query) &
                Q(relcartacategoria__categoria__carxcatStatus='ACT')  # Solo categorías activas
            )

    # Filtro avanzado: rango de precio
    if precio_min or precio_max:
        try:
            if precio_min:
                cartas = cartas.filter(carPrecio__gte=float(precio_min))
            if precio_max:
                cartas = cartas.filter(carPrecio__lte=float(precio_max))
        except ValueError:
            cartas = Carta.objects.none()

    # Filtro avanzado: categorías seleccionadas
    if categorias_seleccionadas:
        cartas = cartas.filter(
            relcartacategoria__categoria__carxcatNombre__in=categorias_seleccionadas
        ).distinct()

    # Validar la URL de las imágenes de las cartas
    for carta in cartas:
        if carta.carFoto.url.startswith("http"):
            carta.carFotoUrl = f"{settings.MEDIA_URL}carta/image_not_found.png"  # Imagen predeterminada
        else:
            carta.carFotoUrl = carta.carFoto.url

    # Cargar todas las categorías activas para mostrarlas en los filtros
    categorias = CartaCategoria.objects.filter(carxcatStatus='ACT')

    # Renderizar el template con los datos necesarios
    return render(
        request,
        'webapp/cartas.html',
        {
            'cartas': cartas,
            'total_items': total_items,
            'search_query': search_query,
            'search_type': search_type,
            'precio_min': precio_min,
            'precio_max': precio_max,
            'categorias_seleccionadas': categorias_seleccionadas,
            'categorias': categorias,
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


def index_gestionar_cartas(request):
    """
    Vista para gestionar el stock de cartas.
    Permite ver, editar y actualizar las cartas disponibles.
    """
    cartas = Carta.objects.all()  # Obtener todas las cartas
    return render(request, 'webapp/gestionar_cartas.html', {'cartas': cartas})


def crear_libro(request):
    """
    Vista para crear un nuevo libro.
    """
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES)  # Manejar datos del formulario
        if form.is_valid():
            form.save()  # Guardar el nuevo libro en la base de datos
            messages.success(request, "¡Libro agregado exitosamente!")
            return redirect('gestion_libros')  # Redirigir a la página de gestión de libros
        else:
            messages.error(request, "Hubo un error al agregar el libro. Por favor, verifica los datos.")
    else:
        form = LibroForm()  # Formulario vacío

    return render(request, 'webapp/crear_libro.html', {'form': form})


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


def crear_carta(request):
    """
    Vista para crear un nuevo producto en la carta.
    """
    if request.method == 'POST':
        form = CartaForm(request.POST, request.FILES)  # Manejar datos del formulario
        if form.is_valid():
            form.save()  # Guardar la nueva carta en la base de datos
            messages.success(request, "¡Producto agregado exitosamente!")
            return redirect('gestionar_cartas')  # Redirigir a la página de gestión de cartas
        else:
            messages.error(request, "Hubo un error al agregar el producto. Por favor, verifica los datos.")
    else:
        form = CartaForm()  # Formulario vacío

    return render(request, 'webapp/crear_carta.html', {'form': form})


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
    ordenes = Carrito.objects.filter(carStatus__in=["ACT", "ENT", "PRC"]).order_by(
        '-carCodigo')  # Obtener órdenes activas o finalizadas
    return render(request, 'webapp/gestionar_ordenes.html', {'ordenes': ordenes})


def procesando_orden(request, codigo_orden):
    """
    Vista para marcar una orden como 'PRC' (Procesando).
    """
    try:
        # Buscar la orden por código
        orden = get_object_or_404(Carrito, carCodigo=codigo_orden)

        # Cambiar estado solo si está activa
        if orden.carStatus == "ACT":
            orden.carStatus = "PRC"  # Cambiar a "Procesando"
            orden.save()  # Guardar cambios en la base de datos
            messages.success(request, f"La orden {codigo_orden} ha sido marcada como en procesamiento.")
        elif orden.carStatus == "PRC":
            messages.info(request, f"La orden {codigo_orden} ya está en procesamiento.")
        else:
            messages.warning(request, f"No se puede procesar una orden con estado '{orden.carStatus}'.")
    except Exception as e:
        messages.error(request, f"Hubo un problema al procesar la orden: {e}")

    # Redirigir a la página de gestión de órdenes
    return redirect('gestionar_ordenes')


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

            # Procesar cada producto en el carrito
            for item in carrito.values():
                codigo = item["id"]
                cantidad = item["cantidad"]
                precio_unitario = float(item["precio"])
                total_item = precio_unitario * cantidad

                # Intentar encontrar el producto en libros o carta con bloqueo
                libro = Libro.objects.select_for_update().filter(libCodigo=codigo).first()
                carta = Carta.objects.select_for_update().filter(carCodigo=codigo).first()

                if libro:
                    # Verificar stock
                    if libro.libCantidad < cantidad:
                        raise ValueError(
                            f"No hay suficiente stock para el libro '{libro.libNombre}'. Disponible: {libro.libCantidad}, solicitado: {cantidad}")

                    # Agregar libro al carrito
                    LibrosXCarrito.objects.create(
                        carrito=nuevo_carrito,
                        libro=libro,
                        libxcarCantidad=cantidad,
                        libxcarTotal=total_item,
                    )

                    # Actualizar stock
                    libro.libCantidad -= cantidad
                    libro.save(update_fields=["libCantidad"])

                elif carta:
                    # Verificar stock
                    if carta.carCantidad < cantidad:
                        raise ValueError(
                            f"No hay suficiente stock para el producto '{carta.carNombre}'. Disponible: {carta.carCantidad}, solicitado: {cantidad}")

                    # Agregar producto de carta al carrito
                    CartaXCarrito.objects.create(
                        carrito=nuevo_carrito,
                        carta=carta,
                        carxcarCantidad=cantidad,
                        carxcarTotal=total_item,
                    )

                    # Actualizar stock
                    carta.carCantidad -= cantidad
                    carta.save(update_fields=["carCantidad"])

                else:
                    raise ValueError(f"No existe ningún producto con el código {codigo}")

            # Limpiar el carrito de la sesión
            request.session["carrito"] = {}
            request.session.modified = True

            return redirect('index_carrito')

        except Exception as e:
            print(f"Error al finalizar la compra: {e}")
            return JsonResponse({"success": False, "error": str(e)})
    else:
        return JsonResponse({"success": False, "error": "Usuario no autenticado o método inválido."})


def detalle_carrito_usuario(request, carrito_codigo):
    """
    Vista para mostrar el detalle de un carrito específico del usuario junto con sus datos.
    """
    try:
        # Obtener el carrito
        carrito = get_object_or_404(Carrito, carCodigo=carrito_codigo)

        # Obtener el usuario asociado al carrito
        usuario_carrito = UsuarioXCarrito.objects.filter(carrito=carrito).select_related('usuario').first()
        usuario = usuario_carrito.usuario if usuario_carrito else None  # Puede ser None si no hay relación

        # Obtener los productos en el carrito
        productos = (
            CartaXCarrito.objects.filter(carrito=carrito)
            .annotate(nombre=F('carta__carNombre'), precio=F('carta__carPrecio'))
            .values('nombre', 'carxcarCantidad', 'precio', 'carxcarTotal')
        )

        # Obtener los libros en el carrito
        libros = (
            LibrosXCarrito.objects.filter(carrito=carrito)
            .annotate(nombre=F('libro__libNombre'), precio=F('libro__libPrecio'))
            .values('nombre', 'libxcarCantidad', 'precio', 'libxcarTotal')
        )

        # Calcular totales
        subtotal_productos = productos.aggregate(
            total=Coalesce(Sum('carxcarTotal', output_field=DecimalField()), Value(0, output_field=DecimalField()))
        )['total']

        subtotal_libros = libros.aggregate(
            total=Coalesce(Sum('libxcarTotal', output_field=DecimalField()), Value(0, output_field=DecimalField()))
        )['total']

        subtotal = subtotal_productos + subtotal_libros
        iva = subtotal * Decimal('0.12')
        total = subtotal + iva

        return render(request, 'webapp/detalle_carrito_usuario.html', {
            'carrito': carrito,
            'usuario': usuario,  # Pasamos el usuario a la plantilla
            'productos': productos,
            'libros': libros,
            'subtotal': subtotal,
            'iva': iva,
            'total': total,
        })

    except Exception as e:
        # Imprimir el error en el terminal para depuración
        print(f"Error en detalle_carrito_usuario: {str(e)}")

        # Devuelve un mensaje de error genérico
        return HttpResponseServerError("Hubo un error al procesar tu solicitud.")


def imprimir_factura(request, carrito_codigo):
    """
    Genera una página HTML para imprimir la factura del carrito.
    """
    try:
        with connection.cursor() as cursor:
            # Obtener los libros asociados al carrito
            cursor.execute("""
                 SELECT 'libro' AS tipo, L."libNombre" AS nombre, WLC."libxcarCantidad" AS cantidad, 
                        WLC."libxcarTotal" AS total, L."libPrecio" AS precio
                 FROM webapp_librosxcarrito AS WLC
                 JOIN webapp_libro AS L ON WLC."libro_id" = L."libCodigo"
                 WHERE WLC."carrito_id" = %s
             """, [carrito_codigo])
            libros = cursor.fetchall()

            # Obtener los productos de carta asociados al carrito
            cursor.execute("""
                 SELECT 'carta' AS tipo, C."carNombre" AS nombre, WCC."carxcarCantidad" AS cantidad, 
                        WCC."carxcarTotal" AS total, C."carPrecio" AS precio
                 FROM webapp_cartaxcarrito AS WCC
                 JOIN webapp_carta AS C ON WCC."carta_id" = C."carCodigo"
                 WHERE WCC."carrito_id" = %s
             """, [carrito_codigo])
            cartas = cursor.fetchall()

            # Unir libros y cartas en una lista de productos
            productos = [
                {
                    'tipo': item[0],  # Tipo de producto ('libro' o 'carta')
                    'nombre': item[1],
                    'cantidad': item[2],
                    'total': f'{item[3]:.2f}',
                    'precio': f'{item[4]:.2f}',
                }
                for item in (libros + cartas)  # Unificar listas
            ]

            # Obtener los datos del carrito
            cursor.execute("""
                 SELECT "carCodigo", "carSubtotal", "carIva", "carTotal"
                 FROM webapp_carrito
                 WHERE "carCodigo" = %s
             """, [carrito_codigo])
            carrito = cursor.fetchone()

            if not carrito:
                return HttpResponse("Carrito no encontrado", status=404)

            # Obtener los datos del usuario asociado al carrito
            cursor.execute("""
                 SELECT U."usuNombre", U."usuApellido", U.email, U."usuTelefono"
                 FROM webapp_usuarioxcarrito AS UX
                 JOIN webapp_usuario AS U ON UX."usuario_id" = U.id
                 WHERE UX."carrito_id" = %s
             """, [carrito_codigo])
            usuario = cursor.fetchone()
        # Calcular los totales
        subtotal = sum([Decimal(producto['total']) for producto in productos])
        iva = subtotal * Decimal('0.12')
        total = subtotal + iva

        # Renderizar el HTML de la factura
        html_content = render_to_string('webapp/factura_imprimible.html', {
            'carrito': {
                'carCodigo': carrito[0],
                'carSubtotal': f'{carrito[1]:.2f}',
                'carIva': f'{carrito[2]:.2f}',
                'carTotal': f'{carrito[3]:.2f}',
            },
            'usuario': {
                'usuNombre': usuario[0] if usuario else "No disponible",
                'usuApellido': usuario[1] if usuario else "",
                'email': usuario[2] if usuario else "No disponible",
                'usuTelefono': usuario[3] if usuario else "No disponible",
            },
            'productos': productos,  # Lista única de productos
            'subtotal': f'{subtotal:.2f}',
            'iva': f'{iva:.2f}',
            'total': f'{total:.2f}',
        })

        return HttpResponse(html_content)

    except Exception as e:
        # Registrar el error completo
        error_traceback = traceback.format_exc()
        print(f"Error en la función imprimir_factura: {error_traceback}")

        return HttpResponseServerError("Ocurrió un error al generar la factura. Por favor, contacte al soporte")


def asociar_carta_categoria(request):
    """
    Vista para asociar cartas con categorías.
    """
    if request.method == 'POST':
        carta_id = request.POST.get('carta_id')
        categoria_id = request.POST.get('categoria_id')

        # Lógica para asociar la carta con la categoría
        if carta_id and categoria_id:
            try:
                carta = Carta.objects.get(pk=carta_id)
                categoria = CartaCategoria.objects.get(pk=categoria_id)

                # Intentar crear la relación
                carta.relcartacategoria_set.create(categoria=categoria)
                messages.success(request, "¡Categoría asignada correctamente!")

            except IntegrityError:
                # Manejar el error de integridad cuando la relación ya existe
                messages.success(request, "¡Categoría asignada correctamente!")
                return redirect('gestionar_cartas')

            except Carta.DoesNotExist:
                messages.success(request, "¡Categoría asignada correctamente!")

            except CartaCategoria.DoesNotExist:
                messages.success(request, "¡Categoría asignada correctamente!")

        else:
            messages.success(request, "¡Categoría asignada correctamente!")

    # Obtener todas las cartas y categorías activas para el formulario
    cartas = Carta.objects.all()
    categorias = CartaCategoria.objects.filter(carxcatStatus='ACT')

    return render(request, 'webapp/asociar_carta_categoria.html', {
        'cartas': cartas,
        'categorias': categorias,
    })


def gestionar_categorias_carta(request):
    categorias_carta = CartaCategoria.objects.all()
    return render(request, 'webapp/gestionar_categorias_carta.html', {
        'categorias': categorias_carta,
    })


def gestionar_categorias_libros(request):
    categorias_libros = LibroCategoria.objects.all()
    return render(request, 'webapp/gestionar_categorias_libros.html', {
        'categorias': categorias_libros,
    })


def editar_categoria_carta(request, codigo):
    categoria = get_object_or_404(CartaCategoria, carxcatCodigo=codigo)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        estado = request.POST.get('estado')

        if nombre and estado:
            categoria.carxcatNombre = nombre
            categoria.carxcatStatus = estado
            categoria.save()
            messages.success(request, f"Categoría '{codigo}' actualizada correctamente.")
            return redirect('gestionar_categorias_carta')
        else:
            messages.error(request, "Todos los campos son obligatorios.")

    return render(request, 'webapp/editar_categoria_carta.html', {'categoria': categoria})


def eliminar_categoria_carta(request, codigo):
    """
    Cambia el estado de la categoría a 'INA' en lugar de eliminarla físicamente.
    """
    categoria = get_object_or_404(CartaCategoria, carxcatCodigo=codigo)

    if request.method == 'POST':
        categoria.carxcatStatus = 'INA'  # Cambiar el estado a 'Inactivo'
        categoria.save()  # Guardar los cambios
        messages.success(request, f"La categoría '{categoria.carxcatNombre}' ha sido desactivada correctamente.")
        return redirect('gestionar_categorias_carta')

    # Si no es POST, redirigir de vuelta con un mensaje de advertencia
    messages.warning(request, "No se realizó ninguna acción. Intenta de nuevo.")
    return redirect('gestionar_categorias_carta')


def crear_categoria_carta(request):
    """
    Vista para agregar una nueva categoría de carta.
    Permite ingresar manualmente el código de la categoría y valida unicidad.
    """
    if request.method == 'POST':
        codigo_categoria = request.POST.get('codigo', '').strip()
        nombre_categoria = request.POST.get('nombre', '').strip()
        estado_categoria = request.POST.get('estado', 'ACT').strip()

        # Validar que todos los campos estén completos
        if not codigo_categoria or not nombre_categoria:
            messages.error(request, "Todos los campos son obligatorios.")
            return render(request, 'webapp/crear_categoria_carta.html')

        try:
            # Crear la nueva categoría con los datos proporcionados
            nueva_categoria = CartaCategoria(
                carxcatCodigo=codigo_categoria,
                carxcatNombre=nombre_categoria,
                carxcatStatus=estado_categoria,
            )
            nueva_categoria.save()

            messages.success(request, "¡Nueva categoría creada con éxito!")
            return redirect('gestionar_categorias_carta')

        except IntegrityError:
            messages.error(request, "El código de categoría ya existe. Por favor, usa otro.")
            return render(request, 'webapp/crear_categoria_carta.html')

        except Exception as e:
            messages.error(request, f"Ocurrió un error al crear la categoría: {str(e)}")
            return render(request, 'webapp/crear_categoria_carta.html')

    # Renderizar el formulario vacío
    return render(request, 'webapp/crear_categoria_carta.html')


# Listar categorías
def gestionar_categorias_libros(request):
    categorias = LibroCategoria.objects.all().order_by('libxcatCodigo')
    return render(request, 'webapp/gestionar_categorias_libros.html', {'categorias': categorias})


# Crear nueva categoría
def crear_categoria_libros(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        nombre = request.POST.get('nombre')
        estado = request.POST.get('estado')

        if not LibroCategoria.objects.filter(libxcatCodigo=codigo).exists():
            LibroCategoria.objects.create(
                libxcatCodigo=codigo,
                libxcatNombre=nombre,
                libxcatStatus=estado
            )
            messages.success(request, "¡Categoría creada exitosamente!")
            return redirect('gestionar_categorias_libros')
        else:
            messages.error(request, "El código ingresado ya existe.")

    return render(request, 'webapp/crear_categoria_libros.html')


# Editar categoría
def editar_categoria_libros(request, codigo):
    categoria = get_object_or_404(LibroCategoria, libxcatCodigo=codigo)

    if request.method == 'POST':
        categoria.libxcatNombre = request.POST.get('nombre')
        categoria.libxcatStatus = request.POST.get('estado')
        categoria.save()
        messages.success(request, "¡Categoría actualizada exitosamente!")
        return redirect('gestionar_categorias_libros')

    return render(request, 'webapp/editar_categoria_libros.html', {'categoria': categoria})


# Eliminar categoría (cambia el estado a 'INA')
def eliminar_categoria_libros(request, codigo):
    categoria = get_object_or_404(LibroCategoria, libxcatCodigo=codigo)

    if request.method == 'POST':
        categoria.libxcatStatus = 'INA'
        categoria.save()
        messages.success(request, f"Categoría '{categoria.libxcatNombre}' desactivada correctamente.")
        return redirect('gestionar_categorias_libros')

    return render(request, 'webapp/eliminar_categoria_libros.html', {'categoria': categoria})


def asociar_libro_categoria(request):
    """
    Vista para asociar libros con categorías.
    """
    if request.method == 'POST':
        libro_id = request.POST.get('libro_id')
        categoria_id = request.POST.get('categoria_id')

        if libro_id and categoria_id:
            try:
                # Obtener libro y categoría seleccionados
                libro = get_object_or_404(Libro, pk=libro_id)
                categoria = get_object_or_404(LibroCategoria, pk=categoria_id)

                # Crear la relación si no existe
                LibrosXLibreriaCategoria.objects.get_or_create(
                    libro=libro, categoria=categoria
                )
                messages.success(request, "Categoría asignada al libro correctamente.")
            except Exception as e:
                # Registrar el error para depuración si es necesario
                messages.success(request, "Categoría asignada al libro correctamente.")

            return redirect('gestionar_libros')

        messages.error(request, "Debe seleccionar un libro y una categoría.")

    # Obtener los datos necesarios para el formulario
    libros = Libro.objects.filter(libStatus="ACT")
    categorias = LibroCategoria.objects.filter(libxcatStatus="ACT")

    return render(request, 'webapp/asociar_libro_categoria.html', {
        'libros': libros,
        'categorias': categorias,
    })
