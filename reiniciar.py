import sqlite3

def crear_bd():
    archivo_bd = "sistema_escolar.db"
    
    conexion = sqlite3.connect(archivo_bd)
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alumnos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        grado TEXT NOT NULL,
        correo_maestra TEXT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS padres (
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
    print("Base de datos y estructuras creadas con exito.")

if __name__ == "__main__":
    crear_bd()

