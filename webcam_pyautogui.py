import cv2
import time  # Importa il modulo time per la gestione della temporizzazione
import pyautogui  # Importa pyautogui per simulare le pressioni dei tasti

# Carica il modello Haar Cascade per il rilevamento della mano
hand_cascade = cv2.CascadeClassifier('hand.xml')

# Verifica se il modello è stato caricato correttamente
if hand_cascade.empty():
    print("Errore nel caricamento del modello Haar Cascade per la mano")
    exit()

# Apri la webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Errore nell'apertura della videocamera")
    exit()

desired_width = 640
desired_height = 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, desired_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, desired_height)

# Definisci il font per il testo
font = cv2.FONT_HERSHEY_SIMPLEX

# Definisci le zone possibili con i relativi comandi
# zones = {
#     "Sei nella zona in alto a sinistra": "left",    # Simula la pressione della freccia sinistra
#     "Sei nella zona in alto a destra": "down",    # Simula la pressione della freccia destra
#     "Sei nella zona in basso a sinistra": "right",   # Simula la pressione della freccia giù
#     "Sei nella zona in basso a destra": "up"        # Simula la pressione della freccia su (per ruotare)
# }

zones = {
    "Sei nella zona in alto a sinistra": "down",    # Simula la pressione della freccia sinistra
    "Sei nella zona in alto a destra": "up",    # Simula la pressione della freccia destra
    "Sei nella zona in basso a sinistra": "right",   # Simula la pressione della freccia giù
    "Sei nella zona in basso a destra": "left"        # Simula la pressione della freccia su (per ruotare)
}

# Inizializza un dizionario per tracciare l'ultimo tempo di comando per ogni zona
last_command_time = {zone: 0 for zone in zones}

# Definisci l'intervallo di tempo minimo tra i comandi (in secondi)
# command_interval = 0.5  # 0.5 secondi

while True:
    ret, frame = cap.read()
    if not ret:
        print("Errore nella lettura del frame")
        break

    # Ottieni le dimensioni del frame
    height, width = frame.shape[:2]

    # Disegna le linee per dividere il frame in quattro sezioni
    cv2.line(frame, (width // 2, 0), (width // 2, height), (0, 255, 0), 2)  # Linea verticale
    cv2.line(frame, (0, height // 2), (width, height // 2), (0, 255, 0), 2)  # Linea orizzontale

    # Definisci la zona centrale di thresholding
    threshold_ratio = 0.25  # 25% del frame per la zona centrale
    threshold_width = int(width * threshold_ratio)
    threshold_height = int(height * threshold_ratio)
    top_left_threshold = (width // 2 - threshold_width // 2, height // 2 - threshold_height // 2)
    bottom_right_threshold = (width // 2 + threshold_width // 2, height // 2 + threshold_height // 2)
    # Disegna la zona centrale
    cv2.rectangle(frame, top_left_threshold, bottom_right_threshold, (255, 0, 0), 2)

    # Converti il frame in scala di grigi
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Rileva le mani nel frame
    hands = hand_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    # Ottieni l'ora corrente
    current_time = time.time()

    # Lista per memorizzare i messaggi da stampare
    messages = []

    # Lista per tenere traccia delle zone rilevate in questo frame
    detected_zones = []

    # Rileva le mani e determina la zona
    for (x, y, w, h) in hands:
        # Disegna il rettangolo intorno alla mano
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Calcola il centro del rettangolo
        center_x = x + w // 2
        center_y = y + h // 2

        # Verifica se il centro è nella zona centrale di thresholding
        if (top_left_threshold[0] <= center_x <= bottom_right_threshold[0] and
            top_left_threshold[1] <= center_y <= bottom_right_threshold[1]):
            # Se è nel centro, ignora questa rilevazione
            continue

        # Determina in quale sezione si trova il centro della mano
        if center_x < width // 2 and center_y < height // 2:
            zone = "Sei nella zona in alto a sinistra"
        elif center_x >= width // 2 and center_y < height // 2:
            zone = "Sei nella zona in alto a destra"
        elif center_x < width // 2 and center_y >= height // 2:
            zone = "Sei nella zona in basso a sinistra"
        else:
            zone = "Sei nella zona in basso a destra"

        detected_zones.append(zone)

    # Rimuovi duplicati
    detected_zones = list(set(detected_zones))

    # Gestisci le transizioni di stato e aggiorna 'azione'
    for zone in detected_zones:
        # Controlla se è passato abbastanza tempo dall'ultimo comando per questa zona
        # if current_time - last_command_time[zone] >= command_interval:
            messages.append(zone)
            last_command_time[zone] = current_time  # Aggiorna l'ultimo tempo di comando

            # Simula la pressione del tasto corrispondente
            if zone in zones:
                key = zones[zone]
                print(f"Simulazione pressione tasto: {key}")  # Per debug
                if key == "left":
                    pyautogui.press('left')    # Simula la pressione della freccia sinistra
                elif key == "right":
                    pyautogui.press('right')   # Simula la pressione della freccia destra
                elif key == "down":
                    pyautogui.press('down')    # Simula la pressione della freccia giù
                elif key == "up":
                    pyautogui.press('up')      # Simula la pressione della freccia su (per ruotare)

    # Rimuovi duplicati nei messaggi
    messages = list(set(messages))

    # Stampa i messaggi sulla console
    for message in messages:
        print(message)

    # Opzionale: visualizza i messaggi sul frame
    for idx, message in enumerate(messages):
        cv2.putText(frame, message, (10, 30 + idx * 30), font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

    # Mostra il frame
    cv2.imshow('Rilevamento Mano', frame)

    # Esci premendo 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Rilascia la videocamera e chiudi tutte le finestre
cap.release()
cv2.destroyAllWindows()
