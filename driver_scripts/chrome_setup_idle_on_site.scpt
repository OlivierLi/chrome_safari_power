tell application "Chromium" 
    if it is running then
      activate

      set bounds of front window to {0, 0, 1920, 1080}

      open location "http://www.polygon.com"

      activate
    end if

end tell
