CC=gcc
CFLAGS=-shared -fPIC -O2

libcompress.so: compress.c
	$(CC) -o $@ $(CFLAGS) $^

clean:
	rm -rf *.so *.o
