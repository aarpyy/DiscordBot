# Config file for main script player_request.py
# Currently just accesses N_HEROES from config.h

import re

# Regex to match a define statement in C header file, adding the variable to globals
define_statement = re.compile(r"""
    ^                               # start of line
    \s*                             # optional leading whitespace
    \#define                        # #define statement
    \s+                             # at least one space between define and variable name
    (?P<varname>[a-z_][a-z0-9_]*)   # variable name, only accepts characters for valid Python varname
    \s+                             # at least one space between variable name and value (if there is one)
    (?P<value>.+)                   # value is anything after define statement; comments have been stripped
    """, re.IGNORECASE | re.VERBOSE)


N_HEROES = None


def main():
    # Add all variables #define-d in a C header file in locals()
    with open('Formatter/config.h', 'r') as configfile:
        for line in configfile:
            m = re.match(define_statement, line.split('//')[0])     # Split by // to ignore any comments
            if m and m.group('value'):                              # If a match was made with a variable with value
                globals()[m.group('varname').strip(' ')] = eval(m.group('value').strip(' '))


# Not inside if __name__ == '__main__' so that when imported, config.py will check if N_HEROES is None
# and properly load N_HEROES if not
if N_HEROES is None:
    main()
