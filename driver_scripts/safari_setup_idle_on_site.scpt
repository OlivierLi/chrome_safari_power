tell application "Safari" 
    if it is running then
      activate
      set w to first window

      set bounds of w to {0, 0, 1920, 1080}

      open location "http://www.polygon.com"

      activate
    end if
end tell
