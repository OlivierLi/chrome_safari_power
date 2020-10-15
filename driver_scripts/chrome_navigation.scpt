tell application "Chromium" 

    -- If Chromium is already started then just bring
    -- it to the forefront otherwise open it.
    if it is running then
      reopen
    else
      activate
    end if

    if it is running then
      activate
      set w to first window
      set bounds of front window to {0, 0, 1920, 1080}

      repeat with i from 1 to 1 

        set sites to {"http://cnn.com", "http://www.bestbuy.ca", "http://www.polygon.com"}
        --set sites to {"http://www.polygon.com"}
        repeat with site in sites
          open location site

          delay 30 

          tell active tab of w
            close
          end tell
        end repeat

      end repeat

      activate
    end if

end tell
