tell application "Google Chrome" 
    if it is running then
      activate

      set bounds of front window to {0, 0, 1280, 720}

      open location "about:blank"
      delay 10

      close every window

      delay 3600 

      activate
    end if

end tell