# 1.first we need to install 'portaudio'

# 2.Then we need to find out the path of portaudio in our laptop or pc
sudo find / -name "portaudio.h"

# 1.Then we need to write down the command
# format is:

# pip install --global-option='build_ext' --global-option='-I/opt/homebrew/Cellar/portaudio/19.7.0/include' --global-option='-L/opt/homebrew/Cellar/portaudio/19.7.0/lib' pyaudio

# What you need to write
pip install --global-option='build_ext' --global-option='-I/------PATH-------' --global-option='-L/-------PATH---------' pyaudio

########
pip install --global-option='build_ext' --global-option='-I/opt/homebrew/Cellar/portaudio/19.7.0/include' --global-option='-L/opt/homebrew/Cellar/portaudio/19.7.0/lib' pyaudio



