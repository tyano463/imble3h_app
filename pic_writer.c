#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <stdint.h>
#include "pic_common.h"
#include "pic_serial.h"

#define BUF_SIZE 256

typedef struct
{
    uint16_t pm_addr;
    uint16_t dm_addr;
    int conf_word_size;
} settings_t;

typedef struct
{
    uint8_t size;
    uint16_t addr;
    uint8_t rtype;
    uint8_t data[];
} __attribute__((packed)) intel_hex_t;

char *g_comm_port = NULL;
char *g_file_name = NULL;

void usage()
{
    const char *s = R"(
usage:
    sudo ./pic_writer [option] hex_file

    option:
        --port:
            ex.) --port=/dev/ttyUSB0
)";
    printf("%s", s);
}

bool writeable()
{
    return getuid() == 0;
}

bool arg_check(int argc, char *argv[])
{
    bool ret = false;
    int opt;
    while ((opt = getopt(argc, argv, "")) != -1)
    {
        switch (opt)
        {
        case 0: // --port オプション
            if (optarg)
            {
                g_comm_port = optarg; // port を保存
            }
            break;
        default:
            break;
        }
    }

    for (int i = optind; i < argc; i++)
    {
        g_file_name = argv[i];
        ret = true;
    }
    return ret;
}

config_type_t get_config_type(const char *s)
{
    if (!s || (strlen(s) < 3))
        return CONF_TYPE_NONE;

    if (strncmp("PIC", s, 3) == 0)
        return CONF_TYPE_PIC;
    else if (strcmp(s, "#BEGIN") == 0)
        return CONF_TYPE_BEGIN;
    else if (strcmp(s, "PGM_SIZE_WORD") == 0)
        return CONF_TYPE_PGM_SIZE_WORD;
    else if (strcmp(s, "EEPROM_BYTE") == 0)
        return CONF_TYPE_EEPROM_BYTE;
    else if (strcmp(s, "CONFIG1") == 0)
        return CONF_TYPE_CONFIG1;
    else if (strcmp(s, "CONFIG2") == 0)
        return CONF_TYPE_CONFIG2;
    else if (strcmp(s, "POWER_MODE") == 0)
        return CONF_TYPE_POWER_MODE;
    else if (strcmp(s, "PGM_TYPE") == 0)
        return CONF_TYPE_PGM_TYPE;
    else if (strcmp(s, "PACKAGE") == 0)
        return CONF_TYPE_PACKAGE;
    else if (strcmp(s, "COMMENT") == 0)
        return CONF_TYPE_NONE;
    else if (strcmp(s, "JP2") == 0)
        return CONF_TYPE_JP2;
    else if (strcmp(s, "FIRM") == 0)
        return CONF_TYPE_FIRM;
    else if (strcmp(s, "VDD_VPP_DELAY") == 0)
        return CONF_TYPE_VDD_VPP_DELAY;
    else if (strcmp(s, "#END") == 0)
        return CONF_TYPE_END;
    else
        return CONF_TYPE_OTHER;
}

settings_t *load_settings()
{
    settings_t *ret = NULL;
    settings_t *s = NULL;
    FILE *fp = NULL;
    char buf[BUF_SIZE];
    const char *delim = " \t";
    char *token;
    int t, index;

    s = malloc(sizeof(settings_t));
    s->pm_addr = 0;
    s->dm_addr = 0;

    fp = fopen("settings.ini", "r");

    while (!feof(fp))
    {
        fgets(buf, sizeof(buf), fp);
        token = strtok(buf, delim);
        t = get_config_type(token);

        index = 0;
        while (token != NULL)
        {
            switch (t)
            {
            case CONF_TYPE_PGM_SIZE_WORD:
                if (index == 1)
                {
                    s->pm_addr = strtoul(token, NULL, 16);
                }
                break;
            case CONF_TYPE_EEPROM_BYTE:
                if (index == 1)
                {
                    s->dm_addr = strtoul(token, NULL, 16);
                }
                break;
            case CONF_TYPE_OTHER:
                if (index == 3)
                {
                    s->conf_word_size = strlen(token) - 2;
                }
                break;
            }

            token = strtok(NULL, delim);
            index++;
        }
    }

    if (s->pm_addr && s->dm_addr)
        ret = s;
error_return:
    if (!ret && s)
        free(s);
    if (fp)
        fclose(fp);
    return ret;
}

static uint8_t c2b(const char c)
{
    if ('0' <= c && c <= '9')
    {
        return c - '0';
    }
    else if ('a' <= c && c <= 'f')
    {
        return c - 'a' + 0xa;
    }
    else if ('A' <= c && c <= 'F')
    {
        return c - 'A' + 0xa;
    }
    else
    {
        return -1;
    }
}

