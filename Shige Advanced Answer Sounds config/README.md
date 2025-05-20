This Anki add-on is a fixed version of [Advanced Answer Sounds](https://ankiweb.net/shared/info/1167194350). Linux and Mac support has been added. (beta)


### How `choice_simpleaudio.py` work

When the Add-on is launched, it identifies the device and version, overwrites the necessary files and saves them.

I used this to create each wheel (Github Actions):
* patch: [py-simple-audio](https://github.com/harcokuppens/py-simple-audio)
* my fork: [py-simple-audio-for-anki-addon](https://github.com/shigeyukey/py-simple-audio-for-anki-addon/tree/test)

----

It would be ideal to put each wheel in the add-on and decompress it but the size is too large so I split it up and it becomes the spaghetti code🍝

Mac and Linux support python3.9
Linux is Python 3.9-3.13, if the Anki version of Python changes it will be broken and the code will need to be fixed.

I don't yet test it on all devices so I don't know if it works well.


### Fixing Procedures

1. Copy and add `simpleaudio_for_linux`
2. Copy and add `simpleaudio_for_mac`
(remove all `__pycache__`)

1. Put them in the `simpleaudio` folder

```
simpleaudio/_simpleaudio.cpython-39-x86_64-linux-gnu.so
simpleaudio/_simpleaudio.cpython-310-x86_64-linux-gnu.so
simpleaudio/_simpleaudio.cpython-311-x86_64-linux-gnu.so
simpleaudio/_simpleaudio.cpython-312-x86_64-linux-gnu.so
simpleaudio/_simpleaudio.cpython-313-x86_64-linux-gnu.so
```

4. Run this in `__init__.py`

```
sys.path.append(os.path.join(os.path.dirname(__file__), "simpleaudio"))
from .simpleaudio_for_linux.choice_simpleaudio import load_simpleaudio
load_simpleaudio()
from . import simpleaudio as sa
```
