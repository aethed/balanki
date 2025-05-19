import os
import sys
import shutil
import platform

def load_simpleaudio():
    os_type = platform.system()

    if os_type == "Linux":

        python_version = sys.version_info[:2]

        if python_version == (3, 9):
            libasound = "simpleaudio_patched-1.0.5-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64"
        elif python_version == (3, 10):
            libasound = "simpleaudio_patched-1.0.5-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64"
        elif python_version == (3, 11):
            libasound = "simpleaudio_patched-1.0.5-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64"
        elif python_version == (3, 12):
            libasound = "simpleaudio_patched-1.0.5-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64"
        elif python_version == (3, 13):
            libasound = "simpleaudio_patched-1.0.5-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64"
        else:
            return

        addon_path = os.path.dirname(os.path.dirname(__file__))
        current_path = os.path.dirname(__file__)
        libasound_folder = os.path.join(current_path, libasound)

        for item in os.listdir(libasound_folder):
            if "simpleaudio_patched.libs" in item:
                source_path = os.path.join(libasound_folder, item)
                destination_path = os.path.join(addon_path, item)
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, destination_path, dirs_exist_ok=True)

    elif os_type == "Darwin":

        arch = platform.machine()
        if arch == "arm64":
            simpleaudio = "simpleaudio_patched-1.0.5-cp39-cp39-macosx_11_0_arm64"
        elif arch == "x86_64":
            simpleaudio = "simpleaudio_patched-1.0.5-cp39-cp39-macosx_10_9_x86_64"

        addon_path = os.path.dirname(os.path.dirname(__file__))
        simpleaudio_for_mac = os.path.join(addon_path, "simpleaudio_for_mac", simpleaudio)

        for item in os.listdir(simpleaudio_for_mac):
            if "_simpleaudio.cpython-39-darwin.so" in item:
                source_path = os.path.join(simpleaudio_for_mac, item)
                destination_path = os.path.join(addon_path, "simpleaudio", item)
                if os.path.isfile(source_path):
                    shutil.copy2(source_path, destination_path)
