import cv2
import numpy as np

# Carica il modello Haar Cascade per il rilevamento della mano
# Assicurati di avere il file 'hand.xml' nella stessa directory o fornisci il percorso corretto
hand_cascade = cv2.CascadeClassifier('hand.xml')
# hand_cascade = cv2.CascadeClassifier('fist.xml')
# hand_cascade = cv2.CascadeClassifier('palm.xml')
# Verifica se il modello è stato caricato correttamente
if hand_cascade.empty():
    print("Errore nel caricamento del modello Haar Cascade per la mano")
    exit()

# Apri la webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Errore nell'apertura della videocamera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Errore nella lettura del frame")
        break

    # Ottieni le dimensioni del frame
    height, width = frame.shape[:2]

    # Disegna le linee per dividere il frame in quattro sezioni
    # Linea verticale
    cv2.line(frame, (width // 2, 0), (width // 2, height), (0, 255, 0), 2)
    # Linea orizzontale
    cv2.line(frame, (0, height // 2), (width, height // 2), (0, 255, 0), 2)

    # Converti il frame in scala di grigi
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #-------------------------------------------------
    #Possibili miglioramenti

    #Dopo la conversione in scala di grigi, provo ad applicare l'otsu tresholding
    avg = np.mean(gray)
    flag = cv2.THRESH_BINARY_INV if avg > 200 else cv2.THRESH_BINARY

    #Continuo applicando Guassian Blur per poi effettuare il tresholding
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    _, otsu = cv2.threshold(blur, 0, 255, flag + cv2.THRESH_OTSU)

    #Tentativo 1:
    #Aggiunta: al posto di var "frame" uso var "otsu": pugno trovato raramente, forse scarsa illuminazione?
    
    #Tentativo 2: applico la chiusura per migliorare i bordi
    kernel = np.ones((5, 5), np.uint8)  # Kernel per operazioni morfologiche
    otsu = cv2.morphologyEx(otsu, cv2.MORPH_CLOSE, kernel)

    # cv2.imshow('Otsu\'s Threshold Blurred', otsu)
    # Rilevazione mani ancora poco efficace, possibile problema di scarsa illuminazione.

    #Tentativo 3: Testare con Sobel e Canny
    # Processare con Sobel per la Edge Detection
    # Calcolare i gradienti con cv.Sobel
    gradients = [cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3),
                 cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3),]
    
    # cv2.imshow('Sobel X', gradients[0])
    # cv2.imshow('Sobel Y', gradients[1])

    # Calcolare la magnitudine e la direzione del gradiente
    gradient = np.sqrt(gradients[0]**2 + gradients[1]**2)
    gradient = cv2.convertScaleAbs(gradient)
    canny = cv2.Canny(gray, 100, 200)
    # cv2.imshow('Sobel', gradient)
    # cv2.imshow('Canny', canny)

    #-------------------------------------------------


    # Rileva le mani nel frame
    hands = hand_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10)

    # Disegna rettangoli attorno alle mani rilevate
    for (x, y, w, h) in hands:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # Mostra il frame
    cv2.imshow('Rilevamento BASE Mano', frame)


    # Rileva le mani nel frame
    hands = hand_cascade.detectMultiScale(otsu, scaleFactor=1.1, minNeighbors=5)

    # Disegna rettangoli attorno alle mani rilevate
    for (x, y, w, h) in hands:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # Mostra il frame
    cv2.imshow('Rilevamento OTSU Mano', frame)
    
    # Rileva le mani nel frame
    hands = hand_cascade.detectMultiScale(gradient, scaleFactor=1.1, minNeighbors=5)

    # Disegna rettangoli attorno alle mani rilevate
    for (x, y, w, h) in hands:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # Mostra il frame
    cv2.imshow('Rilevamento SOBEL Mano', frame)

    # Rileva le mani nel frame
    hands = hand_cascade.detectMultiScale(canny, scaleFactor=1.1, minNeighbors=5)

    # Disegna rettangoli attorno alle mani rilevate
    for (x, y, w, h) in hands:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # Mostra il frame
    cv2.imshow('Rilevamento CANNY Mano', frame)

    # Esci premendo 'esc'
    if cv2.waitKey(1) == 27:
        break

# Rilascia la videocamera e chiudi tutte le finestre
cap.release()
cv2.destroyAllWindows()
