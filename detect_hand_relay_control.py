import cv2
import numpy as np
import serial
import time

# Configuração da porta serial
arduino = serial.Serial('COM5', 9600)  # Substitua 'COM5' pela sua porta serial
time.sleep(2)  # Atraso para a conexão ser estabelecida

# Ponto fixo na tela
fixed_point = (320, 240)  # Ponto central da tela (ajuste conforme necessário)
radius = 50  # Raio para detecção de proximidade

# Função para detectar a posição da mão
def detect_hand_movement(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Definindo intervalo de cor para a pele
    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)

    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) > 500:
            M = cv2.moments(largest_contour)
            if M['m00'] != 0:
                cX = int(M['m10'] / M['m00'])
                cY = int(M['m01'] / M['m00'])
                return (cX, cY)  # Retorna a posição (X, Y) do centro da mão
    return None  # Retorna None se não houver contornos

# Captura de vídeo
cap = cv2.VideoCapture(0
                       )
relay_active = False  # Estado do relé

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detectar a posição da mão
        hand_position = detect_hand_movement(frame)

        # Desenhar o ponto fixo na tela
        cv2.circle(frame, fixed_point, radius, (0, 255, 0), 2)  # Ponto fixo verde

        if hand_position is not None:
            # Desenhar a posição da mão
            cv2.circle(frame, hand_position, 10, (255, 0, 0), -1)  # Posição da mão em azul

            # Verifica se a mão está sobre o ponto fixo
            distance = np.linalg.norm(np.array(hand_position) - np.array(fixed_point))
            if distance < radius:
                if not relay_active:
                    print("Mão sobre o ponto fixo! Acionando o relé.")
                    arduino.write(b'1')  # Envia '1' para o Arduino para ligar o relé
                    relay_active = True  # Marca o relé como ativado
            else:
                if relay_active:
                    print("Mão fora do ponto fixo! Desligando o relé.")
                    arduino.write(b'0')  # Envia '0' para o Arduino para desligar o relé
                    relay_active = False  # Marca o relé como desativado

        cv2.imshow('Frame', frame)

        # Verifica se a tecla 'q' foi pressionada
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
    arduino.close()
