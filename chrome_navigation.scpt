tell application "Chromium" 
    if it is running then
      activate
      set w to first window

      set bounds of front window to {0, 0, 1920, 1080}

      --open location "http://cnn.com"
      --delay 15
      --tell active tab of window 1
        --close
      --end tell

      --open location "http://www.bestbuy.ca"
      --delay 15
      --tell active tab of window 1
        --close
      --end tell

      open location "http://www.polygon.com"
      delay 15

      tell active tab of w
        close
      end tell

      activate
    end if

end tell
