# maoio_stt_pipeline2.py
import requests
from typing import Dict, Any
from pipelines.base import BaseSpeechToText  # Import iz OpenWebUI pipelines
from pydantic import BaseModel
import json

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

    def stt(self, audio_file_path: str) -> str:
        # Implementacija STT funkcije – prima putanju do audio datoteke i vraća tekst kao string
        try:
            params = {
                'encode': str(self.valves.ENCODE).lower(),
                'task': self.valves.TASK.lower(),
                'vad_filter': str(self.valves.VAD_FILTER).lower(),
                'word_timestamps': str(self.valves.WORD_TIMESTAMPS).lower(),
                'output': self.valves.OUTPUT,
            }
            headers = {
                'accept': 'application/json',
            }
            
            with open(audio_file_path, "rb") as audio_file:
                files = {
                    'audio_file': (audio_file_path.split('/')[-1], audio_file, "audio/mpeg")
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
                raise ValueError("Odgovor nije validna lista ili je prazna.")
            
            text = data_list[0].get("data", "").strip()
            return text  # Vraća samo tekst (string), bez dodatnih podataka
            
        except Exception as e:
            return f"Greška u transkribiranju: {str(e)}"

    def get_info(self) -> Dict[str, Any]:
        return {
            "name": "MAOIO ASR",
            "description": "Pretvara govor u tekst koristeći MAOIO ASR endpoint",
            "display_name": "MAOIO ASR",  # Kako će se prikazati u UI izborniku
        }
