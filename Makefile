CC = gcc -g -pedantic -std=c99 -Wall -Wextra

all: split

split: split.c
	@$(CC) -o split split.c

clean:
	@rm -f split
	@find . -name '*.o' | xargs rm -f
	@find . -name '*.dSYM' | xargs rm -f -r

.PHONY: all clean
