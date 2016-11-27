
//CUSTOM
function download(){
    if (navigator.platform.startsWith("Linux")){
        day = "Linux";
        window.location = 'http://horseserver.tk/downloads/linux/Latest-Horse.exe';
    }
    else if (navigator.platform.startsWith("Mac")){
        day = "Mac";
        window.location = 'http://horseserver.tk/downloads/mac/Latest-Horse.app';
    }
    else if (navigator.platform == "Win32"){
        day = "Windows";
        window.location = 'http://horseserver.tk/downloads/windows/Latest-Horse.exe';
    }
}
