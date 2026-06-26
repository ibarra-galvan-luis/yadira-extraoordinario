import cv2
import sqlite3
import smtplib
import time  
from email.mime.text import MIMEText
from deepface import DeepFace

CORREO_EMISOR = "baryplox@gmail.com"
PASSWORD_EMISOR = "aqui pues era mi clave pero la quite"

def enviar_notificacion(nombre_padre, nombre_alumno, grado_alumno, correo_maestra_destino):
    """Envia un correo automatico a la maestra"""
    asunto = f" ALERTA DE SALIDA: Tutor de {nombre_alumno} en camino"
    cuerpo_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px;">
        <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border: 1px solid #e0e0e0;">
            <div style="background-color: #1a365d; padding: 20px; text-align: center; color: #ffffff;">
                <h2 style="margin: 0; font-size: 20px; letter-spacing: 1px;">Control Escolar</h2>
                <p style="margin: 5px 0 0 0; font-size: 13px; color: #cbd5e1;">Notificación de logistica en tiempo real</p>
            </div>
            <div style="padding: 25px; color: #334155; line-height: 1.6;">
                <p style="font-size: 16px; margin-top: 0;">Estimad@ docente,</p>
                <p style="font-size: 15px;">Se le informa que un Padre o Tutor autorizado ha ingresado a la zona de recogida vehicular:</p>
                <div style="background-color: #f8fafc; border-left: 4px solid #3182ce; padding: 15px; margin: 20px 0; border-radius: 0 4px 4px 0;">
                    <p style="margin: 5px 0;"><strong>Tutor:</strong> {nombre_padre}</p>
                    <p style="margin: 5px 0;"><strong>Alumno:</strong> {nombre_alumno}</p>
                    <p style="margin: 5px 0;"><strong>Grado:</strong> {grado_alumno}</p>
                </div>
                <p style="font-size: 14px; color: #475569; background-color: #fef3c7; padding: 10px; border-radius: 4px; text-align: center; font-weight: bold;">
                Por favor, solicite al alumno que se dirija al area de abordaje.
                </p>
            </div>
            <div style="background-color: #f1f5f9; padding: 12px; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0;">
            </div>
        </div>
    </body>
    </html>
    """
    msg = MIMEText(cuerpo_html, 'html', 'utf-8')
    msg['Subject'] = asunto
    msg['From'] = CORREO_EMISOR
    msg['To'] = correo_maestra_destino

    try:
        server = smtplib.SMTP('74.125.142.108', 587)
        server.starttls()
        server.login(CORREO_EMISOR, PASSWORD_EMISOR)
        server.sendmail(CORREO_EMISOR, correo_maestra_destino, msg.as_string())
        server.close()
        print(f" Correo de aviso nviado con exito a {correo_maestra_destino}.")
    except Exception as e:
        print(f"Error al enviar: {e}")


def obtener_padres_bd():
    conexion = sqlite3.connect("sistema_escolar.db")
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT padres.nombre, padres.foto_ruta, alumnos.nombre, alumnos.grado, alumnos.correo_maestra
        FROM padres 
        JOIN alumnos ON padres.alumno_id = alumnos.id
    """)
    filas = cursor.fetchall()
    conexion.close()
    return filas

def iniciar_sistema():
    video_capture = cv2.VideoCapture(0)
    video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 1) 
    print("Camara del estacionamiento iniciada...")
    
    padres_notificados = set()
    contador_cuadros = 0
    
    mensaje_original = "Acerquese a la camara para registrar su llegada, le recomendamos que no tenga nada en la cara que pueda obstruir con la deteccion"
    texto_pantalla = mensaje_original
    color_texto = (255, 255, 255)
    tiempo_deteccion = 0  
    alguien_detectado = False 

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        contador_cuadros += 1
        
        if not alguien_detectado and contador_cuadros % 15 == 0:
            lista_padres = obtener_padres_bd()
            frame_pequeno = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            
            for nombre_p, ruta_foto, nombre_a, grado, correo_m in lista_padres:
                if nombre_p in padres_notificados:
                    continue

                try:
                    resultado = DeepFace.verify(
                        img1_path = frame_pequeno, 
                        img2_path = ruta_foto, 
                        model_name = "VGG-Face", 
                        enforce_detection = False
                    )

                    if resultado["verified"]:
                        print(f"¡Match! Padre: {nombre_p}")
                        enviar_notificacion(nombre_p, nombre_a, grado, correo_m)
                        padres_notificados.add(nombre_p)
                        
                
                        texto_pantalla = f"Hola {nombre_p}! Avisando a la maestra de {nombre_a}"
                        color_texto = (0, 255, 0)
                        tiempo_deteccion = time.time()  
                        alguien_detectado = True
                        break

                except Exception as e:
                    pass 

      
        if alguien_detectado:
            if time.time() - tiempo_deteccion > 5:
                texto_pantalla = mensaje_original
                color_texto = (255, 255, 255) 
                alguien_detectado = False 

      
        alto, ancho, _ = frame.shape
        cv2.rectangle(frame, (0, alto - 60), (ancho, alto), (0, 0, 0), -1)
        cv2.putText(frame, texto_pantalla, (20, alto - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_texto, 2, cv2.LINE_AA)

        cv2.imshow('Pantalla Estacionamiento - Control Escolar', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    iniciar_sistema()

