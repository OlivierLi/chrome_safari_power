tell application "Google Chrome Canary" 
    if it is running then
      activate

      set bounds of front window to {0, 0, 1280, 720}

      open location "http://www.wikipedia.com/wiki/Alessandro_Volta"

      delay 3600 

      activate
    end if

end tell