#!/usr/bin/python3

import argparse
from collections import defaultdict
import os

def main(stack_dir):

  counts = defaultdict(int)
  
  for root, dirs, files in os.walk(stack_dir):
    for stack_file in files:
      if stack_file.endswith(".txt"):

        with open(os.path.join(stack_dir, stack_file), newline='', encoding = "ISO-8859-1") as stack_file:
          lines = stack_file.readlines()
          
          stack_frames = []
          for line in lines:
            if not line.strip():
              if stack_frames:
                count = stack_frames.pop()

                # Drop rare functions for easier flamegraph generation.
                if int(count) > 2:
                  stack_frames.reverse()
                  line = ";".join(stack_frames)
                  counts[line] += int(count)

                stack_frames = []
            else:
              stack_frame = line.strip()

              # Remove offset
              plus_index = stack_frame.find('+')
              if plus_index != -1:
                stack_frame = stack_frame[:plus_index]

              stack_frames.append(stack_frame)

  for line, count in counts.items():
    print(line + " " + str(count))
      

if __name__== "__main__" :
  parser = argparse.ArgumentParser(description='Convert a directory of Dtrace stack files to collapsed format.')
  parser.add_argument("--stack_dir", help="Collapsed stack files directory.", required=True)
  args = parser.parse_args()

  main(args.stack_dir)
