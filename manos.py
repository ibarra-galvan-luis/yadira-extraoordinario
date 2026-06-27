import cv2
import mediapipe as mp

mp_manos = mp.solutions.hands
mp_dibujo = mp.solutions.drawing_utils

manos = mp_manos.Hands(max_num_hands=2, min_detection_confidence=0.7)

camara = cv2.VideoCapture(1)
puntas_dedos = [4, 8, 12, 16, 20]

while True:
    exito, fotograma = camara.read()
    if not exito:
        break

    fotograma = cv2.flip(fotograma, 1)
    color_rgb = cv2.cvtColor(fotograma, cv2.COLOR_BGR2RGB)
    resultados = manos.process(color_rgb)

    total_dedos = 0

    if resultados.multi_hand_landmarks and resultados.multi_handedness:
        for indice, marcas_mano in enumerate(resultados.multi_hand_landmarks):
            lista_puntos = []
            for lm in marcas_mano.landmark:
                alto, ancho, _ = fotograma.shape
                cx, cy = int(lm.x * ancho), int(lm.y * alto)
                lista_puntos.append((cx, cy))

            dedos = []
            lado_mano = resultados.multi_handedness[indice].classification[0].label

            if lado_mano == "Left":
                if lista_puntos[4][0] < lista_puntos[3][0]:
                    dedos.append(1)
                else:
                    dedos.append(0)
            else:
                if lista_puntos[4][0] > lista_puntos[3][0]:
                    dedos.append(1)
                else:
                    dedos.append(0)

            for id in range(1, 5):
                if (
                    lista_puntos[puntas_dedos[id]][1]
                    < lista_puntos[puntas_dedos[id] - 2][1]
                ):
                    dedos.append(1)
                else:
                    dedos.append(0)

            total_dedos += dedos.count(1)

            mp_dibujo.draw_landmarks(
                fotograma, marcas_mano, mp_manos.HAND_CONNECTIONS
            )

    cv2.putText(
        fotograma,
        f"Dedos: {total_dedos}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,
        (0, 255, 0),
        3,
    )

    cv2.imshow("Detector de Dedos", fotograma)

    if cv2.waitKey(1) & 0xFF == 27:
        break

camara.release()
cv2.destroyAllWindows()
