from urllib.request import urlopen
from sys import platform as _platform

def saveFile(url,filename):
    file = urlopen(url).read()
    f = open(filename, 'w')
    f.write(file)
    f.close()

platform = ""

if _platform == "linux" or _platform == "linux2":
    platform = "Linux"
elif _platform == "darwin":
    platform = "Mac"
elif _platform == "win32":
    platform = "Windows"


def install():
    if platform == "Windows":
        saveFile('http://horseserver.tk/downloads/windows/Latest-Horse.exe', "Latest-Horse.exe")
    elif platform == "Mac":
        saveFile('http://horseserver.tk/downloads/mac/Latest-Horse.dmg', "Latest-Horse.dmg")
    elif platform == "Linux":
        saveFile('http://horseserver.tk/downloads/linux/Latest-Horse.exe', "Latest-Horse.exe")