static int intelhex2byte(const char *from, char *to)
{
    int i = 0, j;
    int converted = 0;
    uint8_t upper, lower, size, data;
    intel_hex_t *p;

    ERR_RETn(from[i++] != ':');

    upper = c2b(from[i++]);
    lower = c2b(from[i++]);
    ERR_RETp((upper >= 0x10 || lower >= 0x10), converted = 0);

    size = (upper << 4) | lower;
    to[converted++] = size;

    // address size:2, type:1, checksum:1
    for (j = 0; j < (size + 2 + 1 + 1); j++)
    {
        upper = c2b(from[i++]);
        lower = c2b(from[i++]);
        ERR_RETp(((upper >= 0x10) || (lower >= 0x10)), converted = 0);
        data = (upper << 4) | lower;

        to[converted++] = data;
    }

    p = (intel_hex_t *)to;
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Waddress-of-packed-member"
    swap16(&p->addr);
#pragma GCC diagnostic pop

    for (i = 0; i < (size >> 1); i++)
    {
        swap16((uint16_t *)&to[i * 2 + 4]);
    }

error_return:
    return converted;
}

static void set14bit(uint8_t *data, int size)
{
    uint8_t pattern[] = {0x3F, 0xFF};
    size_t pattern_size = sizeof(pattern);

    int i;
    for (i = 0; i < size; i += pattern_size)
    {
        memcpy(data + i, pattern, pattern_size);
    }
}

pic_data_t *load_from_file(const char *fpath, settings_t *settings)
{
    pic_data_t *ret = NULL, *data;
    char line[BUF_SIZE];
    char buf[32];
    int valid, len;
    intel_hex_t *p;
    int i;

    FILE *fp = fopen(fpath, "r");
    ERR_RETn(!fp);

    data = malloc(sizeof(pic_data_t));
    data->sz_eeprom = (settings->dm_addr + 1) * 2;
    data->sz_flash = (settings->pm_addr + 1) * 2;
    data->sz_conf_word = 0x20;
    data->eeprom = malloc(data->sz_eeprom);
    data->flash = malloc(data->sz_flash);
    data->conf_word = malloc(data->sz_conf_word);

    set14bit(data->eeprom, data->sz_eeprom);
    set14bit(data->flash, data->sz_flash);
    set14bit(data->conf_word, data->sz_conf_word);

    while (fgets(line, BUF_SIZE, fp))
    {
        len = strlen(line);
        for (i = len - 1; i >= 0; i--)
        {
            if (line[i] == '\r')
            {
                line[i] = '\0';
            }
            else if (line[i] == '\n')
            {
                line[i] = '\0';
            }
            else
            {
                break;
            }
        }
        len = strlen(line);
        if (len < 10)
            continue;

        valid = intelhex2byte(line, buf);
        if (!valid)
            continue;

        p = (intel_hex_t *)buf;
        // dump(buf, valid);
        // d("a:%04x t:%x sz:%x", p->addr, p->rtype, p->size);
        if (p->rtype)
            continue;

        if (p->addr > data->sz_flash)
        {
            if (p->addr > 0x4000)
            {
                memcpy(&data->conf_word[p->addr - 0x4000], p->data, p->size);
            }
            else
            {
                memcpy(&data->eeprom[p->addr - data->sz_flash], p->data, p->size);
            }
        }
        else
        {
            memcpy(&data->flash[p->addr], p->data, p->size);
        }
    }

    ret = data;
error_return:
    if (fp)
        fclose(fp);
    return ret;
}

void dump_pic_data(pic_data_t *p)
{
    d("%p (code, data, conf) = (%x, %x, %x)", p->sz_flash, p->sz_eeprom, p->sz_conf_word);

    d("#### code");
    dump(p->flash, p->sz_flash);
    d("#### data");
    dump(p->eeprom, p->sz_eeprom);
    d("#### conf");
    dump(p->conf_word, p->sz_conf_word);
}

int main(int argc, char *argv[])
{
    int status = 0;
    settings_t *settings;
    pic_data_t *data;

    ERR_RETp(!writeable(), usage());
    ERR_RETp(!arg_check(argc, argv), usage());

    settings = load_settings();
    ERR_RETp(!settings, status = NG);

    data = load_from_file(argv[1], settings);
    dump_pic_data(data);

    ERR_RETp(serial_setting(g_comm_port) != OK, printf("#### ERROR: serial open error\n"));

    ERR_RETp(serial_check(), printf("#### ERROR: pic check error\n"));

    ERR_RETp(serial_mode_set(), printf("#### ERROR: mD set error\n"))

    ERR_RETp(serial_read_all(), printf("#### ERROR: read error\n"));

    ERR_RETp(serial_write_all(data), printf("#### ERROR: write error\n"));

error_return:
    serial_close();
    return status;
}