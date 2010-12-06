
CPPFLAGS = $(shell pkg-config --cflags glib-2.0)
LDFLAGS = $(shell pkg-config --libs libcurl) $(shell pkg-config --libs glib-2.0)

default:

all: ameba-updater

client.o : client.c client.h

ameba-utils.h: client.h
ameba-utils.o : ameba-utils.c ameba-utils.h

ameba-updater: ameba-updater.o ameba-utils.o client.o

clean:
	rm -f *.o

fullclean: clean
	rm -f ameba-updater
