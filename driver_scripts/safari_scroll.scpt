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

      open location "http://reddit.com"

      tell document 1
        repeat with i from 1 to 100 

          -- set the vertical scroll 
          repeat with y from 50 to 100 
            do javascript "h=document.documentElement.scrollHeight-document.documentElement.clientHeight; window.scrollTo(0,h*" & 100 & "/100)"
            delay 0.25
          end repeat

          delay 3
        end repeat
      end tell

    end if
end tell
