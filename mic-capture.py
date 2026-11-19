# mic-capture.py
# ---------------------------------------------------------------------------
# Push-to-talk recorder: hold the button to record from a USB microphone,
# release it to hear the recording played back.
#
# This is a good way to test your microphone AND speaker before running the
# full voice assistant (agent.py).
#
# Tips for Raspberry Pi 4B:
#   - Run `arecord -l` in a terminal to list recording devices. Find your USB
#     mic's "card" and "device" numbers and update MIC_DEVICE below to match.
#   - Playback uses the Pi's default audio output (3.5mm jack, HDMI, or a
#     USB/Bluetooth speaker, depending on your audio settings).
#
# Run it with:  python3 mic-capture.py
# ---------------------------------------------------------------------------

# subprocess lets Python run other programs. We use it to run the Linux
# command-line tools `arecord` (record audio) and `aplay` (play audio),
# which come pre-installed on Raspberry Pi OS.
import subprocess

# signal lets us send a "stop" signal to arecord, and also gives us pause().
import signal

# gpiozero makes it easy to read the push button on the GPIO pins.
from gpiozero import Button

# --- Settings you may need to change ---
BUTTON_PIN = 17            # GPIO17 (physical pin 11)
MIC_DEVICE = "plughw:3,0"  # your USB mic: card 3, device 0 (check with `arecord -l`)
FILE = "/tmp/recording.wav"  # where the recording is saved (/tmp is cleared on reboot)

# Set up the button on the chosen GPIO pin.
button = Button(BUTTON_PIN)

# This will hold the running arecord program while we are recording.
# "None" means "nothing is recording right now".
recorder = None


def start_recording():
    """Runs automatically when the button is pressed. Starts recording."""
    # "global" means we want to change the `recorder` variable defined above,
    # instead of creating a new one that only exists inside this function.
    global recorder

    # If we are already recording, do nothing.
    if recorder is not None:
        return

    print("Recording... (hold the button)")

    # Start arecord in the background. The options mean:
    #   -D MIC_DEVICE : which microphone to use
    #   -f cd         : CD quality (16-bit, 44.1 kHz, stereo)
    #   -t wav        : save as a .wav file
    #   FILE          : the file to save to
    # stderr=DEVNULL hides arecord's status messages to keep the terminal tidy.
    recorder = subprocess.Popen(
        ["arecord", "-D", MIC_DEVICE, "-f", "cd", "-t", "wav", FILE],
        stderr=subprocess.DEVNULL,
    )


def stop_and_play():
    """Runs automatically when the button is released. Stops and plays back."""
    global recorder

    # If nothing is recording, there is nothing to stop.
    if recorder is None:
        return

    # SIGINT lets arecord finish writing a valid WAV header
    # (SIGINT is the same signal your terminal sends when you press Ctrl+C.)
    recorder.send_signal(signal.SIGINT)
    recorder.wait()  # wait until arecord has completely finished
    recorder = None  # remember that we are no longer recording

    print("Playing back...")
    # Play the file through the Pi's speaker. subprocess.run waits until
    # playback is finished before moving on to the next line.
    subprocess.run(["aplay", FILE], stderr=subprocess.DEVNULL)
    print("Done. Hold the button to record again.")


# Connect our functions to the button: press = start, release = stop & play.
button.when_pressed = start_recording
button.when_released = stop_and_play

print("Ready. Hold the button to record, release to play back. Ctrl+C to quit.")

# Keep the script alive, waiting for button events, until you press Ctrl+C.
signal.pause()
