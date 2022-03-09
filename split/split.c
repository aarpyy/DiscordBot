#include <stdio.h>

#define NEWLINE 10      // ASCII for \n
#define LEFTCHEVRON 60  // ASCII for <

/*
 * Program splits html file by <, making it easy to read
 * for sed command since each line is a full html tag.
 */
int main(int argc, char **argv) {
    FILE *file;
    if (argc > 0) {
        file = fopen(argv[0], "r");
    } else {
        file = stdin;
    }

    int c;
    while ((c = fgetc(file)) != EOF) {
        if (c == LEFTCHEVRON) putchar(NEWLINE);
        putchar(c);
    }
    return 0;
}
