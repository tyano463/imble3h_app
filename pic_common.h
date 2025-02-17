#ifndef __PIC_COMMON_H__
#define __PIC_COMMON_H__

#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

#define OK 0
#define NG -1

#define __FILENAME__ (strrchr(__FILE__, '/') ? strrchr(__FILE__, '/') + 1 : __FILE__)

#define d(x, ...)                                                                     \
    do                                                                                \
    {                                                                                 \
        printf("%s(%d) %s " x "\n", __FILENAME__, __LINE__, __func__, ##__VA_ARGS__); \
        fflush(stdout);                                                               \
    } while (0)

#define ERR_RETn(c)            \
    {                          \
        if (c)                 \
            goto error_return; \
    }

#define ERR_RETp(c, p)         \
    {                          \
        if (c)                 \
        {                      \
            p;                 \
            goto error_return; \
        }                      \
    }

#define MALLOC2d(_type, x, y)                                                                             \
    ({                                                                                                    \
        int _i;                                                                                           \
        _type **_out = (_type **)malloc(sizeof(_type *) * y + sizeof(_type) * x * y);                     \
        for (_i = 0; _i < y; _i++)                                                                        \
        {                                                                                                 \
            _out[_i] = (_type *)((unsigned char *)_##out + sizeof(_type *) * y + sizeof(_type) * x * _i); \
        }                                                                                                 \
        (_out);                                                                                           \
    })

typedef enum
{
    CONF_TYPE_NONE,
    CONF_TYPE_BEGIN,
    CONF_TYPE_PIC,
    CONF_TYPE_PGM_SIZE_WORD,
    CONF_TYPE_EEPROM_BYTE,
    CONF_TYPE_CONFIG1,
    CONF_TYPE_CONFIG2,
    CONF_TYPE_POWER_MODE,
    CONF_TYPE_PGM_TYPE,
    CONF_TYPE_COMMENT,
    CONF_TYPE_PACKAGE,
    CONF_TYPE_JP2,
    CONF_TYPE_FIRM,
    CONF_TYPE_VDD_VPP_DELAY,
    CONF_TYPE_END,
    CONF_TYPE_OTHER,
    CONF_TYPE_MAX
} config_type_t;

typedef struct
{
    uint8_t *flash;
    uint8_t *eeprom;
    uint8_t *conf_word;

    int sz_flash;
    int sz_eeprom;
    int sz_conf_word;
} pic_data_t;

static inline void swap16(uint16_t *orig)
{
    uint8_t *data = (uint8_t *)orig;
    uint8_t tmp = data[0];
    data[0] = data[1];
    data[1] = tmp;
}

void dump(const char *data, int len);
#endif