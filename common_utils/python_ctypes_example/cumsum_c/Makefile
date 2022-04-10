CC=gcc
CFLAGS=-shared -fPIC -O2

libcumsum.so: cumsum_c.c
	$(CC) -o $@ $(CFLAGS) $^

clean:
	rm -rf *.so *.o
