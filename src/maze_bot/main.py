"""Module for cli entrypoint"""
import argparse
import pyfiglet
from termcolor import colored
import sys
from maze_bot import maze_bot


app_name = "Hello World"
app_description = "Put your app description here!"
color = "red"
font = "slant"


def cli():
  """
  Renders the command line interface for the package.
  """
  parser = argparse.ArgumentParser(
    prog="helloworld",
    description=colored(pyfiglet.figlet_format(app_name, font=font), color) + \
                colored(app_description, color),
    formatter_class=argparse.RawTextHelpFormatter
  )

  parser.add_argument("-z",
                      "--maze",
                      action="store_true",
                      help="This argument triggers an action.")

  if len(sys.argv) == 1:
    parser.print_help(sys.stderr)

  args = parser.parse_args()

  try:
    if args.maze:
      maze_bot.my_app()
    return True

  except KeyboardInterrupt:
    print("\nUser interrupted program.")

  return False


if __name__ == "__main__":
  cli()
