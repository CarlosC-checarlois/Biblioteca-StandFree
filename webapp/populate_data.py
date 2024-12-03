import os
import sys
import django
from faker import Faker
import random

# Agregar el directorio raíz del proyecto al sistema PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BibliotecaStandFree.settings')
django.setup()

from webapp.models import Libro, LibroCategoria, LibrosXLibreriaCategoria, Carta, CartaCategoria, RelCartaCategoria

# Instancia de Faker
faker = Faker()

# Crear categorías de libros
def create_libro_categorias():
    categorias = ['Ficción', 'Ciencia', 'Historia', 'Fantasía', 'Biografía', 'Infantil', 'Romance', 'Misterio']
    for categoria in categorias:
        LibroCategoria.objects.get_or_create(
            libxcatCodigo=faker.unique.lexify(text='LBCAT???'),
            libxcatNombre=categoria
        )
    print(f'{len(categorias)} categorías de libros creadas.')

# Crear libros
def create_libros(num_libros=50):
    categorias = list(LibroCategoria.objects.all())
    for _ in range(num_libros):
        libro = Libro.objects.create(
            libCodigo=faker.unique.lexify(text='LIB???'),
            libNombre=faker.sentence(nb_words=4),
            libAutor=faker.name(),
            libFechaPublicacion=faker.date_between(start_date='-50y', end_date='today'),
            libVolumen=random.randint(1, 5),
            libSinopsis=faker.text(max_nb_chars=255),
            libURLLibro=faker.url(),
            libFoto=faker.image_url(),  # Cambiar si usas imágenes locales
            libStatus=random.choice([True, False]),
            libPrecio=round(random.uniform(5.0, 100.0), 2),  # Precio aleatorio entre 5 y 100
        )
        print(libro)
        # Asignar categorías aleatorias al libro
        if categorias:
            num_categorias = random.randint(1, 2)  # Cada libro puede tener 1-2 categorías
            for _ in range(num_categorias):
                categoria = random.choice(categorias)
                LibrosXLibreriaCategoria.objects.get_or_create(libro=libro, categoria=categoria)
    print(f'{num_libros} libros creados.')

    categorias = list(LibroCategoria.objects.all())
    for _ in range(num_libros):
        libro = Libro.objects.create(
            libCodigo=faker.unique.lexify(text='LIB???'),
            libNombre=faker.sentence(nb_words=4),
            libAutor=faker.name(),
            libFechaPublicacion=faker.date_between(start_date='-50y', end_date='today'),
            libVolumen=random.randint(1, 5),
            libSinopsis=faker.text(max_nb_chars=255),
            libURLLibro=faker.url(),
            libFoto=faker.image_url(),  # Cambiar si usas imágenes locales
            libStatus=random.choice([True, False]),
            libPrecio=round(random.uniform(5.0, 100.0), 2),  # Asignar precio aleatorio entre 5 y 100
        )
        # Asignar categorías aleatorias al libro
        if categorias:
            num_categorias = random.randint(1, 2)  # Cada libro puede tener 1-2 categorías
            for _ in range(num_categorias):
                categoria = random.choice(categorias)
                LibrosXLibreriaCategoria.objects.get_or_create(libro=libro, categoria=categoria)
    print(f'{num_libros} libros creados.')

# Crear categorías de productos de carta
def create_carta_categorias():
    categorias = ['Café', 'Té', 'Postres', 'Snacks', 'Bebidas Frías']
    for categoria in categorias:
        CartaCategoria.objects.get_or_create(
            carxcatCodigo=faker.unique.lexify(text='CARCAT???'),
            carxcatNombre=categoria,
            carxcatStatus=random.choice(['ACT', 'INA'])
        )
    print(f'{len(categorias)} categorías de carta creadas.')

# Crear productos de carta
def create_cartas(num_cartas=50):
    categorias = list(CartaCategoria.objects.filter(carxcatStatus='ACT'))  # Solo categorías activas
    for _ in range(num_cartas):
        carta = Carta.objects.create(
            carCodigo=faker.unique.lexify(text='CAR???'),
            carNombre=faker.sentence(nb_words=3),
            carDescripcion=faker.text(max_nb_chars=255),
            carPrecio=round(random.uniform(1.0, 50.0), 2),
            carFoto=faker.image_url(),  # Cambiar si usas imágenes locales
            carStatus_1=random.choice(['ACT', 'INA']),
        )
        # Asignar categorías aleatorias al producto
        if categorias:
            num_categorias = random.randint(1, 2)  # Cada producto puede tener 1-2 categorías
            for _ in range(num_categorias):
                categoria = random.choice(categorias)
                RelCartaCategoria.objects.get_or_create(carta=carta, categoria=categoria)
    print(f'{num_cartas} productos de carta creados.')

# Ejecutar los scripts de generación
def run():
    print('Creando datos falsos...')
    create_libro_categorias()
    create_libros(num_libros=50)  # Genera 50 libros
    create_carta_categorias()
    create_cartas(num_cartas=50)  # Genera 50 productos de carta
    print('Datos falsos creados exitosamente.')

if __name__ == '__main__':
    run()
