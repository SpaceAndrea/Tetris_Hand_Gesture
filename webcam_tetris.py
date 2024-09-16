import cv2
from time import sleep
import pyautogui

'''
Step per il codice:
1) Apro la webcam e catturo i frame
2) Divido il frame della webcam in quattro sezioni, così da poter poi implementare diversi output per sezioni
3) Rilevo la mano utilizzando un modello Haar Cascade consigliato dal prof:
    -Hand.xml --> Buona rilevazione dei pugni, pochi falsi positivi
    -Fist.xml --> Il migliore nel rilevare i pugni, ma troppi falsi positivi troppo spesso
    -Palm.xml --> Troppi falsi positivi, rileva bene i palmi della mano ma rileva anche troppi dettagli del volto
Opto per Hand.xml
4) Determinare in quale sezione si trova la mano rilevata, in base alla posizione avrò un preciso comando su Tetris
5) Metto una soglia di treshold al centro per cercare di ridurre possibili output involtari
    (cioè se il pugno si trovasse al centro dello schermo, tutti gli output partirebbero insieme)    
'''

# FRAMES_PER_SECOND = 10

# Carica il modello Haar Cascade per il rilevamento della mano
# Assicurati di avere il file 'hand.xml' nella stessa directory o fornisci il percorso corretto
hand_cascade = cv2.CascadeClassifier('hand.xml') #cv2.CascadeClassifier carica il classificatore Haar Cascade
# hand_cascade = cv2.CascadeClassifier('fist.xml')
# hand_cascade = cv2.CascadeClassifier('palm.xml')

# Verifica se il modello è stato caricato correttamente
if hand_cascade.empty():
    print("Errore nel caricamento del modello Haar Cascade per la mano")
    exit()

zones = {
    "Sei nella zona in alto a sinistra": "left",
    "Sei nella zona in alto a destra": "down",
    "Sei nella zona in basso a sinistra": "right",
    "Sei nella zona in basso a destra": "up"
}

# Apri la webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Errore nell'apertura della videocamera")
    exit()

# Definisci il font per il testo
font = cv2.FONT_HERSHEY_SIMPLEX

while True:
    #ret = boolean che indica se lettura del frame è riuscita
    #frame = l'immagine stessa della webcam
    ret, frame = cap.read()
    if not ret:
        print("Errore nella lettura del frame")
        break

    # Ottieni le dimensioni del frame

    #Come funziona frame.shape[:2]?
    #Permette di ottenere l'altezza e la larghezza, in questo caso, del frame.
    #Infatti frame.shape restituisce una tupla contenente le dimensioni dell'immagine: altezza, larghezza, canali.
    height, width = frame.shape[:2]

    # Disegna le linee per dividere il frame in quattro sezioni
    # Linea verticale
    #cv2.line --> disegna una linea sull'immagine:
        #-frame: immagine su cui disegnare
        #-(width // 2, 0): punto di partenza della linea verticale (centro orizzontale superiore)
        #-(width // 2, height): punti di arrivo della linea verticale (centro orizzontale inferiore)
        #-(0, 255, 0): colore linea
        #-2: spessore linea
    cv2.line(frame, (width // 2, 0), (width // 2, height), (0, 255, 0), 2)
    # Linea orizzontale
    cv2.line(frame, (0, height // 2), (width, height // 2), (0, 255, 0), 2)

    # Definisci la zona centrale di thresholding
    threshold_ratio = 0.25  # 25% del frame per la zona centrale
    threshold_width = int(width * threshold_ratio)
    threshold_height = int(height * threshold_ratio)
    #coordinate angolo superiore sinistro
    top_left_threshold = (width // 2 - threshold_width // 2, height // 2 - threshold_height // 2)
    #coordinate angolo inferiore destro
    bottom_right_threshold = (width // 2 + threshold_width // 2, height // 2 + threshold_height // 2)
    # Disegna la zona centrale
    cv2.rectangle(frame, top_left_threshold, bottom_right_threshold, (255, 0, 0), 2)

    # Converti il frame in scala di grigi
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Rileva le mani nel frame
    #scaleFactor=1.1: Specifica quanto ridurre le dimensioni dell'immagine --> 10% ogni volta
        #^^^--> in altre parole, il modello ha di base un valore prefissato con cui si è allenato, ciò significa che le mani vengono 
        #rilevate a quella dimensione se trovate. Però, se viene ridotta la dimensione del frame, è possibile che l'algoritmo detecta di +
    #minNeighbors: Specifica quante volte una finestra deve essere rilevata vicina per mantenere la rivelazione
        #valori + alti riducono falsi positivi

    hands = hand_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    # Inizializza una lista per memorizzare i messaggi da stampare
    messages = []

    # Disegna rettangoli attorno alle mani rilevate e determina la zona
    for (x, y, w, h) in hands:
        # Disegna il rettangolo intorno alla mano
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Calcola il centro del rettangolo
        center_x = x + w // 2
        center_y = y + h // 2

        # # Verifica se il centro è all'interno della zona centrale di thresholding
        # if (top_left_threshold[0] <= center_x <= bottom_right_threshold[0] and
        #     top_left_threshold[1] <= center_y <= bottom_right_threshold[1]):
        #     # Se il centro è nella zona centrale, ignora questa rilevazione
        #     continue

        # Determina in quale sezione si trova il centro
        if center_x < width // 2 and center_y < height // 2:
            zone = "Sei nella zona in alto a sinistra"
        elif center_x >= width // 2 and center_y < height // 2:
            zone = "Sei nella zona in alto a destra"
        elif center_x < width // 2 and center_y >= height // 2:
            zone = "Sei nella zona in basso a sinistra"
        else:
            zone = "Sei nella zona in basso a destra"
        messages.append(zone)

    # Rimuovi i duplicati nei messaggi
    messages = list(set(messages))

    # Stampa i messaggi sulla console
    for message in messages:
        if zone in zones:
            key = zones[zone]
            print(f"Simulazione pressione tasto: {key}") #debug
            if key == "left":
                pyautogui.press('left')
            elif key == "right":
                pyautogui.press('right')
            elif key == "down":
                pyautogui.press('down')
            elif key == "up":
                sleep(0.1)
                pyautogui.press('up')
        # print(message)

    # Opzionale: visualizza i messaggi sul frame
    for idx, message in enumerate(messages):
        cv2.putText(frame, message, (10, 30 + idx * 30), font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

    # Mostra il frame
    cv2.imshow('Rilevamento Mano', frame)

    # Esci premendo 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # sleep(1.0 / FRAMES_PER_SECOND)
# Rilascia la videocamera e chiudi tutte le finestre
cap.release()
cv2.destroyAllWindows()
