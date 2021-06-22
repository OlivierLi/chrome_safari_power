#!/usr/bin/env python3

from jinja2 import Template
import argparse
import os
import utils
import shutil

""" Script to generate browser driver scripts from templates.

The generated scripts can be used to have browsers go 
through scenarios in a repeatable way.
"""

# For certain scenarios more than one driver script is generated. Return a list dicts that describes them all.
def get_render_targets(template_file, output_filename):

  # In the case of idle_on_site render for different sites.
  if template_file.endswith("idle_on_site"):
    render_targets = []
    render_targets.append({"output_filename": output_filename.replace("site","wiki"), "idle_site": "http://www.wikipedia.com/wiki/Alessandro_Volta"})
    render_targets.append({"output_filename": output_filename.replace("site","youtube"), "idle_site": "https://www.youtube.com/watch?v=9EE_ICC_wFw?autoplay=1"})
    return render_targets

  return [{"output_filename" : output_filename}]


# Render a single scenario script.
def render(file_prefix, template, template_file, process_name, extra_args):
  if file_prefix:
    file_prefix = file_prefix.replace(" ", "_") + "_"
    file_prefix = file_prefix.lower()

    background_sites = '"google.com", "youtube.com","tmall.com","baidu.com","qq.com","sohu.com","amazon.com","taobao.com","facebook.com","360.cn","yahoo.com","jd.com","wikipedia.org","zoom.us","sina.com.cn","weibo.com","live.com","xinhuanet.com","reddit.com","microsoft.com","netflix.com","office.com","microsoftonline.com","okezone.com","vk.com","myshopify.com","panda.tv","alipay.com","csdn.net","instagram.com","zhanqi.tv","yahoo.co.jp","ebay.com","apple.com","bing.com","bongacams.com","google.com.hk","naver.com","stackoverflow.com","aliexpress.com","twitch.tv","amazon.co.jp","amazon.in","adobe.com","tianya.cn","huanqiu.com","aparat.com","amazonaws.com","twitter.com","yy.com"'
    output_filename = f"./driver_scripts/{file_prefix}{template_file}.scpt"

    for render_target in get_render_targets(template_file, output_filename):

      render_target = {**render_target, **extra_args}

      with open(render_target["output_filename"], 'w') as output:
        output.write(template.render(
          **render_target,
          background_sites=background_sites, 
          navigation_cycles=30, 
          per_navigation_delay=30, 
          delay=3600, 
          browser=process_name))


# Render all scenario driver scripts for all browsers (if applicable).
def render_runner_scripts(extra_args):

  # Generate all driver scripts from templates.
  for _, _, files in os.walk("./driver_scripts_templates"):
    for template_file in files:
      if not template_file.endswith(".scpt"):

        with open("./driver_scripts_templates/"+template_file, encoding = "ISO-8859-1") as file_:
          template = Template(file_.read())

          if template_file.startswith("safari"):
            # Generate for Safari
            render("", template, template_file, "", extra_args)
          else:
            # Generate for all Chromium based browsers
            for browser in ['Chrome', 'Canary', "Chromium", "Edge"]:
              process_name = utils.browsers_definition[browser]["process_name"]
              render(browser, template, template_file, process_name, extra_args)


def generate_all(extra_args):
  # Delete all existing generated scripts. Scripts should not be modified by hand.
  shutil.rmtree("driver_scripts/", ignore_errors=True)
  os.makedirs("driver_scripts", exist_ok=True)

  # Generate scripts for all scenarios.
  render_runner_scripts(extra_args)

  # Copy the files that don't need any substitutions. 
  for _, _, files in os.walk("./driver_scripts_templates"):
    for script in files:
      if script.endswith(".scpt"):
        shutil.copyfile(f"./driver_scripts_templates/{script}", f"./driver_scripts/{script}")


if __name__== "__main__" :
  parser = argparse.ArgumentParser(description='Flip stack order of a collapsed stack file.')
  parser.add_argument("--meet_meeting_id", help="ID of meeting for Meet base scnearios.", required=False)
  args = parser.parse_args()

  extra_args = {}
  if args.meet_meeting_id:
    extra_args["meeting_id"] = args.meet_meeting_id

  generate_all(extra_args)
