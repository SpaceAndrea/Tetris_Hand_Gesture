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

if __name__ == "__main__":

    # FRAMES_PER_SECOND = 10

    # Carico il modello Haar Cascade per il rilevamento della mano
    hand_cascade = cv2.CascadeClassifier('hand.xml')
    # hand_cascade = cv2.CascadeClassifier('fist.xml')
    # hand_cascade = cv2.CascadeClassifier('palm.xml')

    #Dizionario per le zone {chiave: valore}
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

    while True:
        #ret = boolean che indica se lettura del frame è riuscita
        #frame = l'immagine stessa della webcam
        ret, frame = cap.read()
        if not ret:
            print("Errore nella lettura del frame")
            break

        # Inverti (specchia) il frame orizzontalmente
        frame = cv2.flip(frame, 1)

        # Ottieni le dimensioni del frame

        #Come funziona frame.shape[:2]?
        #Permette di ottenere l'altezza e la larghezza, in questo caso, del frame.
        #Infatti frame.shape restituisce una tupla contenente le dimensioni dell'immagine: altezza, larghezza, canali.
        height, width = frame.shape[:2]

        # Disegna le linee per dividere il frame in quattro sezioni
        # Linea verticale
        #cv2.line --> disegna una linea sull'immagine:
            #-frame: immagine su cui disegnare
        #0,0 --> in alto a sinistra, quindi
                        #centro sopra       #centro sotto       #colore     #spessore
        cv2.line(frame, (width // 2, 0), (width // 2, height), (0, 255, 0), 2)
        # Linea orizzontale
                        #centro sinistra   #centro destra      #colore     #spessore
        cv2.line(frame, (0, height // 2), (width, height // 2), (0, 255, 0), 2)

        # Definisci la zona centrale di thresholding
        threshold_ratio = 0.25  # 25% del frame per la zona centrale
        threshold_width = int(width * threshold_ratio)
        threshold_height = int(height * threshold_ratio)
        #coordinate angolo superiore sinistro
                            #metà del frame - metà larghezza zona centrale, # same - metà lunghezza zona centrale
        top_left_threshold = (width // 2 - threshold_width // 2, height // 2 - threshold_height // 2)
        #coordinate angolo inferiore destro
        bottom_right_threshold = (width // 2 + threshold_width // 2, height // 2 + threshold_height // 2)
        # Disegna la zona centrale
        cv2.rectangle(frame, top_left_threshold, bottom_right_threshold, (255, 0, 0), 2)

        # Converti il frame in scala di grigi
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

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
        #x, y = coordinate angolo superiore sinistro rettangolo
        #w, h = larghezza e altezza rettangolo
        for (x, y, w, h) in hands:
            # Disegna il rettangolo intorno alla mano
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # Calcola il centro del rettangolo, rappresentando le coordinate relative al frame della webcam
            #Userò queste coordinate per determinare in quale delle quattro sezioni di frame si trova la mano rilevata
            center_x = x + w // 2
            center_y = y + h // 2

            # Verifica se il centro è all'interno della zona centrale di thresholding
            if (top_left_threshold[0] <= center_x <= bottom_right_threshold[0] and
                top_left_threshold[1] <= center_y <= bottom_right_threshold[1]):
                # Se il centro è nella zona centrale, ignora questa rilevazione
                continue

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
            if message in zones:
                key = zones[message]
                print(f"Simulazione pressione tasto: {key}") #debug
                if key == "left":
                    pyautogui.press('left')
                elif key == "right":
                    pyautogui.press('right')
                elif key == "down":
                    print("complimenti")
                    # pyautogui.press('down')
                elif key == "up":
                    # sleep(0.1)
                    pyautogui.press('up')
            # print(message)

        # Mostra il frame
        cv2.imshow('Rilevamento Mano', frame)

        # Esci premendo 'ESC'
        if cv2.waitKey(1) == 27:
            break

        # sleep(1.0 / FRAMES_PER_SECOND)
    # Rilascia la videocamera e chiudi tutte le finestre
    cap.release()
    cv2.destroyAllWindows()
