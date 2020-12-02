tell application "Chromium" 
    if it is running then
      activate

      set bounds of front window to {0, 0, 1280, 720}

      open location "http://www.wikipedia.com/wiki/Alessandro_Volta"

      delay 3 

      activate
    end if

end tell