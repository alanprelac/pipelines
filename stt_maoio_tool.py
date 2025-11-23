# stt_maoio_tool.py
import requests
from typing import Any, Dict
import json
from pydantic import BaseModel

class Valves(BaseModel):
    ASR_API_URL: str = "http://h1.maoio.eu:32772/asr"
    ENCODE: bool = True
    TASK: str = "transcribe"
    VAD_FILTER: bool = False
    WORD_TIMESTAMPS: bool = False
    OUTPUT: str = "txt"

class Pipeline:
    def __init__(self):
        self.valves = Valves()
    
    def inlet(self, body: Dict, __event_emitter__) -> Dict:
        # Prazno za sada – ako želiš pipeline, dodaj logiku ovdje (npr. automatsko dodavanje STT rezultata)
        return body
    
    def outlet(self, body: Dict, __event_emitter__) -> Dict:
        # Prazno za sada
        return body
    
    def speech_to_text(self, audio_file_path: str, mime_type: str = "audio/mpeg") -> Dict[str, Any]:
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
                    'audio_file': (audio_file_path.split('/')[-1], audio_file, mime_type)
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
            return {
                "text": text,
                "language": "hr",
            }
        except Exception as e:
            return {"text": "", "error": str(e), "language": "hr"}

class Function:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.name = "MAOIO ASR"  # Naziv alata
        self.description = "Pretvara govor u tekst koristeći MAOIO ASR endpoint na http://h1.maoio.eu:32772/asr"
        self.parameters = {
            "type": "object",
            "properties": {
                "audio_file": {
                    "type": "string",
                    "description": "Putanja do audio datoteke (npr. MP3) koju želite transkribirati."
                }
            },
            "required": ["audio_file"]
        }
    
    def get_info(self) -> Dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
    
    def call(self, arguments: str) -> str:
        args = json.loads(arguments)
        audio_file_path = args.get("audio_file", "")
        if not audio_file_path:
            return json.dumps({"error": "Nema 'audio_file' putanju!"})
        
        result = self.pipeline.speech_to_text(audio_file_path, mime_type="audio/mpeg")
        return json.dumps(result)
