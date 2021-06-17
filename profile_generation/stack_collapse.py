#!/usr/bin/python3

import argparse
from collections import defaultdict
import os

def main(stack_dir):

  counts = defaultdict(int)
  
  for root, dirs, files in os.walk(stack_dir):
    for stack_file in files:
      if stack_file.endswith(".txt"):

        with open(os.path.join(stack_dir, stack_file), newline='') as stack_file:
          lines = stack_file.readlines()
          
          stack_frames = []
          for line in lines:
            if not line.strip():
              if stack_frames:
                count = stack_frames.pop()

                line = ";".join(stack_frames)
                counts[line] += int(count)

                stack_frames = []
            else:
              stack_frames.append(line.strip())

  for line, count in counts.items():
    print(line + " " + str(count))
      

if __name__== "__main__" :
  parser = argparse.ArgumentParser(description='Convert a directory of Dtrace stack files to collapsed format.')
  parser.add_argument("--stack_dir", help="Collapsed stack files directory.", required=True)
  args = parser.parse_args()

  main(args.stack_dir)
