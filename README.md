# AbsurdiBot
A discord bot with a variety of creative commands, such as image/audio editing, "remixing" music and more.

## Setup
### Step 1: install package requirements.
```
pip install -r requirements.txt
````
### Step 2: Fill in service_setup.py
Can be found in ./everything/service_setup.py
You will need:
1.  A valid [discord bot token](https://discord.com/developers/applications)
2.  An [OpenAI key](https://beta.openai.com/account/api-keys) (Note: OpenAI's gives you 16$ in tokens for free)
4.  A [Reddit application](https://old.reddit.com/prefs/apps/) (Client ID, Client Secret, User Agent)

### Step 3: Run main.py
If everything went right, this should start without any errors.

You're done!

## Bot features
### Artificial Intelligence
**openai_complete (prompt)**
Let the bot finish writing prompts, using OpenAI's DaVinci models.
Example: `-openai_complete Tell me a story!`

**openai_code (prompt)**
Describe a program, and the bot will create it for you using OpenAI's Codex models.
Example: `-openai_code Write a script in C that prints hello world!`

### Audio Tools/Manipulation
**any2mp3 (input_url)**
Converts any audio or video file into a mp3 file.
Example: `-any2mp3 https://example.com/video.mp4`

**audio_trim (url_to_audio) (trim_start) (optional: trim_end)**
Trim an audio file, arguments in milliseconds.
Example: `-audio_trim https://example.com/audio.mp3 1000 5000` - would cut the first second off, and would cut off at 5 seconds = 4 second output.

**breakcoregen (url_to_audio) (bpm) (optional: soundfont)**
Adds breaks, and compresses the input.
Example: `-breakcoregen https://example.com/audio.mp3 165 default1`
Sound packs will use different breaks for the output.

**clubgen (url_to_audio) (bpm) (optional: target_bpm)**
Adds a bunchy beat, slows down, and adds reverb to the input.
Example: `-clubgen https://example.com/audio.mp3 165 150`
Changing the target BPM will affect how much the input gets slowed down.

**drum_machine (beat_pattern) (bpm) (sample) (optional: overlay_audio)**
A drum machine.
The beat pattern consists of 0's and 1's. 0 means off, 1 means play.
Example: `-drum_machine 1000100010001000 130 808_kick`
You can also overlay the output onto an audio file.
Example: `-drum_machine 1000100010001000 130 808_kick https://example.com/audio.mp3`

**list_samples**
Simply lists all available samples for drum_machine.
Example: `-list_samples`

