#ifndef __PIC_SERIAL_H__
#define __PIC_SERIAL_H__

#include <termios.h>
#include "pic_common.h"

#ifndef CRTSCTS
#define CRTSCTS		0x80000000
#endif

int serial_open(const char *port);
int serial_close(void);
int serial_check(void);
int serial_setting(const char *port);
int serial_mode_set(void);
int serial_read_all(void);
int serial_write_all(pic_data_t*);

#endif

