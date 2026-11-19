# button_test.py
# ---------------------------------------------------------------------------
# A tiny script to check that your push button is wired up correctly.
#
# Wiring (Raspberry Pi 4B):
#   - One leg of the button   -> GPIO17 (physical pin 11)
#   - Other leg of the button -> any GND pin (for example physical pin 9)
#
# Run it with:  python3 button_test.py
# Press and release the button and you should see messages in the terminal.
# ---------------------------------------------------------------------------

# gpiozero is a beginner-friendly library for using the Pi's GPIO pins.
# It comes pre-installed on Raspberry Pi OS.
from gpiozero import Button

# pause() keeps the script running forever (until you press Ctrl+C),
# so it can keep listening for button presses.
from signal import pause

# Create a Button on GPIO17. gpiozero turns on the Pi's built-in
# "pull-up" resistor for us, so no extra resistor is needed in the circuit.
button = Button(17)

# Tell gpiozero what to do when the button is pressed or released.
# A "lambda" is just a short, nameless function written on one line.
button.when_pressed = lambda: print("Button pressed!")
button.when_released = lambda: print("Button released.")

print("Waiting for button presses... (Ctrl+C to quit)")

# Wait here while gpiozero calls our functions in the background
# whenever the button changes state.
pause()
