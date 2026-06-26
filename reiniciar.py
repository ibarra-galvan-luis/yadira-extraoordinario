import sqlite3
import os

def limpiar_y_crear_bd():
    archivo_bd = "sistema_escolar.db"
    

    if os.path.exists(archivo_bd):
        try:
            os.remove(archivo_bd)
            print(" Base de datos vieja eliminada con exito.")
        except PermissionError:
            print("ERROR: Cierra los archivos 'main.py' o 'app.py' antes de ejecutar esto.")
            return

  
    conexion = sqlite3.connect(archivo_bd)
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE alumnos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        grado TEXT NOT NULL,
        correo_maestra TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE padres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_id INTEGER,
        nombre TEXT NOT NULL,
        correo TEXT NOT NULL,
        foto_ruta TEXT NOT NULL,
        FOREIGN KEY (alumno_id) REFERENCES alumnos (id) ON DELETE CASCADE
    )
    """)
    
    conexion.commit()
    conexion.close()
    print("Estructura de la base de datos creada desde cero con exito")

if __name__ == "__main__":
    limpiar_y_crear_bd()
