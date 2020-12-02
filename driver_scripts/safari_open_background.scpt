tell application "Safari" 

    if it is running then
      activate

      set sites to { "google.com" }
      repeat with site in sites
        open location site
        
        repeat while document 1's source = ""
          delay 0.5
        end repeat

      end repeat

      activate
    end if
end tell