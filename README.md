# Raspberry Pi AI Voice Assistant

A push-to-talk voice assistant for the Raspberry Pi 4B. Hold a button and speak: your voice is recorded with a USB microphone, transcribed by [ElevenLabs](https://elevenlabs.io/) speech-to-text, answered by [Claude](https://www.anthropic.com/claude), and spoken back through the Pi's speaker with ElevenLabs text-to-speech. Claude keeps recent conversation history, so you can ask follow-up questions.

📺 **Watch the live stream:** [Livestream | Build an AI Voice Assistant with Raspberry Pi](https://youtube.com/live/1oBIsfcoGmA)

## Prerequisites

### Hardware

- Raspberry Pi 4B running Raspberry Pi OS
- USB microphone
- Speaker (3.5mm jack, HDMI, USB, or Bluetooth)
- Momentary push button wired to **GPIO17** (physical pin 11) and any **GND** pin (e.g., physical pin 9). No resistor is needed; the Pi's internal pull-up is used.

### Software & accounts

- Python 3.8+
- An [Anthropic API key](https://console.anthropic.com/)
- An [ElevenLabs API key](https://elevenlabs.io/app/settings/api-keys)
- `mpv` for MP3 playback:

  ```bash
  sudo apt install mpv
  ```

Install the required Python packages (`anthropic`, `elevenlabs`, `python-dotenv`):

```bash
pip install -r requirements.txt
```

> `gpiozero`, `arecord`, and `aplay` come pre-installed on Raspberry Pi OS.

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

```bash
ANTHROPIC_API_KEY=your-anthropic-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key
```

### Configure your microphone

Find your USB mic's card and device numbers:

```bash
arecord -l
```

Then update `MIC_DEVICE` (default `plughw:3,0`) in [mic-capture.py](mic-capture.py) and [agent.py](agent.py) to match.

## Run the Sample

It's recommended to test each component on its own before running the full assistant, roughly in the order below.

| Script | Purpose | Command |
| --- | --- | --- |
| [button_test.py](button_test.py) | Verify the push button is wired correctly. Prints a message on press and release. | `python3 button_test.py` |
| [mic-capture.py](mic-capture.py) | Test the mic and speaker. Hold the button to record, release to play it back. Saves to `/tmp/recording.wav`. | `python3 mic-capture.py` |
| [anthropic-quickstart.py](anthropic-quickstart.py) | Confirm your Anthropic API key works by sending one question to Claude. | `python3 anthropic-quickstart.py` |
| [elevenlabs-quickstart-stt.py](elevenlabs-quickstart-stt.py) | Transcribe `/tmp/recording.wav` with ElevenLabs speech-to-text. Run `mic-capture.py` first. | `python3 elevenlabs-quickstart-stt.py` |
| [elevenlabs-quickstart-tts.py](elevenlabs-quickstart-tts.py) | Convert a sample sentence to speech with ElevenLabs and play it. | `python3 elevenlabs-quickstart-tts.py` |
| [agent.py](agent.py) | The full voice assistant. Hold the button to ask a question, release to hear Claude's answer. | `python3 agent.py` |

Press `Ctrl+C` to exit any of the button-driven scripts.

## Issues & Questions

If you run into any problems or have questions, please [file an issue](../../issues).
