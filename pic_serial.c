#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <dirent.h>
#include <sys/select.h>
#include <sys/time.h>
#include "pic_serial.h"

#define MAX_PATH 512
#define TIME_OUT 2

static int g_fd = -1;
static struct timeval g_timeout;

static void set_timeout(struct timeval *t)
{
    t->tv_sec = TIME_OUT;
    t->tv_usec = 0;
}

int serial_open(const char *port)
{
    const char *device = port;
    int fd = open(device, O_RDWR | O_NOCTTY);

    if (fd == -1)
    {
        return NG;
    }

    struct termios options;
    if (tcgetattr(fd, &options) == -1)
    {
        close(fd);
        return NG;
    }

    // ボーレートを57600に設定
    cfsetispeed(&options, B57600);
    cfsetospeed(&options, B57600);

    options.c_cflag &= ~PARENB;        // パリティなし
    options.c_cflag &= ~CSTOPB;        // ストップビット1
    options.c_cflag &= ~CSIZE;         // データビットマスクをクリア
    options.c_cflag |= CS8;            // データビット8
    options.c_cflag &= ~CRTSCTS;       // ハードウェアフロー制御なし
    options.c_cflag |= CREAD | CLOCAL; // 受信を有効化し、ローカル接続に設定

    // 入出力設定
    options.c_iflag &= ~(IXON | IXOFF | IXANY);         // ソフトウェアフロー制御なし
    options.c_iflag &= ~ICANON;                         // Canonical mode (行単位での入力) を無効化
    options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG); // 入力エコーなし
    options.c_oflag &= ~OPOST;                          // 出力処理なし

    // 入力のタイムアウトを設定
    options.c_cc[VMIN] = 1;  // 最低1文字の入力を待つ
    options.c_cc[VTIME] = 0; // タイムアウトなし

    // 設定を適用
    if (tcsetattr(fd, TCSANOW, &options) == -1)
    {
        close(fd);
        return NG;
    }
    g_fd = fd;

    set_timeout(&g_timeout);
    return OK;
}

static char **get_port_list()
{
    char **ret = NULL;
    char **list = NULL;
    struct dirent *entry;
    int devcnt = 0;
    int i;

    DIR *dp = opendir("/dev");

    ERR_RETn(!dp);

    list = MALLOC2d(char, MAX_PATH, 10);

    while ((entry = readdir(dp)))
    {
        if (strncmp(entry->d_name, "ttyUSB", 6) == 0)
        {
            list[devcnt++] = strdup(entry->d_name);
        }
    }

    if (devcnt > 0)
    {
        ret = list;
        list[devcnt] = NULL;
    }

error_return:
    return ret;
}

static char *get_port(const char *_port)
{
    char **list;
    char *port = NULL;
    int i;

    list = get_port_list();
    ERR_RETn(!list);

    d("%s", list[0]);
    if (!_port)
    {
        if (list)
        {
            port = malloc(strlen(list[0] + 8));
            sprintf(port, "/dev/%s", list[0]);
        }
    }
    else
    {
        for (i = 0; list[i]; i++)
        {
            if (strcmp(&_port[5], list[i]) == 0)
            {
                port = malloc(strlen(list[0] + 8));
                sprintf(port, "/dev/%s", list[0]);
                break;
            }
        }
    }

error_return:
    if (list)
        free(list);
    return port;
}

int serial_setting(const char *_port)
{
    int ret = NG;
    char *port = get_port(_port);
    ERR_RETp(!port, printf("#ERROR: port not specified\n"));

    ret = serial_open(port);

error_return:
    if (port)
        free(port);
    return ret;
}

int serial_close(void)
{
    if (g_fd >= 0)
    {
        close(g_fd);
        g_fd = -1;
    }
    else
    {
        d("");
    }
}

