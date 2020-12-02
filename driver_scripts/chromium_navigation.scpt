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
      set bounds of front window to {0, 0, 1280, 720}

      -- Insure a tab stays live all the time so the window doesn't go away.
      open location "about:blank"

      -- Each cycles takes about 2 mins. Aim for a test that takes an hour.
      repeat with i from 1 to 30

        set sites to {"http://cnn.com", "http://www.lapresse.ca", "http://www.nytimes.com", "http://theguardian.com"}
        repeat with site in sites
          open location site

          delay 3600 

          tell active tab of w
            close
          end tell
        end repeat

      end repeat

      activate
    end if

end tell