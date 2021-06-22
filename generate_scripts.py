#!/usr/bin/env python3

from jinja2 import Template
import os
import utils
import shutil

""" Script to generate browser driver scripts from templates.

The generated scripts can be used to have browsers go 
through scenarios in a repeatable way.
"""

# For certain scenarios more than one driver script is generated. Return a list of tuple that describes them all.
def get_render_targets(template_file, output_filename):
  render_targets = [(output_filename ,"")]

  # In the case of idle_on_site render for different sites.
  if template_file.endswith("idle_on_site"):
    idle_sites = ["http://www.wikipedia.com/wiki/Alessandro_Volta", "https://www.youtube.com/watch?v=9EE_ICC_wFw?autoplay=1"]
    render_targets[0] = (output_filename.replace("site","wiki"),  idle_sites[0])
    render_targets.append((output_filename.replace("site","youtube"),  idle_sites[1]))

  return render_targets


# Render a single scenario script.
def render(file_prefix, template, template_file, process_name, meet_meeting_id=None):
  if file_prefix:
    file_prefix = file_prefix.replace(" ", "_") + "_"
    file_prefix = file_prefix.lower()

    background_sites = '"google.com", "youtube.com","tmall.com","baidu.com","qq.com","sohu.com","amazon.com","taobao.com","facebook.com","360.cn","yahoo.com","jd.com","wikipedia.org","zoom.us","sina.com.cn","weibo.com","live.com","xinhuanet.com","reddit.com","microsoft.com","netflix.com","office.com","microsoftonline.com","okezone.com","vk.com","myshopify.com","panda.tv","alipay.com","csdn.net","instagram.com","zhanqi.tv","yahoo.co.jp","ebay.com","apple.com","bing.com","bongacams.com","google.com.hk","naver.com","stackoverflow.com","aliexpress.com","twitch.tv","amazon.co.jp","amazon.in","adobe.com","tianya.cn","huanqiu.com","aparat.com","amazonaws.com","twitter.com","yy.com"'
    output_filename = f"./driver_scripts/{file_prefix}{template_file}.scpt"

    for render_target in get_render_targets(template_file, output_filename):
      with open(render_target[0], 'w') as output:
        output.write(template.render(
          idle_site=render_target[1], 
          background_sites=background_sites, 
          navigation_cycles=30, 
          per_navigation_delay=30, 
          delay=3600, 
          browser=process_name,
          meeting_id=meet_meeting_id))


# Render all scenario driver scripts for all browsers (if applicable).
def render_runner_scripts(meet_meeting_id=None):

  if meet_meeting_id != None:
    template_files.append('meet')

  # Generate all driver scripts from templates.
  for _, _, files in os.walk("./driver_scripts_templates"):
    for template_file in files:
      if not template_file.endswith(".scpt"):

        with open("./driver_scripts_templates/"+template_file) as file_:
          template = Template(file_.read())

          if template_file.startswith("safari"):
            # Generate for Safari
            render("", template, template_file, "", meet_meeting_id)
          else:
            # Generate for all Chromium based browsers
            for browser in ['Chrome', 'Canary', "Chromium", "Edge"]:
              process_name = utils.browsers_definition[browser]["process_name"]
              render(browser, template, template_file, process_name, meet_meeting_id)


def generate_all(meet_meeting_id=None):
  # Delete all existing generated scripts. Scripts should not be modified by hand.
  shutil.rmtree("driver_scripts/", ignore_errors=True)
  os.makedirs("driver_scripts", exist_ok=True)

  # Generate scripts for all scenarios.
  render_runner_scripts(meet_meeting_id)

  # Copy the files that don't need any substitutions. 
  for script in ["idle", "prep_safari"]:
    shutil.copyfile(f"./driver_scripts_templates/{script}.scpt", f"./driver_scripts/{script}.scpt")


if __name__== "__main__" :
  generate_all()
