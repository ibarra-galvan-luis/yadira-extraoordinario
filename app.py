import streamlit as st
import sqlite3
import os

st.set_page_config(page_title="Control Escolar", page_icon="🎒", layout="centered")

def obtener_registros():
    conexion = sqlite3.connect("sistema_escolar.db")
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT alumnos.id, alumnos.nombre, alumnos.grado, alumnos.correo_maestra, padres.nombre, padres.foto_ruta
        FROM alumnos JOIN padres ON alumnos.id = padres.alumno_id
    """)
    datos = cursor.fetchall()
    conexion.close()
    return datos

def guardar_registro(nom_a, grado_a, corr_m, nom_p, corr_p, foto_nombre):
    conexion = sqlite3.connect("sistema_escolar.db")
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO alumnos (nombre, grado, correo_maestra) VALUES (?, ?, ?)", (nom_a, grado_a, corr_m))
    id_a = cursor.lastrowid
    cursor.execute("INSERT INTO padres (alumno_id, nombre, correo, foto_ruta) VALUES (?, ?, ?, ?)", (id_a, nom_p, corr_p, foto_nombre))
    conexion.commit()
    conexion.close()

def eliminar_registro(id_alumno, ruta_foto):
    """Borra al alumno, al padre y elimina la foto física de la carpeta"""
    conexion = sqlite3.connect("sistema_escolar.db")
    cursor = conexion.cursor()
    
    cursor.execute("DELETE FROM alumnos WHERE id = ?", (id_alumno,))
    conexion.commit()
    conexion.close()
    
    if os.path.exists(ruta_foto):
        try:
            os.remove(ruta_foto)
        except Exception:
            pass


st.title("Sistema de Control Escolar")
st.markdown("Plataforma de gestion de alumnos y Padres o Tutores para reconocimiento facial.")


pestaña1, pestaña2 = st.tabs(["Registrar Nuevo", "Alumnos Registrados"])

with pestaña1:
    st.header("Formulario de Registro")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Datos del Alumno")
        nombre_alumno = st.text_input("Nombre Completo del Alumno", placeholder="Ej. Carlos Pérez")
        grado_alumno = st.text_input("Grado y Grupo", placeholder="Ej. 3er Grado A")
        correo_maestra = st.text_input("Correo de la Maestra", placeholder="ejemplo@colegio.com")
        
    with col2:
        st.subheader("Datos del Tutor")
        nombre_padre = st.text_input("Nombre Completo del Tutor", placeholder="Ej. Juan Pérez")
        correo_padre = st.text_input("Correo del Tutor", placeholder="tutor@correo.com")
        foto_subida = st.file_uploader("Subir Fotografía para la IA", type=["jpg", "png", "jpeg"])

    if st.button("Guardar en la Base de Datos", type="primary"):
        if nombre_alumno and grado_alumno and correo_maestra and nombre_padre and foto_subida:
            nombre_archivo_foto = foto_subida.name
            with open(nombre_archivo_foto, "wb") as f:
                f.write(foto_subida.getbuffer())
            
            guardar_registro(nombre_alumno, grado_alumno, correo_maestra, nombre_padre, correo_padre, nombre_archivo_foto)
            st.success(f"{nombre_alumno} y su tutor han sido registrados.")
            st.rerun() 
        else:
            st.error(" Asegurate de llenar todos los campos obligatorios y subir una fotografia.")

with pestaña2:
    st.header("Lista de Familias en el Sistema")
    registros = obtener_registros()
    
    if registros:
        for reg in registros:
            id_a, nom_a, gra_a, cor_m, nom_p, foto_r = reg
            with st.container():
                st.markdown(f"###  Alumno: {nom_a} ({gra_a})")
                
                col_text, col_img, col_btn = st.columns([2, 1, 1])
                
                with col_text:
                    st.write(f"Tutor Autorizado: {nom_p}")
                    st.write(f"Envía alertas a:{cor_m}")
                
                with col_img:
                    if os.path.exists(foto_r):
                        st.image(foto_r, width=100, caption="Rostro IA")
                    else:
                        st.caption(" Foto no encontrada")
                
                with col_btn:
                    if st.button(" Eliminar", key=f"del_{id_a}", type="secondary"):
                        eliminar_registro(id_a, foto_r)
                        st.success(f"Eliminado correctamente.")
                        st.rerun()
                st.divider()
    else:
        st.info("No hay alumnos registrados todavía.")
