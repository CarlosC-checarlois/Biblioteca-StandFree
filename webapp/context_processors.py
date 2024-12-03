def carrito_context(request):
    # Obtener el carrito de la sesión o inicializarlo como vacío
    carrito = request.session.get('carrito', {})
    total_carrito = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    cantidad_items = sum(item['cantidad'] for item in carrito.values())
    return {
        'carrito': carrito,
        'total_carrito': total_carrito,
        'cantidad_items': cantidad_items,
    }
