#!/usr/bin/python3

import csv
import argparse
from collections import defaultdict
import os

# List of stacks we just want to drop to get nicer flames. Everything under them is dropped.
ignored_frames = ["ThreadFunc", "ThreadControllerWithMessagePumpImpl::Do", "JobTask::Run", "base::RunLoop::Run", "base::Thread::Run", "RunWorker", "MessagePumpCFRunLoopBase", "::RunTask"]
tokens_to_remove = ["Chromium Framework`", "libsystem_kernel.dylib`", "Security`" ]

# Only for wakeups, in those cases a PostTask represents a context switch.
drop_frames_with = ["PostTask"]

def shorten_stack(stack):
  last_ignored_index = -1
  for i, frame in enumerate(stack):
      if any(ignored_frame in frame for ignored_frame in ignored_frames):
        last_ignored_index = i

  if last_ignored_index != -1:
    return stack[last_ignored_index+1:]

def add_category_from_any_frame(stack):

  # Categories ordered by importance.
  special_markers = ["viz", "network::", "net::", "blink::", "mojo::", "gpu::", "v8::", "sql::", "CoreText", "AppKit","Security", "CoreFoundation"]

  compound_marker = []
  for special_marker in special_markers:
    for frame in stack:
        if special_marker in frame and special_marker not in compound_marker:
          compound_marker.append(special_marker)

  # Add some namespace seperators for markers that didn't have them.
  for i, marker in enumerate(compound_marker):
    if marker.find("::") == -1:
      compound_marker[i] = marker+"::"

  # Replace some synonyms
  for i, marker in enumerate(compound_marker):
    if marker == "network::":
      if "net::" not in compound_marker:
        compound_marker[i] = "net::"
      else:
        compound_marker[i] = ""
 
  if compound_marker:
    compound_marker.sort()
    stack = ["".join(compound_marker)] + stack

  return stack

def post_process_dict(mode, stack_frames):
    with open('samples/samples.collapsed.' + mode, 'w') as f:
      for row in stack_frames:
        # Filter out the frames we don't care about and all those under it.
        if mode == "cpu_time":
          row = shorten_stack(row)

          # If nothing is left after filtering.
          if not row:
            continue

          row = add_category_from_any_frame(row)

        # In the case of wakeups there are things we don't care about at all.
        if mode == "wakeups":
          drop_whole_stack = False
          for i, frame in enumerate(row):
            if any(skip_frame in frame for skip_frame in drop_frames_with):
              drop_whole_stack = True

          if drop_whole_stack:
            continue

        # Drop parts of the function names that just add noise.  
        for i, frame in enumerate(row):
          for token in tokens_to_remove:
            row[i] = row[i].replace(token,"")

        # Reform the line in stacked format.
        count = row.pop()
        line = ';'.join(row)

        f.write(f"{line} {count}\n")

def main(mode, stack_dir):
  counts = defaultdict(int)
  rows = []

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

  for stack, count in counts.items():
    row = stack.split(';')
    row.append(str(count))
    rows.append(row)

  post_process_dict(mode, rows)


if __name__== "__main__" :
  parser = argparse.ArgumentParser(description='Flip stack order of a collapsed stack file.')
  parser.add_argument("--stack_dir", help="Collapsed stack file.", required=True)
  parser.add_argument("--mode", help="Whether to filter for wakeups or cpu time.", required=True, choices=["clean_only", "cpu_time", "wakeups"])
  args = parser.parse_args()

  main(args.mode, args.stack_dir)

