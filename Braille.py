import cv2               # Librería para visión por computadora, usada para capturar y mostrar imágenes.
import easyocr           # Librería para reconocimiento óptico de caracteres (OCR).
import serial            # Librería para comunicación con Arduino por puerto serial.
import time              # Librería para manejar tiempos y pausas.

# Función que convierte una cadena de texto a una lista de caracteres en Braille codificados en binario
def convertir_a_braille(texto):
    # Diccionario con los caracteres y su representación en Braille como cadenas de 6 bits
    braille_dict = {
        'a': '100000', 'b': '110000', 'c': '100100', 'd': '100110',
        'e': '100010', 'f': '110100', 'g': '110110', 'h': '110010',
        'i': '010100', 'j': '010110', 'k': '101000', 'l': '111000',
        'm': '101100', 'n': '101110', 'ñ': '110111', 'o': '101010', 'p': '111100',
        'q': '111110', 'r': '111010', 's': '011100', 't': '011110',
        'u': '101001', 'v': '111001', 'w': '010111', 'x': '101101',
        'y': '101111', 'z': '101011',
        '1': '100000', '2': '110000', '3': '100100', '4': '100110',
        '5': '100010', '6': '110100', '7': '110110', '8': '110010',
        '9': '010100', '0': '010110',
        '#': '001111',  # Símbolo Braille que indica que sigue una secuencia numérica
        '.': '010011', ',': '010000', ':': '010010',
        ' ': '000000',  # Espacio representado por celda vacía en Braille
        'á': '111110', 'é': '011101', 'í': '001100', 'ó': '001101', 'ú': '011111'
    }

    braille_text = []    # Lista donde se almacenará la traducción completa a Braille
    en_numero = False    # Bandera que indica si estamos dentro de una secuencia de números

    # Recorremos cada carácter del texto original
    for letra in texto:
        letra = letra.lower()  # Convertimos a minúsculas para coincidir con el diccionario

        if letra.isdigit():  # Si el carácter es un número
            if not en_numero:
                braille_text.append(braille_dict['#'])  # Agregamos símbolo de número solo una vez
                en_numero = True
            braille_text.append(braille_dict[letra])   # Agregamos el dígito traducido a Braille
        else:
            en_numero = False  # Ya no estamos en una secuencia numérica
            if letra in braille_dict:
                braille_text.append(braille_dict[letra])  # Agregamos letra en Braille
            else:
                braille_text.append('000000')  # Carácter desconocido, celda vacía

    return braille_text  # Devolvemos la lista de caracteres Braille



# Inicializamos el lector OCR con soporte en inglés y español
reader = easyocr.Reader(['en', 'es'], gpu=False)

# Iniciamos la cámara (índice 0 por defecto)
cap = cv2.VideoCapture(0)

print("Presiona 's' para tomar una foto y analizar el texto.")
print("Presiona 'q' para salir sin capturar.")

captured = False  # Bandera para saber si se ha capturado una imagen

# Bucle que muestra la imagen en vivo de la cámara hasta que se presione una tecla
while True:
    ret, frame = cap.read()  # Capturamos un fotograma
    if not ret:
        print("Error al acceder a la cámara.")
        break

    # Mostramos la imagen en una ventana
    cv2.imshow("Presiona 's' para capturar", frame)
    key = cv2.waitKey(1) & 0xFF  # Esperamos por la tecla presionada

    if key == ord('s'):  # Si se presiona 's', se guarda la imagen y se rompe el bucle
        captured = True
        image = frame.copy()
        break
    elif key == ord('q'):  # Si se presiona 'q', salimos sin capturar
        break

cap.release()              # Liberamos la cámara
cv2.destroyAllWindows()    # Cerramos todas las ventanas abiertas de OpenCV

# Si se capturó una imagen, iniciamos el procesamiento OCR
if captured:
    results = reader.readtext(image)  # Aplicamos OCR a la imagen capturada

    print("\nTexto detectado en la imagen:\n")

    boxes = []     # Lista para almacenar coordenadas de las cajas delimitadoras
    words = []     # Lista para almacenar las palabras detectadas

    # Iteramos por cada resultado del OCR (caja, texto, probabilidad)
    for bbox, text, prob in results:
        print(f"→ \"{text}\" (confianza: {prob:.2f})")

        (top_left, _, bottom_right, _) = bbox  # Obtenemos coordenadas de la caja
        top_left = tuple(map(int, top_left))   # Convertimos a enteros
        bottom_right = tuple(map(int, bottom_right))

        padding = 10  # Margen extra alrededor de cada palabra
        top_left = (top_left[0] - padding, top_left[1] - padding)
        bottom_right = (bottom_right[0] + padding, bottom_right[1] + padding)

        boxes.append([top_left, bottom_right])  # Guardamos coordenadas
        words.append(text)                      # Guardamos palabra

        # Dibujamos un rectángulo y el texto en la imagen
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
        cv2.putText(image, text, (top_left[0], top_left[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

    # Agrupamos las palabras por líneas según su posición vertical
    grouped_lines = []
    current_line = []
    prev_bottom = -1
    line_height_threshold = 20  # Umbral para considerar si una palabra está en la misma línea

    for i in range(len(boxes)):
        top_left, bottom_right = boxes[i]
        if prev_bottom == -1 or top_left[1] - prev_bottom < line_height_threshold:
            current_line.append(words[i])
        else:
            grouped_lines.append(' '.join(current_line))
            current_line = [words[i]]
        prev_bottom = bottom_right[1]

    if current_line:
        grouped_lines.append(' '.join(current_line))

    print("\nFrases completas detectadas:")

    # Redimensionamos la imagen si es muy grande, para mostrarla mejor
    height, width = image.shape[:2]
    max_width = 900
    if width > max_width:
        scale = max_width / width
        image = cv2.resize(image, (int(width * scale), int(height * scale)))

    # Mostramos la imagen con texto antes de comenzar a enviar al Arduino
    cv2.imshow("Texto detectado", image)
    print("\nMostrando texto detectado...")

    cv2.waitKey(1)      # Refresca la ventana
    time.sleep(2)       # Esperamos 2 segundos antes de continuar

    # Iniciamos comunicación serial con Arduino
    arduino = serial.Serial('COM4', 9600, timeout=1)
    time.sleep(2)       # Esperamos que se estabilice la conexión

    # Recorremos cada línea detectada de texto
    for i, line in enumerate(grouped_lines):
        print(f"Renglón {i + 1}: {line}")
        braille_result = convertir_a_braille(line)  # Convertimos línea a Braille
        print(f"→ Braille: {braille_result}")

        # Enviamos cada carácter Braille al Arduino
        for braille_char in braille_result:
            arduino.write((braille_char + '\n').encode())  # Enviamos por serial
            print(f"Enviado al Arduino: {braille_char}")
            time.sleep(2)  # Esperamos 2 segundos entre letras

    arduino.close()  # Cerramos la conexión serial

    print("\nCierra la ventana para finalizar.")
    cv2.waitKey(0)   # Esperamos que el usuario cierre la ventana
    cv2.destroyAllWindows()  # Cerramos la ventana final
