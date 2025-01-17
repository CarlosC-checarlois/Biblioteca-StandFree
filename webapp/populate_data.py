import re


def transform_sql_file(input_file: str, output_file: str):
    """
    Transforma un archivo SQL de SQLite a PostgreSQL, cambiando:
    1. Eliminando comillas dobles de los nombres de las tablas.
    2. Agregando el prefijo 'public.' a los nombres de las tablas en los comandos INSERT INTO.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            sql_content = infile.read()

        # Expresión regular para encontrar y transformar los nombres de las tablas en INSERT INTO
        table_pattern = re.compile(r'INSERT INTO\s+"([^"]+)"', re.IGNORECASE)

        # Reemplazar las tablas con el prefijo 'public.' y sin comillas dobles
        transformed_sql = table_pattern.sub(lambda match: f'INSERT INTO public.{match.group(1)}', sql_content)

        # Guardar el resultado en un nuevo archivo
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write(transformed_sql)

        print(f"Transformación completada. Archivo guardado en: {output_file}")

    except FileNotFoundError:
        print(f"El archivo {input_file} no se encontró. Verifica el path e inténtalo nuevamente.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")


# Ejemplo de uso
if __name__ == "__main__":
    # Ruta de entrada y salida
    input_file = r"C:\Users\Carlos\Desktop\Variados\Portafolio\BibliotecaStandFreeDjango\BibliotecaStandFree\SQL_DATA_DJANGO_DUMP.sql"
    output_file = r"C:\Users\Carlos\Desktop\Variados\Portafolio\BibliotecaStandFreeDjango\BibliotecaStandFree\SQL_DATA_DJANGO_DUMP_TRANSFORMED.sql"

    # Llamar a la función de transformación
    transform_sql_file(input_file, output_file)
