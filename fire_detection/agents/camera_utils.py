# agents/camera_utils.py

import json
import logging
import threading
import time
from pathlib import Path
import cv2
import pandas as pd
import torch
from django.conf import settings
from ultralytics import YOLO

# Configuration du logger
logger = logging.getLogger(__name__)

# Configuration du chemin de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Vérification de la disponibilité d'un GPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'
logger.info(f'Utilisation du device: {device}')

# AMÉLIORATION: Recherche du modèle YOLO dans plusieurs emplacements possibles
MODEL_PATH = r"C:\Users\Abd Rahim Kaouech\Desktop\firedetection\fire_detection\yolov8n.pt"

model = None
if Path(MODEL_PATH).exists():
    try:
        model = YOLO(MODEL_PATH).to(device)
        logger.info(f'Modèle YOLO chargé avec succès depuis: {MODEL_PATH}')
    except Exception as e:
        logger.error(f'Erreur lors du chargement du modèle: {e}')
else:
    logger.warning(f'Le fichier modèle n\'existe pas à ce chemin: {MODEL_PATH}')
"""MODEL_PATHS = [
    BASE_DIR / 'Hakim-F.pt',
    BASE_DIR / 'models' / 'FireShield.pt',
    BASE_DIR / 'static' / 'models' / 'FireShield.pt',
]

model = None
for path in MODEL_PATHS:
    if path and path.exists():
        try:
            model = YOLO(str(path)).to(device)
            logger.info(f'Modèle YOLO chargé avec succès depuis: {path}')
            break
        except Exception as e:
            logger.error(f'Erreur lors du chargement du modèle depuis {path}: {e}')"""

if model is None:
    logger.warning('Modèle YOLO non trouvé. La détection d\'objets sera désactivée.')
    logger.warning(f'Chemins vérifiés: {MODEL_PATHS}')


class VideoCamera:
    """
    Classe pour gérer le flux vidéo de la caméra avec détection d'objets YOLO.
    """
    def __init__(self, rtsp_url, cam_name):
        """
        Initialise la caméra vidéo.
        """
        self.rtsp_url = rtsp_url
        self.cam_name = cam_name
        self.video = cv2.VideoCapture(rtsp_url)
        self.grabbed, self.frame = self.video.read()
        self.running = True
        
        # AMÉLIORATION: Gestion de la reconnexion
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5  # secondes

        # Démarrage d'un thread pour mettre à jour le flux vidéo en arrière-plan
        threading.Thread(target=self.update, args=(), daemon=True).start()

    def __del__(self):
        """Libère les ressources vidéo lors de la destruction de l'objet."""
        logger.info(f"Libération des ressources pour la caméra {self.cam_name}")
        self.running = False
        if hasattr(self, 'video') and self.video.isOpened():
            self.video.release()

    def get_frame(self):
        """
        Récupère une frame du flux vidéo, y applique la détection d'objets et l'encode en JPEG.
        """
        if not self.grabbed:
            return None

        try:
            # Si le modèle est chargé, effectuer la prédiction
            if model:
                results = model.predict(self.frame, conf=0.4, verbose=False)
                # Dessine les boîtes de détection sur l'image
                res_plotted = results[0].plot()
            else:
                # Si pas de modèle, utiliser l'image brute
                res_plotted = self.frame

            # Encodage de l'image en JPEG
            _, jpeg = cv2.imencode('.jpg', res_plotted)
            return jpeg.tobytes()

        except Exception as e:
            logger.error(f'Erreur lors du traitement de la frame pour {self.cam_name}: {e}')
            return None

    def update(self):
        """
        Met à jour le flux vidéo en continu dans un thread séparé.
        """
        while self.running:
            if not self.video.isOpened():
                logger.warning(f"Le flux vidéo pour {self.cam_name} n'est pas ouvert. Tentative de reconnexion.")
                self.reconnect()
                time.sleep(1) # Attendre avant la prochaine tentative
                continue

            try:
                grabbed, frame = self.video.read()
                if not grabbed:
                    logger.warning(f'Impossible de lire une frame depuis {self.rtsp_url}')
                    self.reconnect()
                else:
                    self.grabbed, self.frame = grabbed, frame
                    # Réinitialiser le compteur de tentatives en cas de succès
                    self.reconnect_attempts = 0
            except Exception as e:
                logger.error(f'Erreur lors de la lecture du flux pour {self.cam_name}: {e}')
                self.reconnect()
            
            # Petite pause pour éviter de surcharger le CPU
            time.sleep(0.01)

    def reconnect(self):
        """
        Tente de se reconnecter à la caméra en cas d'erreur.
        """
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f'Nombre maximal de tentatives de reconnexion atteint pour {self.cam_name}. Arrêt du flux.')
            self.running = False
            return
            
        self.reconnect_attempts += 1
        logger.info(f'Tentative de reconnexion {self.reconnect_attempts}/{self.max_reconnect_attempts} pour {self.cam_name} dans {self.reconnect_delay}s...')
        
        time.sleep(self.reconnect_delay)
        
        try:
            if self.video.isOpened():
                self.video.release()
            self.video = cv2.VideoCapture(self.rtsp_url)
            grabbed, frame = self.video.read()
            if grabbed:
                logger.info(f'Reconnexion réussie pour {self.cam_name}')
                self.grabbed, self.frame = grabbed, frame
                self.reconnect_attempts = 0 # Reset on success
        except Exception as e:
            logger.error(f'Erreur lors de la reconnexion à {self.cam_name}: {e}')


def gen(camera):
    """
    Générateur pour créer le flux vidéo en streaming HTTP.
    """
    try:
        while camera.running:
            frame = camera.get_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            else:
                # Si aucune frame n'est disponible, attendre un peu avant de réessayer
                time.sleep(0.1)
    except GeneratorExit:
        # Gérer proprement la fermeture du générateur quand le client se déconnecte
        logger.info(f'Flux vidéo terminé pour la caméra {camera.cam_name}')
    except Exception as e:
        logger.error(f'Erreur dans le générateur de flux vidéo pour {camera.cam_name}: {e}')
    finally:
        # S'assurer que la caméra est bien libérée
        if 'camera' in locals() and hasattr(camera, 'running'):
            camera.running = False
