# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san-studio SDK Software in commercial settings.
#

import os
import subprocess
from pathlib import Path
from typing import Optional

from langchain_community.document_loaders.parsers.audio import OpenAIWhisperParser, OpenAIWhisperParserLocal


class VideoTranscriber:
    def __init__(self, video_path: str, output_dir: Optional[str] = None, use_api: bool = True):
        self.video_path = Path(video_path)
        self.output_dir = Path(output_dir) if output_dir else self.video_path.parent
        self.audio_path = self.output_dir / f"{self.video_path.stem}.wav"
        self.transcript = None
        self.use_api = use_api

    def extract_audio(self) -> str:
        command = [
            "ffmpeg",
            "-i", str(self.video_path),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-y",
            str(self.audio_path)
        ]
        subprocess.run(command, check=True)
        return str(self.audio_path)

    def transcribe_with_openai(self) -> str:
        # import openai
        # with open(self.audio_path, "rb") as audio_file:
        #     transcript = openai.Audio.transcribe("whisper-1", audio_file)
        # return transcript["text"]
    
        """
        Use OpenAI Whisper (via LangChain) to transcribe extracted audio.
        """
        parser = OpenAIWhisperParser()
        # Transcribe the videos to text
        self.transcript = parser.parse(str(self.audio_path)).text
        return self.transcript

    def transcribe_with_local_whisper(self) -> str:
        try:
            import whisper
        except ImportError:
            raise ImportError("Local Whisper not installed. Install with: pip install git+https://github.com/openai/whisper.git")
        model = whisper.load_model("tiny")
        result = model.transcribe(str(self.audio_path))
        return result["text"]

    def transcribe_audio(self) -> str:
        if self.use_api:
            try:
                return self.transcribe_with_openai()
            except Exception as e:
                print(f"OpenAI API failed: {e}. Falling back to local Whisper...")
        return self.transcribe_with_local_whisper()

    def run(self) -> str:
        print(f"Extracting audio from: {self.video_path}")
        self.extract_audio()
        print(f"Transcribing audio: {self.audio_path}")
        self.transcript = self.transcribe_audio()
        return self.transcript


if __name__ == "__main__":
    # Example Usage
    video_file_path = "videos/video1249801264.mp4"
    transcriber = VideoTranscriber(video_file_path, use_api=True)
    transcript_text = transcriber.run()

    # Save transcript
    transcript_path = Path(video_file_path).with_suffix(".txt")
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(transcript_text)

    print(f"Transcript saved to {transcript_path}")
    print(transcript_text[:500])  # Preview first 500 characters
