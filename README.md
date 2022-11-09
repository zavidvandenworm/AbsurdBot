# AbsurdiBot
A discord bot with a variety of creative commands, such as image/audio editing, "remixing" music and more.

### Note: don't expect a polished product. This was done for fun, and half of the code here is still in the "do first, refactor later" phase. A lot is outright broken/unused (but all commands are functional).

## Setup
### Note: you should probably use Python 3.9+, as anything before it hasn't been tested
### Step 1: install package requirements.
```
pip install -r requirements.txt
````
### Step 2: Fill in service_setup.py
Can be found in ./cogs/scripts/service_setup.py
You will need:
1.  A valid [discord bot token](https://discord.com/developers/applications)
2.  An [OpenAI key](https://beta.openai.com/account/api-keys) (Note: OpenAI's gives you 16$ in tokens for free)
3.  A [Reddit application](https://old.reddit.com/prefs/apps/) (Client ID, Client Secret, User Agent)
4.  A (http(s)) web server for large files

### Step 3: Run main.py
If everything went right, this should start without any errors.

You're done!
The prefix of the bot can be changed in main.py -> prefix variable

## Available commands
### Artificial Intelligence
**openai_complete (prompt)**<br/>
Let the bot finish writing prompts, using OpenAI's DaVinci models.<br/>
Example: `-openai_complete Tell me a story!`<br/>

**openai_code (prompt)**<br/>
Describe a program, and the bot will create it for you using OpenAI's Codex models.<br/>
Example: `-openai_code Write a script in C that prints hello world!`<br/>

### Audio Tools/Manipulation
**any2mp3 (input_url)**<br/>
Converts any audio or video file into a mp3 file.<br/>
Example: `-any2mp3 https://example.com/video.mp4`<br/>

**audio_trim (url_to_audio) (trim_start) (optional: trim_end)**<br/>
Trim an audio file, arguments in milliseconds.<br/>
Example: `-audio_trim https://example.com/audio.mp3 1000 5000` - would cut the first second off, and would cut off at 5 seconds = 4 second output.<br/>

**breakcoregen (url_to_audio) (bpm) (optional: soundpack)**<br/>
Adds breaks, and compresses the input.<br/>
Example: `-breakcoregen https://example.com/audio.mp3 165 default1`<br/>
Sound packs will use different breaks for the output.<br/>

**clubgen (url_to_audio) (bpm) (optional: target_bpm)**<br/>
Adds a punchy beat, slows down, and adds reverb to the input.<br/>
Example: `-clubgen https://example.com/audio.mp3 165 150`<br/>
Changing the target BPM will affect how much the input gets slowed down.<br/>

**drum_machine (beat_pattern) (bpm) (sample) (optional: overlay_audio)**<br/>
A drum machine.<br/>
The beat pattern consists of 0's and 1's. 0 means off, 1 means play.<br/>
Example: `-drum_machine 1000100010001000 130 808_kick`<br/>
You can also overlay the output onto an audio file.<br/>
Example: `-drum_machine 1000100010001000 130 808_kick https://example.com/audio.mp3`<br/>

**list_samples**<br/>
Simply lists all available samples for drum_machine and breakcoregen.<br/>
Example: `-list_samples`<br/>

### (List is a WIP)
