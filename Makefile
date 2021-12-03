CC = gcc -g -pedantic -std=c99 -Wall -Wextra

TARGETS = split

.PHONY: clean

all: split

split: split.c
	@$(CC) -o split split.c

clean:
	@rm -f $(TARGETS)
	@find . -name '*.o' | xargs rm -f
	@find . -name '*.dSYM' | xargs rm -f -r
