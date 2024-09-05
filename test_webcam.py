'''Che cosa fa questo codice in breve:
- Acquisisce un video in tempo reale dalla webcam.
- Converte ogni frame da BGR a RGB per essere compatibile con MediaPipe.
- Usa MediaPipe per rilevare le mani e i loro punti chiave (landmarks).
- Disegna i punti chiave e le connessioni tra di essi sulla mano rilevata.
- Mostra il video in tempo reale con le mani tracciate in una finestra.
- Si interrompe se premi il tasto 'q'.
'''

'''Punti chiave utili (landmarks), che vengono identificati da un numero tra 0 e 20 e hanno coordinate x,y,z:
-Landmark 0: Il centro del palmo.
-Landmark 4: La punta del pollice.
-Landmark 8: La punta dell’indice.
-Landmark 12: La punta del medio.
-Landmark 16: La punta dell’anulare.
-Landmark 20: La punta del mignolo.
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

#AGGIUNTA: Memorizza le posizioni precedenti
previous_x = None
previous_y = None

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
            #Disegno i landmark nella mano:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS) #utilizza drawing per disegnare i punti chiave e le loro connessioni direttamente
                                                                                        #sul frame che sto visualizzando.
            #Da sapere che: "frame" è il video su cui verranno disegnati i punti chiave
                            #"hand_landmarks" sono le coordinate dei 21 punti chiave della mano
                            #"mp_hands.HAND_CONNECTIONS" disegna le connessioni tra i punti chiave per formare la mano visibile

            #AGGIUNTA: Landmark del palmo (landmark 0)
            current_x = hand_landmarks.landmark[0].x
            current_y = hand_landmarks.landmark[0].y

            #AGGIUNTA: Riconoscere il movimento della mano a destra o sinistra
            if previous_x is not None:
                if current_x > previous_x + 0.08:  # Tolleranza per evitare piccoli movimenti
                    print("Movimento a destra")
                elif current_x < previous_x - 0.08:
                    print("Movimento a sinistra")

            #AGGIUNTA: Riconoscere il movimento della mano verso il basso
            if previous_y is not None:
                if current_y > previous_y + 0.08:
                    print("Movimento verso il basso")

            #AGGIUNTA: Aggiorna le posizioni precedenti del palmo
            previous_x = current_x
            previous_y = current_y

    cv2.imshow("Webcam", frame) #mostra il frame catturato in una finestra "Webcam"

    #Attende per 1 millisecondo per vedere se è stato premuto il tasto Q, restituito con codice ASCII usando "ord"
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release() #Ferma l'acquisizione del video e chiude la connessione alla webcam
cv2.destroyAllWindows() #Chiude tutte le finestre aperte di OpenCV

# #IDEE: Riconoscere il movimento della mano da destra a sinistra
# # Memorizza la posizione precedente del palmo
# previous_x = None

# #Condizione: confronta la posizione x del palmo tra i frame consecutivi.
# #Se x aumenta, la mano si sta muovendo verso destra
# #Se x diminuisce, la mano si sta muovendo verso sinistra

# if result.multi_hand_landmarks:
#     for hand_landmarks in result.multi_hand_landmarks:
#         current_x = hand_landmarks.landmark[0].x  # Landmark del palmo
        
#         if previous_x is not None:
#             if current_x > previous_x + 0.02:  # Tolleranza per evitare piccoli movimenti
#                 print("Movimento a destra")
#             elif current_x < previous_x - 0.02:
#                 print("Movimento a sinistra")

#         previous_x = current_x

# #IDEE: Riconoscere il movimento della mano verso il basso
# #Memorizza la posizione precedente del palmo
# previous_y = None

# if result.multi_hand_landmarks:
#         for hand_landmarks in result.multi_hand_landmarks:
#             current_y = hand_landmarks.landmark[0].y #Landmark del palmo
        
#         if previous_y is not None:
#             if current_y > previous_y + 0.02:
#                 print("Movimento verso il basso")