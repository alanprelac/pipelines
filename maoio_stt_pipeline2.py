# maoio_stt_pipeline2.py
import requests
from typing import Dict, Any
import os
from pipelines.base import BaseSpeechToText  # OpenWebUI import za STT pipelines
from pydantic import BaseModel

class Valves(BaseModel):
    ASR_API_URL: str = "http://h1.maoio.eu:32772/asr"
    ENCODE: bool = True
    TASK: str = "transcribe"
    VAD_FILTER: bool = False
    WORD_TIMESTAMPS: bool = False
    OUTPUT: str = "txt"

class MySTTPipe(BaseSpeechToText):
    def __init__(self):
        self.valves = Valves()
        self.valves = self.valves

    def stt(self, audio_file_path: str) -> str:
        # Ako putanja nije validna, vrati grešku
        if not os.path.isfile(audio_file_path):
            return f"Greška: Audio datoteka '{audio_file_path}' nije pronađena."
        
        try:
            params = {
                'encode': str(self.valves.ENCODE).lower(),
                'task': self.valves.TASK,
                'vad_filter': str(self.valves.VAD_FILTER).lower(),
                'word_timestamps': str(self.valves.WORD_TIMESTAMPS).lower(),
                'output': self.valves.OUTPUT,
            }
            headers = {
                'accept': 'application/json',
            }
            
            with open(audio_file_path, "rb") as audio_file:
                files = {
                    'audio_file': (os.path.basename(audio_file_path), audio_file, "audio/mpeg")
                }
                response = requests.post(
                    self.valves.ASR_API_URL,
                    params=params,
                    headers=headers,
                    files=files,
                    timeout=30
                )
            
            response.raise_for_status()
            data_list = response.json()
            if not isinstance(data_list, list) or not data_list:
                return "Greška: Odgovor s API-ja nije validan."
            
            text = data_list[0].get("data", "").strip()
            if not text:
                return "Greška: Transkribirani tekst je prazan."
            return text
        
        except requests.exceptions.RequestException as e:
            return f"Greška: Greška u API pozivu - {str(e)}"
        except Exception as e:
            return f"Greška: Nepoznata greška - {str(e)}"

    def get_info(self) -> Dict[str, Any]:
        return {
            "name": "maoio_asr",
            "description": "Custom STT pipeline za MAOIO ASR endpoint",
            "display_name": "MAOIO ASR",  # Ovo će se prikazati u izborniku
            "valves": self.valves,  # Omogućuje prilagođavanje u UI-ju
        }
