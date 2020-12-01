#!/usr/bin/env python3

from jinja2 import Template
import os

def render(file_prefix, template_file):
    if file_prefix:
        file_prefix = file_prefix.replace(" ", "_") + "_"
        file_prefix = file_prefix.lower()

    background_sites = '"google.com", "youtube.com","tmall.com","baidu.com","qq.com","sohu.com","amazon.com","taobao.com","facebook.com","360.cn","yahoo.com","jd.com","wikipedia.org","zoom.us","sina.com.cn","weibo.com","live.com","xinhuanet.com","reddit.com","microsoft.com","netflix.com","office.com","microsoftonline.com","okezone.com","vk.com","myshopify.com","panda.tv","alipay.com","csdn.net","instagram.com","zhanqi.tv","yahoo.co.jp","ebay.com","apple.com","bing.com","bongacams.com","google.com.hk","naver.com","stackoverflow.com","aliexpress.com","twitch.tv","amazon.co.jp","amazon.in","adobe.com","tianya.cn","huanqiu.com","aparat.com","amazonaws.com","twitter.com","yy.com"'

    with open("./driver_scripts/"+file_prefix+template_file+".scpt", 'w') as output:
        output.write(template.render(background_sites=background_sites, navigation_cycles=1, per_navigation_delay=3, delay=3, browser=browser))

for template_file in ['open_background', 'idle_on_site', 'idle', 'scroll', 'navigation', 'alligned_timers']:

    with open("./driver_scripts_templates/"+template_file) as file_:
        template = Template(file_.read())
        
        # Generate for all Chromium based browsers
        for browser in ['Google Chrome', "Chromium", "Microsoft Edge"]:

            # Small replacements to make files names make sense
            file_prefix=browser.replace("Google ", "").replace("Microsoft ", "")
            render(file_prefix, template_file)

    # Skip alligned timer case as chrome only
    if template_file == "alligned_timers":
        continue

    template_file = "safari_"+template_file
    with open("./driver_scripts_templates/"+template_file) as file_:
        template = Template(file_.read())

        # Generate for Safari
        render("", template_file)
        
