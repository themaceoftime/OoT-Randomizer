CC = gcc
CFLAGS = -s -O3

# Windows gets Decompress.exe and Decompress32.exe
# MacOS gets Decompress.out (it doesn't support 32 bit programs)
# Linux gets Decompress

ifeq ($(OS), Windows_NT)
	EXECUTABLES = Decompress.exe Decompress32.exe
else
	UNAME_S = $(shell uname -s)
	ifeq ($(UNAME_S), Darwin)
		EXECUTABLES = Decompress.out
	endif

	ifeq ($(UNAME_S), Linux)
		EXECUTABLES = Decompress
	endif
endif

all: $(EXECUTABLES)

.SUFFIXES: .c
Decompress.exe: decompressor.c
	$(CC) $(CFLAGS) -o $@ $^

.SUFFIXES: .c
Decompress32.exe: decompressor.c
	$(CC) $(CFLAGS) -m32 -o $@ $^

.SUFFIXES: .c
Decompress.out: decompressor.c
	$(CC) $(CFLAGS) -o $@ $^

.SUFFIXES: .c
Decompress: decompressor.c
	$(CC) $(CFLAGS) -o $@ $^
