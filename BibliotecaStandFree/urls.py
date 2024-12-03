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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', webapp_views.index, name='index'),
    path('cartas/', webapp_views.index_cartas, name='index_cartas'),
    path('libros/', webapp_views.index_libros, name='index_libros'),
    path('login/', webapp_views.index_login, name='index_login'),
    path('register/', webapp_views.index_register, name='index_register'),
    path('carrito/', webapp_views.index_carrito, name='index_carrito'),
    path('contacto/', webapp_views.index_contacto, name='index_contacto'),
    path('carrito/agregar/<str:producto_id>/<str:tipo_producto>/', webapp_views.agregar_al_carrito,
         name='agregar_al_carrito'),
    path('carrito/eliminar/<str:producto_id>/<str:tipo_producto>/', webapp_views.eliminar_del_carrito,
         name='eliminar_del_carrito'),

]
