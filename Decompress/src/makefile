CC = gcc
CFLAGS = -s -O3
LIBS = -lpthread
EXECUTABLES = Decompress

all: $(EXECUTABLES)

.SUFFIXES: .c .o
Decompress: decompressor.o
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)

clean:
	rm $(EXECUTABLES) *.o
