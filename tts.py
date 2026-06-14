import os
import time
import asyncio
import threading
import pygame
import edge_tts

class TTSManager:
    def __init__(self):
        self.voice_folder = "voice"
        if not os.path.exists(self.voice_folder):
            os.makedirs(self.voice_folder)
            
        pygame.mixer.init()
        self.voice_enabled = True
        self.current_audio_file = None
        # Neerja is English (India) female, offering human-like cadence
        self.voice_id = "en-IN-NeerjaNeural" 
        
    def set_voice_enabled(self, enabled):
        self.voice_enabled = enabled
        if not enabled:
            self.stop()
            
    def play_audio(self, text):
        if not self.voice_enabled or not text.strip():
            return
            
        # Run async generation in a separate thread so Tkinter does not block
        threading.Thread(target=self._generate_and_play, args=(text,), daemon=True).start()
        
    def _generate_and_play(self, text):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = os.path.join(self.voice_folder, f"response_{timestamp}.mp3")
        
        # Async context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        communicate = edge_tts.Communicate(text, self.voice_id)
        loop.run_until_complete(communicate.save(filename))
        loop.close()
        
        self.current_audio_file = filename
        
        # Play the audio via pygame
        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
        except:
            pass

    def pause(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            
    def resume(self):
        pygame.mixer.music.unpause()
        
    def stop(self):
        pygame.mixer.music.stop()
