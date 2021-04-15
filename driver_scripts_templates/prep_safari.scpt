tell application "Safari" 
    activate
    reopen
    close (every tab of window 1)
    close every window
end tell
