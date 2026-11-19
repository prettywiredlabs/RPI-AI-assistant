# elevenlabs-quickstart-tts.py
# ---------------------------------------------------------------------------
# Text-to-speech (TTS) test: turns a sentence into spoken audio with
# ElevenLabs and plays it through the Raspberry Pi's speaker.
#
# Before running:
#   1. Put your ELEVENLABS_API_KEY in the .env file.
#   2. Connect a speaker (3.5mm jack, HDMI, USB, or Bluetooth).
#   3. Playing MP3 audio needs a media player. On Raspberry Pi OS install one with:
#        sudo apt install mpv
#
# Run it with:  python3 elevenlabs-quickstart-tts.py
# ---------------------------------------------------------------------------

# python-dotenv loads the keys from the .env file.
from dotenv import load_dotenv

# The ElevenLabs client, plus a helper function that plays audio.
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

# os lets us read environment variables (like our API key).
import os

# Read the .env file so os.getenv() can find ELEVENLABS_API_KEY.
load_dotenv()

# Create an ElevenLabs client using our API key.
elevenlabs = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY"),
)

# Ask ElevenLabs to turn our text into speech (needs an internet connection).
audio = elevenlabs.text_to_speech.convert(
    text="The first move is what sets everything in motion.",  # what to say
    voice_id="JBFqnCBsd6RMkjVDRZzb",  # "George" - browse voices at elevenlabs.io/app/voice-library
    model_id="eleven_v4",             # which ElevenLabs voice model to use
    output_format="mp3_44100_128",    # MP3, 44.1 kHz sample rate, 128 kbps quality
)

# Play the audio through the Pi's default speaker.
play(audio)
