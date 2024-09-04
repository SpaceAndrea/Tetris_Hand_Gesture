'''Che cosa fa questo codice in breve:
- Acquisisce un video in tempo reale dalla webcam.
- Converte ogni frame da BGR a RGB per essere compatibile con MediaPipe.
- Usa MediaPipe per rilevare le mani e i loro punti chiave (landmarks).
- Disegna i punti chiave e le connessioni tra di essi sulla mano rilevata.
- Mostra il video in tempo reale con le mani tracciate in una finestra.
- Si interrompe se premi il tasto 'q'.
'''

import cv2 # importo la libreria di opencv
import mediapipe as mp #importo la libreria di mediapipe

#Inizializzazione MediaPipe Hand
mp_hands = mp.solutions.hands #creato un riferimento al modulo "Hands" di MediaPipe
# IMPORTANTE: l'oggetto hands utilizza un modello pre-addestrato per riconoscere 21 punti chiave (landmarks) per ciascuna mano, come pollice, dita e palmo
hands = mp_hands.Hands() #creato oggetto Hands per rilevare le mani nel video
mp_drawing = mp.solutions.drawing_utils #Utilizza la parte di MediaPipe chiamata drawing_utils, che permette di disegnare i landmarks rilevati sulla mano

#Creo oggetto videocapture, parametro 0 per indicare di usare la prima webcam collegata
cap = cv2.VideoCapture(0)

#Loop fin quando non premo q
while True:
    #restituisce due valori:
    # ret: True/False che indica se frame viene letto correttamente
    # frame: l'immagine acquisita dalla webcam, cioè un array Numpy contenente l'immagine del frame catturato
    ret, frame = cap.read()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #converte da BGR a RGB perché MediaPipe richiede immagine in formato RGB
    #Result conterrà i dati sui punti chiave delle mani
    result = hands.process(frame_rgb) #MediaPipe analizza il frame e cerca di rilevare le mani all'interno dell'immagine e il risultato viene salvato in "result"

    #Se MediaPipe ha rilevato una o più mani, questa variabile conterrà i punti chiave di ogni mano
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks: #ciclo for che scorre per tutte le mani rilevate nel frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS) #utilizza drawing per disegnare i punti chiave e le loro connessioni direttamente
                                                                                        #sul frame che sto visualizzando.
            #Da sapere che: "frame" è il video su cui verranno disegnati i punti chiave
                            #"hand_landmarks" sono le coordinate dei 21 punti chiave della mano
                            #"mp_hands.HAND_CONNECTIONS" disegna le connessioni tra i punti chiave per formare la mano visibile

    cv2.imshow("Webcam", frame) #mostra il frame catturato in una finestra "Webcam"

    #Attende per 1 millisecondo per vedere se è stato premuto il tasto Q, restituito con codice ASCII usando "ord"
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release() #Ferma l'acquisizione del video e chiude la connessione alla webcam
cv2.destroyAllWindows() #Chiude tutte le finestre aperte di OpenCV
