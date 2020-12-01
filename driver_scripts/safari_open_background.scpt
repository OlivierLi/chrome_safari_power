tell application "Safari" 

    if it is running then
      activate

      set sites to { "google.com", "youtube.com","tmall.com","baidu.com","qq.com","sohu.com","amazon.com","taobao.com","facebook.com","360.cn","yahoo.com","jd.com","wikipedia.org","zoom.us","sina.com.cn","weibo.com","live.com","xinhuanet.com","reddit.com","microsoft.com","netflix.com","office.com","microsoftonline.com","okezone.com","vk.com","myshopify.com","panda.tv","alipay.com","csdn.net","instagram.com","zhanqi.tv","yahoo.co.jp","ebay.com","apple.com","bing.com","bongacams.com","google.com.hk","naver.com","stackoverflow.com","aliexpress.com","twitch.tv","amazon.co.jp","amazon.in","adobe.com","tianya.cn","huanqiu.com","aparat.com","amazonaws.com","twitter.com","yy.com" }
      repeat with site in sites
        open location site
        
        repeat while document 1's source = ""
          delay 0.5
        end repeat

      end repeat

      activate
    end if
end tell