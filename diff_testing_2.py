# Got help from this! https://www.smallsurething.com/comparing-files-in-python-using-difflib/

import sys, pprint
from deepdiff import DeepDiff

pp = pprint.PrettyPrinter(indent=2)

def main():
  print(sys.argv)
  if len(sys.argv) != 3:
    return

  with open(sys.argv[1]) as f1, open(sys.argv[2]) as f2:
    lines1 = f1.readlines()
    lines2 = ['red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'blue', 'blue', 'blue', 'orange', 'yellow', 'yellow', 'yellow', 'o', 'o', 'o', 'o', 'o', 'o']
    lines2 = [line + '\n' for line in lines2]
    print(lines1)
    print(lines2)
    ddiff = DeepDiff(lines1, lines2)
    pp.pprint(ddiff)


if __name__ == "__main__":
  main()
