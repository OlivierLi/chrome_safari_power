from jinja2 import Template
import os
import utils
from shutil import copyfile

def render(file_prefix, template, template_file, process_name):
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
                browser=process_name))


def render_runner_scripts():
    for template_file in ['open_background', 'idle_on_site', 'idle', 'scroll', 'navigation', 'alligned_timers', 'zero_window']:

        with open("./driver_scripts_templates/"+template_file) as file_:
            template = Template(file_.read())
            
            # Generate for all Chromium based browsers
            for browser in ['Chrome', 'Canary', "Chromium", "Edge"]:
                process_name = utils.browsers_definition[browser]["process_name"]
                render(browser, template, template_file, process_name)

        # Skip alligned timer case as chrome only
        if template_file == "alligned_timers":
            continue

        template_file = "safari_"+template_file
        with open("./driver_scripts_templates/"+template_file) as file_:
            template = Template(file_.read())

            # Generate for Safari
            render("", template, template_file, "")
        
def generate_all():
  os.makedirs("driver_scripts", exist_ok=True)
  render_runner_scripts()
  shutil.copyfile("./driver_scripts_templates/idle.scpt", "./driver_scripts/")
  shutil.copyfile("./driver_scripts_templates/finder.scpt", "./driver_scripts/")
  shutil.copyfile("./driver_scripts_templates/prep_safari.scpt", "./driver_scripts/")

