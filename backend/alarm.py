# backend/alarm.py

import pygame

def trigger_alarm():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load("backend/static/alert.mp3")
        pygame.mixer.music.play()
    except Exception as e:
        print("Alarm çalınamadı:", e)
