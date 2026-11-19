# agent.py
# ---------------------------------------------------------------------------
# The full push-to-talk voice assistant for the Raspberry Pi 4B.
#
# How it works, step by step:
#   1. Hold the button and speak. The USB mic records your voice.
#   2. Let go. ElevenLabs turns your recording into text (speech-to-text).
#   3. The text is sent to Claude, which writes an answer.
#   4. ElevenLabs turns Claude's answer into speech (text-to-speech).
#   5. The answer plays through the Pi's speaker. Then it waits for you again.
#
# Before running, it's a good idea to test each part on its own:
#   button_test.py, mic-capture.py, anthropic-quickstart.py,
#   elevenlabs-quickstart-stt.py and elevenlabs-quickstart-tts.py
#
# You'll also need:
#   - pip install -r requirements.txt
#   - A .env file with ANTHROPIC_API_KEY and ELEVENLABS_API_KEY
#   - An MP3 player for audio playback:  sudo apt install mpv
#
# Run it with:  python3 agent.py
# ---------------------------------------------------------------------------

# --- Built-in Python modules ---
import os          # read environment variables (our API keys)
import signal      # send a "stop" signal to the recording program
import subprocess  # run Linux programs like `arecord` from Python
import time        # measure how long the button was held

# --- Libraries installed with pip (or pre-installed on Raspberry Pi OS) ---
import anthropic                          # talk to Claude
from dotenv import load_dotenv            # load API keys from the .env file
from elevenlabs.client import ElevenLabs  # speech-to-text and text-to-speech
from elevenlabs.play import play          # play audio through the speaker
from gpiozero import Button               # read the push button on the GPIO pins

# Load the keys from .env into environment variables.
# override=True means values in .env win over any already set in the terminal.
load_dotenv(override=True)

# --- Config ---
# These are the settings you are most likely to want to change.
BUTTON_PIN = 17              # GPIO17 (physical pin 11)
MIC_DEVICE = "plughw:3,0"    # USB mic: card 3, device 0 (find yours with `arecord -l`)
RECORDING_PATH = "/tmp/recording.wav"  # where each recording is temporarily saved
MIN_RECORDING_SECS = 0.5     # ignore accidental taps

STT_MODEL = "scribe_v3"            # ElevenLabs speech-to-text model
CLAUDE_MODEL = "claude-opus-5-5"   # Claude model that writes the answers
TTS_MODEL = "eleven_v4"            # ElevenLabs text-to-speech model
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # "George" (browse voices at elevenlabs.io/app/voice-library)

# The system prompt is a set of instructions Claude follows for every answer.
# Because the answer is spoken out loud, we ask for short, plain sentences.
SYSTEM_PROMPT = (
    "You are a voice assistant. Your reply will be read aloud, so answer in "
    "plain text with no markdown, lists, or special characters, and keep it brief."
)

# --- Clients ---
# Create the objects we use to talk to the button, ElevenLabs, and Claude.
button = Button(BUTTON_PIN)
elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
claude = anthropic.Anthropic()  # automatically uses ANTHROPIC_API_KEY

# Claude doesn't remember past conversations on its own, so we keep a list of
# recent messages and send it every time. This lets you ask follow-up questions.
# We only send the most recent messages so requests stay small and fast.
MAX_HISTORY_MESSAGES = 20  # keeps the last ~10 exchanges

# Each item looks like {"role": "user" or "assistant", "content": "..."}.
history = []

