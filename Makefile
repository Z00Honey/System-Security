CC = gcc
CFLAGS = -Wall -Werror -fPIC
LDFLAGS = -shared

SRCDIR = src/core
INCDIR = src/core/include
BINDIR = build
TARGET = $(BINDIR)/libfile_explorer.so

SOURCES = $(wildcard $(SRCDIR)/*.c)
OBJECTS = $(SOURCES:.c=.o)

$(TARGET): $(OBJECTS)
	mkdir -p $(BINDIR)
	$(CC) $(CFLAGS) -I$(INCDIR) $(OBJECTS) -o $(TARGET) $(LDFLAGS)

clean:
	rm -f $(SRCDIR)/*.o $(TARGET)