#!/usr/bin/env python3

from jinja2 import Template
import os

browsers_definition = {
  "Chrome": {
    "executable": "Google Chrome",
    "identifier": "com.google.Chrome"
  },
  "Canary": {
    "executable": "Google Chrome Canary",
    "identifier": "com.google.Chrome.canary"
  },
  "Chromium": {
    "executable": "Chromium",
    "identifier": "org.chromium.Chromium"
  },
  "Edge": {
    "executable": "Microsoft Edge",
    "identifier": ""
  },
  "Safari": {
    "executable": "Safari",
    "identifier": "com.apple.Safari"
  }
}

def render(file_prefix, template_file, browser):
    if file_prefix:
        file_prefix = file_prefix.replace(" ", "_") + "_"
        file_prefix = file_prefix.lower()

    background_sites = '"google.com", "youtube.com","tmall.com","baidu.com","qq.com","sohu.com","amazon.com","taobao.com","facebook.com","360.cn","yahoo.com","jd.com","wikipedia.org","zoom.us","sina.com.cn","weibo.com","live.com","xinhuanet.com","reddit.com","microsoft.com","netflix.com","office.com","microsoftonline.com","okezone.com","vk.com","myshopify.com","panda.tv","alipay.com","csdn.net","instagram.com","zhanqi.tv","yahoo.co.jp","ebay.com","apple.com","bing.com","bongacams.com","google.com.hk","naver.com","stackoverflow.com","aliexpress.com","twitch.tv","amazon.co.jp","amazon.in","adobe.com","tianya.cn","huanqiu.com","aparat.com","amazonaws.com","twitter.com","yy.com"'
    idle_sites = ["http://www.wikipedia.com/wiki/Alessandro_Volta", "https://www.youtube.com/watch?v=9EE_ICC_wFw"]

    output_filename = "./driver_scripts/"+file_prefix+template_file+".scpt"

    # Tuple of target with idle_site
    render_targets = [(output_filename ,"wiki")]

    if template_file.endswith("idle_on_site"):
        render_targets[0] = (output_filename.replace("site","wiki"),  idle_sites[0])
        render_targets.append((output_filename.replace("site","youtube"),  idle_sites[1]))

    for render_target in render_targets:
        with open(render_target[0], 'w') as output:
            output.write(template.render(
                idle_site=render_target[1], 
                background_sites=background_sites, 
                navigation_cycles=30, 
                per_navigation_delay=15, 
                delay=3600, 
                browser=browser))

for template_file in ['open_background', 'idle_on_site', 'idle', 'scroll', 'navigation', 'alligned_timers', 'zero_window']:

    with open("./driver_scripts_templates/"+template_file) as file_:
        template = Template(file_.read())
        
        # Generate for all Chromium based browsers
        for browser in ['Chrome', 'Canary', "Chromium", "Edge"]:

            # Small replacements to make files names make sense
            file_prefix=browser
            browser_executable = browsers_definition[browser]["executable"]
            render(file_prefix, template_file, browser_executable)

    # Skip alligned timer case as chrome only
    if template_file == "alligned_timers":
        continue

    template_file = "safari_"+template_file
    with open("./driver_scripts_templates/"+template_file) as file_:
        template = Template(file_.read())

        # Generate for Safari
        render("", template_file, "")
        
