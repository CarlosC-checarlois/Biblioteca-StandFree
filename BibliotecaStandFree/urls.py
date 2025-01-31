"""BibliotecaStandFree URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from webapp import views as webapp_views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404
from django.shortcuts import render

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('usuario/panel/', webapp_views.index_panel_usuario, name='index_panel_usuario'),
                  path('usuario/panel_administrador/', webapp_views.index_panel_administrador,
                       name='index_panel_administrador'),
                  path('', webapp_views.index, name='index'),
                  path('cartas/', webapp_views.index_cartas, name='index_cartas'),
                  path('libros/', webapp_views.index_libros, name='index_libros'),
                  path('login/', webapp_views.index_login, name='index_login'),
                  path('register/', webapp_views.index_register, name='index_register'),
                  path('carrito/', webapp_views.index_carrito, name='index_carrito'),
                  path('contacto/', webapp_views.index_contacto, name='index_contacto'),
                  path('carrito/agregar/<str:producto_id>/<str:tipo_producto>/', webapp_views.agregar_al_carrito,
                       name='agregar_al_carrito'),
                  path("finalizar_compra/", webapp_views.finalizar_compra, name="finalizar_compra"),
                  path('carrito/eliminar/<str:producto_id>/<str:tipo_producto>/', webapp_views.eliminar_del_carrito,
                       name='eliminar_del_carrito'),
                  path('logout/', webapp_views.index_logout, name='index_logout'),
                  path('libros/detalle/<str:libro_codigo>/', webapp_views.detalle_libro, name='detalle_libro'),
                  path('cartas/detalle/<str:carCodigo>/', webapp_views.detalle_carta, name='detalle_carta'),

                  path('gestionar/cartas/', webapp_views.index_gestionar_cartas, name='gestionar_cartas'),
                  path('gestionar/cartas/editar/<str:carta_codigo>/', webapp_views.editar_carta, name='editar_carta'),
                  path('gestionar/cartas/eliminar/<str:carta_codigo>/', webapp_views.eliminar_carta,
                       name='eliminar_carta'),

                  path('gestionar/libros/', webapp_views.index_gestionar_libros, name='gestionar_libros'),
                  path('gestionar/libros/editar/<str:libro_codigo>/', webapp_views.editar_libro, name='editar_libro'),
                  path('gestionar/libros/eliminar/<str:libro_codigo>/', webapp_views.eliminar_libro,
                       name='eliminar_libro'),

                  path('gestionar/ordenes/', webapp_views.index_gestionar_ordenes, name='gestionar_ordenes'),
                  path('gestionar/ordenes/finalizar/<str:codigo_orden>/', webapp_views.finalizar_orden,
                       name='finalizar_orden'),
                  path('gestionar/ordenes/detalle/<str:codigo_orden>/', webapp_views.detalle_orden,
                       name='detalle_orden'),
                  path('gestionar/ordenes/procesar/<str:codigo_orden>/', webapp_views.procesando_orden,
                       name='procesando_orden'),
                  # Nueva ruta

                  path('carrito/agregar/<str:producto_id>/<int:cantidad_producto>/<str:tipo_producto>/',
                       webapp_views.agregar_al_carrito, name='agregar_al_carrito'),

                  path('panel-usuario/', webapp_views.index_panel_usuario, name='panel_usuario'),
                  path('detalle-carrito/<str:carrito_codigo>/', webapp_views.detalle_carrito_usuario,
                       name='detalle_carrito_usuario'),
                  path('imprimir-factura/<str:carrito_codigo>/', webapp_views.imprimir_factura,
                       name='imprimir_factura'),
                  path('crear-carta/', webapp_views.crear_carta, name='crear_carta'),
                  path('crear-libro/', webapp_views.crear_libro, name='crear_libro'),

                  # Otras rutas
                  path('categorias-carta/', webapp_views.gestionar_categorias_carta, name='gestionar_categorias_carta'),
                  path('categorias-libros/', webapp_views.gestionar_categorias_libros,
                       name='gestionar_categorias_libros'),
                  path('asociar-carta-categoria/', webapp_views.asociar_carta_categoria,
                       name='asociar_carta_categoria'),

                  # Ruta para gestionar categorías de carta
                  path('categorias-carta/', webapp_views.gestionar_categorias_carta, name='gestionar_categorias_carta'),

                  # Ruta para editar una categoría de carta
                  path('categorias-carta/editar/<str:codigo>/', webapp_views.editar_categoria_carta,
                       name='editar_categoria_carta'),

                  # Ruta para eliminar una categoría de carta
                  path('categorias-carta/eliminar/<str:codigo>/', webapp_views.eliminar_categoria_carta,
                       name='eliminar_categoria_carta'),
                  path('crear-categoria-carta/', webapp_views.crear_categoria_carta, name='crear_categoria_carta'),

                  path('categorias-libros/', webapp_views.gestionar_categorias_libros,
                       name='gestionar_categorias_libros'),
                  path('categorias-libros/crear/', webapp_views.crear_categoria_libros, name='crear_categoria_libros'),
                  path('categorias-libros/editar/<str:codigo>/', webapp_views.editar_categoria_libros,
                       name='editar_categoria_libros'),
                  path('categorias-libros/eliminar/<str:codigo>/', webapp_views.eliminar_categoria_libros,
                       name='eliminar_categoria_libros'),
                  path('asociar-libro-categoria/', webapp_views.asociar_libro_categoria, name='asociar_libro_categoria'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
              + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)


handler404 = custom_404_view
