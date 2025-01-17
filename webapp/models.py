from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password


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
    libCantidad = models.IntegerField() # Cantidad de Libro
    libFechaPublicacion = models.DateField()  # Fecha de publicación
    libVolumen = models.IntegerField()  # Volumen del libro
    libSinopsis = models.TextField()  # Sinopsis del libro
    libURLLibro = models.URLField(blank=True, null=True)  # URL del libro (opcional)
    libFoto = models.ImageField(upload_to='libros/')  # Imagen del libro
    libStatus = models.CharField(max_length=3, default="ACT")
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
    carCantidad = models.IntegerField() # Cantidad del producto
    carDescripcion = models.TextField()  # Descripción del producto
    carPrecio = models.DecimalField(max_digits=9, decimal_places=2)  # Precio del producto
    carFoto = models.ImageField(upload_to='carta/')  # Imagen del producto
    carStatus = models.CharField(max_length=3, default="ACT")  # Estado del carrito (ACT: Activo, FIN: Finalizado)

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


class UsuarioManager(BaseUserManager):
    """Gestor personalizado para el modelo Usuario."""

    def create_user(self, usuCorreo, usuClave=None, **extra_fields):
        """Crea y devuelve un usuario común."""
        if not usuCorreo:
            raise ValueError(_("El correo electrónico es obligatorio."))
        usuCorreo = self.normalize_email(usuCorreo)
        extra_fields.setdefault("is_active", True)
        user = self.model(usuCorreo=usuCorreo, **extra_fields)
        if usuClave:  # Permitir usuarios sin contraseña (opcional)
            user.set_password(usuClave)
        else:
            raise ValueError(_("La contraseña es obligatoria."))
        user.save(using=self._db)
        return user

    def create_superuser(self, usuCorreo, usuClave=None, **extra_fields):
        """Crea y devuelve un superusuario."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("El superusuario debe tener is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("El superusuario debe tener is_superuser=True."))

        return self.create_user(usuCorreo, usuClave, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Modelo personalizado de Usuario que coincide con la tabla SQL proporcionada."""

    usuNombre = models.CharField(max_length=150, verbose_name=_("Nombre"))
    usuApellido = models.CharField(max_length=150, verbose_name=_("Apellido"), default="Sin Apellido")
    usuFechaNacimiento = models.DateField(verbose_name=_("Fecha de Nacimiento"), null=True, blank=True)
    usuGenero = models.CharField(
        max_length=1,
        choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')],
        verbose_name=_("Género"),
        null=True,
        blank=True
    )
    usuTelefono = models.CharField(max_length=15, verbose_name=_("Teléfono"), null=True, blank=True)
    email = models.EmailField(unique=True, verbose_name=_("Correo Electrónico"))
    password = models.CharField(max_length=255, verbose_name=_("Contraseña"))  # Usar 'password' como estándar
    usuApodo = models.CharField(max_length=150, null=True, blank=True, verbose_name=_("Apodo"))
    usuPreferenciaAnuncios = models.BooleanField(default=False, verbose_name=_("Preferencia por Anuncios"))
    usuStatus = models.CharField(
        max_length=3,
        choices=[("ACT", "Activo"), ("INA", "Inactivo")],
        default="ACT",
        verbose_name=_("Estado")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Activo"))
    is_staff = models.BooleanField(default=False, verbose_name=_("Miembro del personal"))
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    # Ajustar para usar el email como identificador principal
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["usuNombre", "usuApellido"]

    objects = UsuarioManager()

    class Meta:
        db_table = "webapp_usuario"  # Coincide con la tabla SQL
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")

    def __str__(self):
        return f"{self.usuNombre} {self.usuApellido}"

    def set_password(self, raw_password):
        """Encripta y asigna una contraseña."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verifica si la contraseña proporcionada coincide con la almacenada."""
        return check_password(raw_password, self.password)


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


class Contacto(models.Model):
    nombre = models.CharField(max_length=150, verbose_name="Nombre del Contacto")
    email = models.EmailField(verbose_name="Correo Electrónico")
    mensaje = models.TextField(verbose_name="Mensaje")
    fecha_envio = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Envío")

    def __str__(self):
        return f"Contacto de {self.nombre} - {self.email}"


