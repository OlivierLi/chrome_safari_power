tell application "Safari" 
    if it is running then
      activate
      set w to first window

      set bounds of w to {0, 0, 1920, 1080}

      set sites to {"http://cnn.com", "http://www.bestbuy.ca", "http://www.polygon.com"}
      repeat with site in sites
        open location site
        delay 15

        set t to current tab of w
        close t 
      end repeat

      activate
    end if
end tell
