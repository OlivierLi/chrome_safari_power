tell application "Chromium" 
    if it is running then
      activate

      set bounds of front window to {0, 0, 1920, 1080}
      delay 300

      activate
    end if

end tell