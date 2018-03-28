# Got help from this! https://www.smallsurething.com/comparing-files-in-python-using-difflib/

import sys
import difflib


def main():
  print(sys.argv)
  if len(sys.argv) != 3:
    return

  with open(sys.argv[1]) as f1, open(sys.argv[2]) as f2:
    lines1 = f1.readlines()
    lines2 = ['red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'blue', 'orange', 'yellow', 'yellow', 'yellow', 'o', 'o', 'o', 'o', 'o', 'o']
    lines2 = [line + '\n' for line in lines2]
    print(lines1)
    print(lines2)
    for diff in difflib.context_diff(lines1,
                                     lines2,
                                     fromfile=sys.argv[1],
                                     tofile=sys.argv[2]):
      sys.stdout.write(diff)


if __name__ == "__main__":
  main()
