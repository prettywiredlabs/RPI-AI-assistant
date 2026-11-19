# elevenlabs-quickstart-stt.py
# ---------------------------------------------------------------------------
# Speech-to-text (STT) test: sends a recorded audio file to ElevenLabs and
# prints the transcription (the words it heard).
#
# Before running:
#   1. Make a recording first with mic-capture.py (it saves /tmp/recording.wav).
#   2. Put your ELEVENLABS_API_KEY in the .env file.
#
# Run it with:  python3 elevenlabs-quickstart-stt.py
# ---------------------------------------------------------------------------

# os lets us read environment variables (like our API key).
import os

# python-dotenv loads the keys from the .env file.
from dotenv import load_dotenv

# The official ElevenLabs library.
from elevenlabs.client import ElevenLabs

# Read the .env file so os.getenv() can find ELEVENLABS_API_KEY.
load_dotenv()

# Create an ElevenLabs client using our API key.
elevenlabs = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

AUDIO_FILE = "/tmp/recording.wav"  # same path your record/playback script saves to

# Open the audio file in "rb" (read binary) mode, because audio isn't text.
# The "with" block closes the file automatically when we're done with it.
with open(AUDIO_FILE, "rb") as audio_file:
    # Upload the audio to ElevenLabs and get back a transcription.
    transcription = elevenlabs.speech_to_text.convert(
        file=audio_file,
        model_id="scribe_v3",    # Model to use
        tag_audio_events=True,   # Tag audio events like laughter, applause, etc.
        language_code="eng",     # Set to None to auto-detect the language
        diarize=True,            # Annotate who is speaking
    )

# Print the full result (includes extra details like word timings and speakers).
print(transcription)

# Uncomment the line below instead if you only want the plain text.
#print(transcription.text)
