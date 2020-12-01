tell application "Safari" 

    -- If Safari is already started then just bring
    -- it to the forefront otherwise open it.
    if it is running then
      reopen
    else
      activate
      reopen
    end if

    if it is running then
      activate
      set w to first window
      set bounds of w to {0, 0, 1280, 720}

      -- Each cycles takes about 2 mins. Aim for a test that takes an hour.
      repeat with i from 1 to 15 

        set sites to {"http://cnn.com", "http://www.lapresse.ca", "http://www.nytimes.com", "http://theguardian.com"}
        repeat with site in sites
          open location site

          delay 30

          set t to current tab of w
          close t 
        end repeat
      end repeat

      activate
    end if
end tell
