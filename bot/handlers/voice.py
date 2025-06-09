import os
from tempfile import NamedTemporaryFile
from faster_whisper import WhisperModel
from aiogram import types
from gtts import gTTS
from core.orchestrator import Orchestrator

class VoiceHandler:
    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator
        self.whisper = WhisperModel("small")  # Модель для распознавания (может быть tiny, base, small)

    async def handle_voice(self, message: types.Message):
        """Обрабатывает голосовое сообщение"""
        # Скачиваем аудио
        voice_file = await message.voice.get_file()
        ogg_path = await self._download_voice(voice_file)
        
        # Конвертируем в WAV и распознаем
        wav_path = await self._convert_to_wav(ogg_path)
        text = await self._recognize_speech(wav_path)
        
        # Очищаем временные файлы
        os.unlink(ogg_path)
        os.unlink(wav_path)
        
        # Отправляем текст в Dashka
        return await self.orchestrator.process(message.from_user.id, text)

    async def _download_voice(self, voice_file) -> str:
        """Скачивает голосовое сообщение"""
        with NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            await voice_file.download(destination=tmp.name)
            return tmp.name

    async def _convert_to_wav(self, ogg_path: str) -> str:
        """Конвертирует OGG в WAV (нужен ffmpeg)"""
        wav_path = ogg_path.replace(".ogg", ".wav")
        os.system(f"ffmpeg -i {ogg_path} -ar 16000 {wav_path}")
        return wav_path

    async def _recognize_speech(self, audio_path: str) -> str:
        """Распознает речь через Whisper"""
        segments, _ = self.whisper.transcribe(audio_path)
        return " ".join([segment.text for segment in segments])

    async def generate_voice_response(self, text: str) -> str:
        """Генерирует голосовой ответ (TTS)"""
        tts = gTTS(text=text, lang="ru")
        with NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tts.save(tmp.name)
            return tmp.name