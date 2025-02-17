CC		:= gcc

CFLAGS 	:= -g -O0
OBJS	:= pic_writer.o pic_serial.o

EXE		:= pic_writer

all: $(EXE)

$(EXE): $(OBJS)
	$(CC) $(LDFLAGS) $^ -o $@

.c.o:
	$(CC) $(CFLAGS) -c $<

clean:
	rm -f $(OBJS) $(EXE)