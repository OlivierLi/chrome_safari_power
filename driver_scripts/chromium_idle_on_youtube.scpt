tell application "Chromium" 
    if it is running then
      activate

      set bounds of front window to {0, 0, 1280, 720}

      open location "https://www.youtube.com/watch?v=9EE_ICC_wFw"

      delay 3600 

      activate
    end if

end tell