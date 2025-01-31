from django import forms
from webapp.models import Carta,Libro


class CartaForm(forms.ModelForm):
    class Meta:
        model = Carta
        fields = ['carCodigo', 'carNombre', 'carCantidad', 'carDescripcion', 'carPrecio', 'carFoto', 'carStatus']
        widgets = {
            'carCodigo': forms.TextInput(attrs={'class': 'form-control'}),
            'carNombre': forms.TextInput(attrs={'class': 'form-control'}),
            'carCantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'carDescripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'carPrecio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'carFoto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'carStatus': forms.Select(choices=[('ACT', 'Activo'), ('FIN', 'Finalizado')],
                                      attrs={'class': 'form-control'}),
        }
        labels = {
            'carCodigo': 'Código del Producto',
            'carNombre': 'Nombre del Producto',
            'carCantidad': 'Cantidad Disponible',
            'carDescripcion': 'Descripción',
            'carPrecio': 'Precio',
            'carFoto': 'Imagen del Producto',
            'carStatus': 'Estado del Producto',
        }


class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['libCodigo', 'libNombre', 'libAutor', 'libCantidad', 'libFechaPublicacion',
                  'libVolumen', 'libSinopsis', 'libPrecio', 'libFoto', 'libURLLibro']
        widgets = {
            'libFechaPublicacion': forms.DateInput(attrs={'type': 'date'}),
            'libSinopsis': forms.Textarea(attrs={'rows': 4}),
        }
