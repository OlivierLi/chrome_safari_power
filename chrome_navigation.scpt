tell application "Google Chrome" 
    if it is running then
      activate

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
      tell active tab of window 1
        close
      end tell

      activate
    end if

end tell
