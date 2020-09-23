tell application "Safari" 
    if it is running then
      activate
      set w to first window

      set bounds of w to {0, 0, 1920, 1080}

      --open location "http://cnn.com"
      --delay 15
      --set t to current tab of w
      --close t 

      --open location "http://www.bestbuy.ca"
      --delay 15
      --set t to current tab of w
      --close t 

      open location "http://www.polygon.com"
      delay 15

      set t to current tab of w
      close t 

      activate
    end if
end tell
