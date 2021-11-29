#include <stdio.h>
#include <ctype.h>
#include "config.h"

#define NEWLINE 10      // ASCII for \n
#define VERTLINE 124    // ASCII for |


/*
 * This program reads in a file containing two types of lines: either a
 * competitive-rank related data/link, or a hero name/hero stat.
 * It ignores the former through checking if | is in the line (| were
 * inserted by a previous shell script to all lines containing rank data,
 * and are not contained by any hero name/stat lines) and formats the latter
 * by checking if a digit is present. If a digit is not present, then it is
 * a hero name and should be followed by | and the stat (ex. Genji|32:40:05)
 * to make for easier future parsing in Python. If a digit is present, that
 * means the hero name was already read and the stat should be printed as
 * normal.
 */
int main() {
    int c;

    // 'booleans' for ignoring line and if a digit is present in a line
    char ignore = 0;
    char has_digit = 0;

    // lines_printed strictly less than 32 (currently < 10) so char is enough
    unsigned char lines_printed = 0;
    while ((c = getchar()) != EOF) {
        if (lines_printed == 2 * N_HEROES) return 0;
        else if (c == VERTLINE) {
            putchar(c);
            ignore = 1;
        }
        else if (isdigit(c)) {
            has_digit = 1;
            putchar(c);
        }
        else if (c == NEWLINE) {
            lines_printed++;
            if (ignore) {
                lines_printed = 0;
                putchar(c);
            }
            else if (has_digit) putchar(c);
            else putchar(VERTLINE);
            ignore = 0;
            has_digit = 0;
        }
        else putchar(c);
    }
    return 0;
}
