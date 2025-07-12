"""
Azure Cognitive Services Speech-to-Text Integration
IG-Shop-Agent: Enterprise SaaS Platform
"""

import logging
import os
import tempfile
import httpx
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)

class AzureSpeechService:
    """Azure Cognitive Services Speech-to-Text service for voice message transcription"""
    
    def __init__(self):
        self.subscription_key = os.getenv("AZURE_SPEECH_KEY")
        self.region = os.getenv("AZURE_SPEECH_REGION", "eastus")
        self.endpoint = f"https://{self.region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
        
        if not self.subscription_key:
            logger.warning("Azure Speech service not configured - voice transcription will be disabled")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("Azure Speech service initialized successfully")
    
    async def transcribe_audio(self, audio_url: str, language: str = "ar-JO") -> Optional[str]:
        """
        Transcribe audio from URL to text using Azure Speech-to-Text
        
        Args:
            audio_url: URL to the audio file
            language: Language code (ar-JO for Jordanian Arabic, en-US for English)
            
        Returns:
            Transcribed text or None if transcription fails
        """
        if not self.enabled:
            logger.warning("Azure Speech service not configured")
            return None
            
        try:
            # Download audio file
            audio_data = await self._download_audio(audio_url)
            if not audio_data:
                return None
            
            # Prepare headers
            headers = {
                "Ocp-Apim-Subscription-Key": self.subscription_key,
                "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
                "Accept": "application/json"
            }
            
            # Prepare parameters
            params = {
                "language": language,
                "format": "detailed",
                "profanity": "masked"
            }
            
            # Make transcription request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.endpoint,
                    headers=headers,
                    params=params,
                    content=audio_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract transcription from response
                    if "NBest" in result and len(result["NBest"]) > 0:
                        transcript = result["NBest"][0].get("Display", "")
                        confidence = result["NBest"][0].get("Confidence", 0)
                        
                        logger.info(f"Speech transcription successful: confidence={confidence}")
                        return transcript
                    else:
                        logger.warning("No transcription results in response")
                        return None
                else:
                    logger.error(f"Speech transcription failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    async def _download_audio(self, audio_url: str) -> Optional[bytes]:
        """Download audio file from URL"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(audio_url, timeout=30.0)
                
                if response.status_code == 200:
                    return response.content
                else:
                    logger.error(f"Failed to download audio: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            return None
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of text to determine appropriate Speech-to-Text language
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (ar-JO or en-US)
        """
        # Simple language detection based on character analysis
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        english_chars = sum(1 for c in text if c.isalpha() and c.isascii())
        
        if arabic_chars > english_chars:
            return "ar-JO"  # Jordanian Arabic
        else:
            return "en-US"  # English
    
    async def transcribe_instagram_audio(self, audio_attachment: dict) -> Optional[str]:
        """
        Transcribe Instagram audio message
        
        Args:
            audio_attachment: Instagram audio attachment data
            
        Returns:
            Transcribed text or None if transcription fails
        """
        if not self.enabled:
            return None
            
        try:
            # Extract audio URL from Instagram attachment
            audio_url = audio_attachment.get("payload", {}).get("url")
            if not audio_url:
                logger.warning("No audio URL found in Instagram attachment")
                return None
            
            # Try Arabic first (primary language for our merchants)
            transcript = await self.transcribe_audio(audio_url, "ar-JO")
            
            # If Arabic transcription fails or returns empty, try English
            if not transcript or len(transcript.strip()) < 3:
                logger.info("Arabic transcription failed or returned short result, trying English")
                transcript = await self.transcribe_audio(audio_url, "en-US")
            
            if transcript:
                logger.info(f"Successfully transcribed Instagram audio: {len(transcript)} characters")
                return transcript.strip()
            else:
                logger.warning("Audio transcription failed for both Arabic and English")
                return None
                
        except Exception as e:
            logger.error(f"Error transcribing Instagram audio: {e}")
            return None 