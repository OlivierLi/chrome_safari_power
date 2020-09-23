tell application "Chromium" 
    if it is running then
      activate
      set w to first window

      set bounds of front window to {0, 0, 1920, 1080}

      set sites to {"http://cnn.com", "http://www.bestbuy.ca", "http://www.polygon.com"}
      repeat with site in sites
        open location site
        delay 15 

        tell active tab of w
          close
        end tell

      end repeat

      activate
    end if

end tell
