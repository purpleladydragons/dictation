Barebones voice chat interface to GPT. 

## Running

You need to create a .env file like below. Get API keys from OpenAI and picovoice

```
OPENAI_API_KEY=x
PORCUPINE_API_KEY=x
```

Then just

```
python main.py
```

Speak the word "porcupine" to wake it up, and then ask your question. Recording finishes when there's a 2-second silence.

## TODO / improvements etc

- abstract over the implementations. Would be nice to support local-only with mycroft and llama.cpp
- currently, chat history is not preserved, so it's really only for one-off questions
- improve the endpoint detection
- speed up / improve the process around streaming to an audio file for whisper.cpp (stream is not ideal though IMO)