def record_while_held() -> float:
    """Record from the mic while the button is held. Returns the duration in seconds."""
    # Pause here until the button is pressed.
    button.wait_for_press()
    print("Recording... (release to stop)")

    # Note the start time so we can tell how long the button was held.
    started = time.monotonic()

    # Start the `arecord` program in the background. The options mean:
    #   -D MIC_DEVICE   : which microphone to use
    #   -f cd           : CD quality (16-bit, 44.1 kHz, stereo)
    #   -t wav          : save as a .wav file
    #   RECORDING_PATH  : the file to save to
    # stderr=DEVNULL hides arecord's status messages to keep the terminal tidy.
    recorder = subprocess.Popen(
        ["arecord", "-D", MIC_DEVICE, "-f", "cd", "-t", "wav", RECORDING_PATH],
        stderr=subprocess.DEVNULL,
    )

    # Keep recording until the button is let go.
    button.wait_for_release()
    duration = time.monotonic() - started

    # SIGINT lets arecord finish writing a valid WAV header
    # (SIGINT is the same signal your terminal sends when you press Ctrl+C.)
    recorder.send_signal(signal.SIGINT)
    try:
        # Give arecord up to 3 seconds to finish saving the file.
        recorder.wait(timeout=3)
    except subprocess.TimeoutExpired:
        # If it's stuck, force it to stop so the assistant doesn't freeze.
        recorder.kill()
        recorder.wait()
    print(f"Recording stopped ({duration:.1f}s).")
    return duration


def transcribe(path: str) -> str:
    """Send the audio file to ElevenLabs and return the words it heard as text."""
    # Open the file in "rb" (read binary) mode, because audio isn't text.
    with open(path, "rb") as audio_file:
        result = elevenlabs.speech_to_text.convert(
            file=audio_file,
            model_id=STT_MODEL,
            tag_audio_events=False,  # don't add tags like "(laughter)" to the text
            language_code="eng",     # we expect English speech
            diarize=False,           # only one person is speaking, so skip speaker labels
        )
    # .strip() removes any extra spaces or blank lines at the start and end.
    return result.text.strip()


def ask_claude(prompt: str) -> str:
    """Send the question (plus recent conversation) to Claude and return its answer."""
    # Add the new question to the conversation history.
    history.append({"role": "user", "content": prompt})
    try:
        message = claude.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1000,       # upper limit on how long the answer can be
            system=SYSTEM_PROMPT,
            # history[-20:] means "the last 20 items" of the list.
            messages=history[-MAX_HISTORY_MESSAGES:],
        )
    except Exception:
        history.pop()  # don't keep a question that got no answer
        raise          # pass the error on so main() can print it

    # Claude's reply is a list of "content blocks". Join all the text blocks
    # together into one string.
    answer = "".join(b.text for b in message.content if b.type == "text").strip()
    if answer:
        # Save Claude's answer so it remembers it for follow-up questions.
        history.append({"role": "assistant", "content": answer})
    else:
        # No answer came back, so remove the unanswered question.
        history.pop()
    return answer


def speak(text: str) -> None:
    """Turn text into speech with ElevenLabs and play it through the speaker."""
    audio = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id=VOICE_ID,
        model_id=TTS_MODEL,
        output_format="mp3_44100_128",  # MP3, 44.1 kHz sample rate, 128 kbps quality
    )
    play(audio)


def main() -> None:
    """Check the setup, then loop forever: listen, think, and speak."""
    # Stop early with a helpful message if an API key is missing.
    for var in ("ANTHROPIC_API_KEY", "ELEVENLABS_API_KEY"):
        if not os.getenv(var):
            raise SystemExit(f"{var} is not set (check your .env file)")

    print("Ready. Hold the button to talk. Ctrl+C to quit.")

    # "while True" repeats forever, until we "break" out of it.
    while True:
        try:
            # 1. Record. If the press was too short, it was probably an accident.
            #    "continue" skips the rest of the loop and starts over.
            if record_while_held() < MIN_RECORDING_SECS:
                print("Too short, try again.")
                continue

            # 2. Turn the recording into text.
            question = transcribe(RECORDING_PATH)
            if not question:
                print("Didn't catch that, try again.")
                continue
            print(f"You: {question}")

            # 3. Ask Claude.
            answer = ask_claude(question)
            if not answer:
                print("No response, try again.")
                continue
            print(f"Claude: {answer}")

            # 4. Say the answer out loud.
            speak(answer)
            print("\nReady. Hold the button to talk.")
        except KeyboardInterrupt:
            # Ctrl+C was pressed: exit the loop and end the program cleanly.
            print("\nBye.")
            break
        except Exception as e:  # keep running if one API call fails
            # For example: no internet, or a service is temporarily down.
            print(f"Error: {e}")


# This is true only when you run this file directly (python3 agent.py),
# not when another script imports it. It's the program's starting point.
if __name__ == "__main__":
    main()
