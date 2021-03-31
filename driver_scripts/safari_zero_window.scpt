tell application "Safari" 
    if it is running then
      activate
      set w to first window

      set bounds of w to {0, 0, 1280, 720}

      open location "about:blank"
      delay 10

      close every window

      delay 3600

      activate
    end if
end tell