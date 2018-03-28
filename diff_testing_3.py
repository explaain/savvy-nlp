# Got help from this! https://www.smallsurething.com/comparing-files-in-python-using-difflib/

import sys
import difflib


def main():
  print(sys.argv)
  if len(sys.argv) != 3:
    return

  with open(sys.argv[1]) as f1, open(sys.argv[2]) as f2:
    lines1 = f1.readlines()
    lines2 = f2.readlines()
    # print(lines1)
    # print(lines2)
    for diff in difflib.context_diff(lines1, lines2):
      print(diff)


if __name__ == "__main__":
  main()
