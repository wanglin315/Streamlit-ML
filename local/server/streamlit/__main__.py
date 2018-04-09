"""This is a script which is run when the streamlit package is executed."""

import sys
import textwrap
import streamlit.local.caching
import streamlit.local.reference

def print_usage():
    """Prints a help message."""
    usage = """
        Usage:

        python -m streamlit <command>

        where command is one of:

        clear_cache - Clear the memoization cache.
        help        - Show help in browser.
        usage       - Print this help message.
    """
    print(textwrap.dedent(usage).strip())

def clear_cache():
    streamlit.local.caching.clear_cache(True)

def help():
    print('Showing help page in browser..')
    streamlit.local.reference.display_reference()

def main():
    # Dispatch based on the given command.
    accepted_commands = {
        'usage': print_usage,
        'clear_cache': clear_cache,
        'help': help,
    }
    try:
        accepted_commands[sys.argv[1]](*sys.argv[2:])
    except IndexError:
        print_usage()
    except KeyError:
        print(f'Command "{sys.argv[1]}" invalid.\n')
        print_usage()

if __name__ == '__main__':
    main()
