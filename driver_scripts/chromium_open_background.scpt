tell application "Chromium" 

  if it is running then
    reopen
  else
    activate
  end if

  if it is running then
    activate
    set w to first window
    set bounds of front window to {0, 0, 1280, 720}

    set sites to { "google.com", "youtube.com","tmall.com","baidu.com","qq.com","sohu.com","amazon.com","taobao.com","facebook.com","360.cn","yahoo.com","jd.com","wikipedia.org","zoom.us","sina.com.cn","weibo.com","live.com","xinhuanet.com","reddit.com","microsoft.com","netflix.com","office.com","microsoftonline.com","okezone.com","vk.com","myshopify.com","panda.tv","alipay.com","csdn.net","instagram.com","zhanqi.tv","yahoo.co.jp","ebay.com","apple.com","bing.com","bongacams.com","google.com.hk","naver.com","stackoverflow.com","aliexpress.com","twitch.tv","amazon.co.jp","amazon.in","adobe.com","tianya.cn","huanqiu.com","aparat.com","amazonaws.com","twitter.com","yy.com" }
    repeat with site in sites
      open location "http://" & site

      tell active tab of w
        repeat while (loading)
            delay 1
        end repeat
      end tell

    end repeat

  end if

end tell