int serial_read_count(int fd, char *buf, int length, struct timeval *timeout)
{
    fd_set read_fds;
    struct timeval start_time, current_time, elapsed_time, remaining_time;
    size_t total_read = 0;
    ssize_t bytes_read;

    // 開始時間を取得
    gettimeofday(&start_time, NULL);

    while (total_read < length)
    {
        FD_ZERO(&read_fds);
        FD_SET(fd, &read_fds);

        // 現在の時間を取得
        gettimeofday(&current_time, NULL);

        // 経過時間を計算
        timersub(&current_time, &start_time, &elapsed_time);

        // 残り時間を計算
        if (timercmp(&elapsed_time, timeout, <))
        {
            timersub(timeout, &elapsed_time, &remaining_time);
        }
        else
        {
            printf("Timeout occurred! Only %zu bytes read.\n", total_read);
            return -1;
        }

        int ret = select(fd + 1, &read_fds, NULL, NULL, &remaining_time);
        if (ret == -1)
        {
            perror("select");
            return -1;
        }
        else if (ret == 0)
        {
            printf("Timeout occurred! Only %zu bytes read.\n", total_read);
            return -1;
        }
        else
        {
            if (FD_ISSET(fd, &read_fds))
            {
                bytes_read = read(fd, buf + total_read, length - total_read);
                if (bytes_read == -1)
                {
                    perror("read");
                    return -1;
                }
                else if (bytes_read == 0)
                {
                    break; // EOF
                }
                total_read += bytes_read;
            }
        }
    }

    return total_read;
}

int serial_read_char(int fd, char *_buf, char expect, struct timeval *timeout)
{
    int i = 0;
    char buf[8];
    int count = 0;
    while (1)
    {
        // selectを使ってタイムアウトを設定
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(fd, &read_fds);
        timeout->tv_sec = 1;

        if (!timeout->tv_sec)
            printf("### %d", __LINE__);
        // d("to:%d", timeout->tv_sec);
        int ret = select(fd + 1, &read_fds, NULL, NULL, timeout);
        if (ret == -1)
        {
            d("");
            return NG;
        }
        else if (ret == 0)
        {
            if (count++ > 5)
            {
                if (!timeout->tv_sec)
                    printf("### %d to:%d\n", __LINE__, timeout->tv_sec);
                // d("to:%d", timeout->tv_sec);
                return i;
            }
            continue;
        }

        // データが読み込める状態になった場合
        // d("");
        if (FD_ISSET(g_fd, &read_fds))
        {
            int bytes_read = read(g_fd, buf, 1);
            if (bytes_read == -1)
            {
                d("");
                return NG;
            }

            memcpy(&_buf[i], buf, bytes_read);
            i += bytes_read;
            if (buf[0] == expect)
                break;
        }
    }
    return i;
}

#define DUMP_LINE_WIDTH 16

// バイトのダンプを行うマクロ
#define DUMP_BYTE(b) printf("%02x ", (unsigned char)(b))

// ダンプの形式を管理する関数
void dump(const char *data, int len)
{
    fflush(stdout);
    for (int i = 0; i < len; i++)
    {
        if (i % DUMP_LINE_WIDTH == 0)
        {
            if (i != 0)
            {
                printf("  ");
                for (int j = i - DUMP_LINE_WIDTH; j < i; j++)
                {
                    printf("%c", (data[j] >= 32 && data[j] <= 126) ? data[j] : '.');
                }
            }
            printf("\n%08x ", i);
        }
        DUMP_BYTE(data[i]);
    }
    // 最後の行に対する処理
    int remainder = len % DUMP_LINE_WIDTH;
    if (remainder != 0)
    {
        for (int i = 0; i < DUMP_LINE_WIDTH - remainder; i++)
        {
            printf("   ");
        }
        printf("  ");
        for (int i = len - remainder; i < len; i++)
        {
            printf("%c", (data[i] >= 32 && data[i] <= 126) ? data[i] : '.');
        }
    }
    printf("\n");
    fflush(stdout);
}

int serial_check(void)
{
    int ret = NG;
    char buf[0x20];
    char writer[0x20];
    char *p;
    int readed;

    d("");
    ERR_RETn(g_fd < 0);

    write(g_fd, "***?", 4);
    p = writer;

    d("");
    readed = serial_read_char(g_fd, buf, '@', &g_timeout);
    ERR_RETp(readed < 1, printf("#### ERROR serial check\n"));

    dump(buf, readed);

    if (strncmp("AE-PGM877", buf, 9) == 0)
        ret = OK;
error_return:
    return ret;
}

int serial_mode_set(void)
{
    int ret = NG;
    char buf[8];
    int readed;
    ERR_RETn(g_fd < 0);

    write(g_fd, "mD\n", 3);
    readed = serial_read_char(g_fd, buf, '\n', &g_timeout);
    ERR_RETp(readed != 1, printf("#### ERROR mode set\n"));

    ret = OK;
error_return:
    return ret;
}

