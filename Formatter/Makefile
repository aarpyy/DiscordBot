CC = gcc -g -pedantic -std=c99 -Wall -Wextra

TARGETS = split format

.PHONY: clean

all: split format

split: split.c
	@$(CC) -o split split.c

format: format.c config.h
	@$(CC) -o format format.c

clean:
	@rm -f $(TARGETS)
	@find . -name '*.o' | xargs rm -f
	@find . -name '*.dSYM' | xargs rm -f -r
