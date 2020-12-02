set myURL to "https://reddit.com"
set scrollAmount to "100" --- % down the page

tell application "Google Chrome"
    activate
    tell front window to set curTab to make new tab at after (get active tab) with properties {URL:myURL}
    tell curTab
        repeat while (loading)
            delay 1
        end repeat

        repeat with i from 1 to 30 

          -- set the vertical scroll 
          repeat with y from 90 to 100 
            execute javascript "h=document.documentElement.scrollHeight-document.documentElement.clientHeight; window.scrollTo(0,h*" & y & "/100)"
            delay 0.25
          end repeat

          delay 3
        end repeat
    end tell
end tell