static int read_configuration_word(char *buf)
{
    int readed, status;

    memcpy(buf, "nrsc", 4);
    buf[4] = 0;
    buf[5] = 8;
    buf[6] = '@';
    d("### send nrsc");
    // dump(buf, 7);
    write(g_fd, buf, 7);
    readed = serial_read_char(g_fd, buf, '@', &g_timeout);

    memcpy(buf, "nbs", 3);
    buf[3] = 8;
    buf[4] = 0;
    d("### send nbs");
    // dump(buf, 5);
    write(g_fd, buf, 5);
    status = serial_read_char(g_fd, buf, '@', &g_timeout);
    ERR_RETn(!readed);

error_return:
    return readed;
}

static int read_flash_memory(char *buf)
{
    const int end_addr = 0x3fff;
    int i;
    int sz_block;
    int readed;

    sz_block = (end_addr + 1) / 16 + ((end_addr + 1) % 16);
    memcpy(buf, "nrsp", 4);
    buf[4] = 8;
    buf[5] = 0;
    for (i = 0; i < sz_block; i++)
    {
        buf[i + 6] = '@';
    }
    d("### send nrsp");
    // dump(buf, 6 + sz_block);
    write(g_fd, buf, sz_block + 4 + 2);

    readed = serial_read_char(g_fd, buf, '@', &g_timeout);
    return readed;
}

static int read_eeprom(char *buf)
{
    const int end_addr = 0xff;
    int i;
    int sz_block;
    int readed, status;

    sz_block = (end_addr + 1) / 8 + ((end_addr + 1) % 8);
    memcpy(buf, "nrsd", 4);
    buf[4] = 1;
    buf[5] = 0;
    for (i = 0; i < sz_block; i++)
    {
        buf[i + 6] = '@';
    }
    d("### send nrsd %d", sz_block);
    write(g_fd, buf, sz_block + 4 + 2);

    readed = serial_read_char(g_fd, buf, '@', &g_timeout);
error_return:
    d("readed:%d", readed);
    return readed;
}

int serial_read_all(void)
{
    int ret = NG;
    char *buf = NULL;
    int readed;
    int i;

    buf = malloc(0x1000);
    ERR_RETn(g_fd < 0);

    readed = read_configuration_word(buf);
    ERR_RETn(readed <= 16);

    d("### configuration");
    dump(buf, readed);

    readed = read_flash_memory(buf);
    ERR_RETn(readed <= 0);

    d("#### code block sz:%x", readed);
    dump(buf, readed);

    readed = read_eeprom(buf);
    ERR_RETn(readed <= 0);

    d("#### eeprom:%x", readed);
    dump(buf, readed);

    ret = OK;
error_return:
    if (buf)
        free(buf);
    return ret;
}

static int write_flash_memory(pic_data_t *data)
{
    char *buf;
    int readed, i, ret;
    char expect;

    ret = NG;

    buf = malloc(BUFSIZ);

    memcpy(buf, "nbd", 3);
    buf[3] = 0xe;
    buf[4] = 0;
    write(g_fd, buf, 5);
    readed = serial_read_char(g_fd, buf, '@', &g_timeout);
    ERR_RETp(!readed, printf("### ERROR: 1st nbd failed.\n"));

    memcpy(buf, "nbd", 3);
    buf[3] = 0xf;
    buf[4] = 0;
    write(g_fd, buf, 5);
    readed = serial_read_char(g_fd, buf, '@', &g_timeout);
    ERR_RETp(!readed, printf("### ERROR: 2nd nbd failed.\n"));

    memcpy(buf, "nwhe", 3);
    buf[3] = 8;
    buf[4] = 0;
    write(g_fd, buf, 5);
    readed = serial_read_char(g_fd, buf, '\0', &g_timeout);
    ERR_RETp(!readed, printf("### ERROR: 2nd nbd failed.\n"));

    expect = 1;
    for (i = 0; i < data->sz_flash; i += 2)
    {
        memcpy(buf, &data->flash[i], 2);
        readed = serial_read_count(g_fd, buf, expect, &g_timeout);
        ERR_RETp(!readed, printf("### ERROR: write failed @%04x: %02x %02x", i, data->flash[i], data->flash[i + 1]));
    }

    ret = OK;
error_return:
    return readed;
}

int serial_write_all(pic_data_t *data)
{
    int ret = NG;
    int readed;
    readed = write_flash_memory(data);

    ret = OK;
error_return:
    return ret;
}