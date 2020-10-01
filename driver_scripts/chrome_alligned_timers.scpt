tell application "Chromium" 
    if it is running then
      activate
      set w to first window

      set bounds of front window to {0, 0, 1920, 1080}

      set base_url to "file:///Users/olivier/git/chrome_safari_power/pages/spam_tasks.html?interval=200&numPeers=3&peerID="
      set sites to { base_url & "1", base_url & "2", base_url & "3" }

      set i to 1
      repeat with site in sites
        make new window
        set bounds of front window to {1080 / 3 *i, 0, 1920, 1080}
        open location site

        set i to i+1
      end repeat

      activate
    end if

end tell
