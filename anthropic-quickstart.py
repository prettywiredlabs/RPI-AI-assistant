# anthropic-quickstart.py
# ---------------------------------------------------------------------------
# The simplest possible test of the Claude API: send one question and print
# the answer. Use this to confirm your Anthropic API key works on the Pi.
#
# Before running:
#   1. Install the libraries:  pip install -r requirements.txt
#   2. Copy .env.example to .env and put your real ANTHROPIC_API_KEY in it.
#
# Run it with:  python3 anthropic-quickstart.py
# ---------------------------------------------------------------------------

# python-dotenv reads secret keys from the .env file, so you never have to
# type them directly into your code.
from dotenv import load_dotenv

# The official Anthropic library for talking to Claude.
import anthropic

# Load the keys from .env into environment variables.
# override=True means values in .env win over any already set in the terminal.
load_dotenv(override=True)

# Create a Claude client. It automatically finds ANTHROPIC_API_KEY
# in the environment, so we don't need to pass it in ourselves.
client = anthropic.Anthropic()

# Send a message to Claude and wait for the reply (needs an internet connection).
message = client.messages.create(
    model="claude-opus-5-5",  # which Claude model to use
    max_tokens=1000,          # upper limit on how long the reply can be
    # The "system" prompt gives Claude general instructions for how to answer.
    system="Answer in plain text without formatting.",
    # "messages" is the conversation so far. Here it's just one user question.
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?",
        }
    ],
)

# Claude's reply comes back as a list of "content blocks".
# We loop through them and print only the text ones.
for block in message.content:
    if block.type == "text":
        print(block.text)
