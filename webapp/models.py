from django.db import models


# **Categorías de Libros**
class LibroCategoria(models.Model):
    libxcatCodigo = models.CharField(max_length=7, primary_key=True)  # Código de la categoría
    libxcatNombre = models.CharField(max_length=150)  # Nombre de la categoría

    def __str__(self):
        return self.libxcatNombre


# **Libros**
class Libro(models.Model):
    libCodigo = models.CharField(max_length=7, primary_key=True)  # Código único del libro
    libNombre = models.CharField(max_length=150)  # Nombre del libro
    libAutor = models.CharField(max_length=150)  # Autor del libro
    libFechaPublicacion = models.DateField()  # Fecha de publicación
    libVolumen = models.IntegerField()  # Volumen del libro
    libSinopsis = models.TextField()  # Sinopsis del libro
    libURLLibro = models.URLField(blank=True, null=True)  # URL del libro (opcional)
    libFoto = models.ImageField(upload_to='libros/')  # Imagen del libro
    libStatus = models.BooleanField(default=True)  # Estado (activo/inactivo)
    libPrecio = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.libNombre


# **Relación Libros x Categorías**
class LibrosXLibreriaCategoria(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)  # Relación con Libro
    categoria = models.ForeignKey(LibroCategoria, on_delete=models.CASCADE)  # Relación con LibroCategoria

    class Meta:
        unique_together = ('libro', 'categoria')  # Evitar duplicados


# **Categorías de Carta**
class CartaCategoria(models.Model):
    carxcatCodigo = models.CharField(max_length=7, primary_key=True)  # Código de la categoría
    carxcatNombre = models.CharField(max_length=150)  # Nombre de la categoría
    carxcatStatus = models.CharField(max_length=3)  # Estado de la categoría

    def __str__(self):
        return self.carxcatNombre


# **Productos en la Carta**
class Carta(models.Model):
    carCodigo = models.CharField(max_length=7, primary_key=True)  # Código único del producto
    carNombre = models.CharField(max_length=150)  # Nombre del producto
    carDescripcion = models.TextField()  # Descripción del producto
    carPrecio = models.DecimalField(max_digits=9, decimal_places=2)  # Precio del producto
    carFoto = models.ImageField(upload_to='carta/')  # Imagen del producto
    carStatus_1 = models.CharField(max_length=3)  # Estado del producto

    def __str__(self):
        return self.carNombre


# **Relación Carta x Categorías**
class RelCartaCategoria(models.Model):
    carta = models.ForeignKey(Carta, on_delete=models.CASCADE)  # Relación con Carta
    categoria = models.ForeignKey(CartaCategoria, on_delete=models.CASCADE)  # Relación con CartaCategoria

    class Meta:
        unique_together = ('carta', 'categoria')  # Evitar duplicados


# **Carrito**
class Carrito(models.Model):
    carCodigo = models.CharField(max_length=7, primary_key=True)  # Código del carrito
    carSubtotal = models.DecimalField(max_digits=9, decimal_places=2)  # Subtotal sin IVA
    carIva = models.DecimalField(max_digits=9, decimal_places=2)  # IVA aplicado
    carTotal = models.DecimalField(max_digits=9, decimal_places=2)  # Total con IVA
    carStatus = models.CharField(max_length=3, default="ACT")  # Estado del carrito (ACT: Activo, FIN: Finalizado)

    def __str__(self):
        return f"Carrito {self.carCodigo} - Total: {self.carTotal}"


# **Relación Usuario x Carrito**
class Usuario(models.Model):
    usuCodigo = models.CharField(max_length=7, primary_key=True)  # Código del usuario
    usuNombre = models.CharField(max_length=255)  # Nombre completo
    usuApodo = models.CharField(max_length=150)  # Apodo del usuario
    usuCorreo = models.EmailField(unique=True)  # Correo electrónico
    usuClave = models.CharField(max_length=255)  # Contraseña
    usuStatus = models.CharField(max_length=3, default="ACT")  # Estado del usuario


    def __str__(self):
        return self.usuNombre


class UsuarioXCarrito(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="carritos")
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    usuxcarFechaModificacion = models.DateTimeField(auto_now=True)  # Fecha de modificación
    usuxcarStatus = models.CharField(max_length=3, default="ACT")  # Estado de la relación

    def __str__(self):
        return f"{self.usuario.usuNombre} - Carrito {self.carrito.carCodigo}"


# **Libros en Carrito**
class LibrosXCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name="libros")
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    libxcarCantidad = models.PositiveIntegerField()  # Cantidad del libro en el carrito
    libxcarTotal = models.DecimalField(max_digits=9, decimal_places=2)  # Total por este libro

    def __str__(self):
        return f"{self.libro.libNombre} x {self.libxcarCantidad}"


# **Carta en Carrito**
class CartaXCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name="carta")
    carta = models.ForeignKey(Carta, on_delete=models.CASCADE)
    carxcarCantidad = models.PositiveIntegerField()  # Cantidad del producto en la carta
    carxcarTotal = models.DecimalField(max_digits=9, decimal_places=2)  # Total por este producto

    def __str__(self):
        return f"{self.carta.carNombre} x {self.carxcarCantidad}"

