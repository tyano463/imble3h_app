/*
 * File:   main.c
 * Author: tyano
 *
 * Created on January 31, 2025, 3:12 PM
 */

// CONFIG
#pragma config FOSC = INTOSCIO // Oscillator Selection bits (INTOSCIO oscillator: I/O function on RA4/OSC2/CLKOUT pin, I/O function on RA5/OSC1/CLKIN)
#pragma config WDTE = OFF      // Watchdog Timer Enable bit (WDT disabled)
#pragma config PWRTE = OFF     // Power-up Timer Enable bit (PWRT disabled)
#pragma config MCLRE = OFF     // MCLR Pin Function Select bit (MCLR pin function is digital input, MCLR internally tied to VDD)
#pragma config CP = OFF        // Code Protection bit (Program memory code protection is disabled)
#pragma config CPD = OFF       // Data Code Protection bit (Data memory code protection is disabled)
#pragma config BOREN = OFF     // Brown Out Detect (BOR disabled)
#pragma config IESO = OFF      // Internal External Switchover bit (Internal External Switchover mode is disabled)
#pragma config FCMEN = OFF     // Fail-Safe Clock Monitor Enabled bit (Fail-Safe Clock Monitor is disabled)

#define _XTAL_FREQ 8000000

#define BIT_WAIT_50us 0x5C     // 0x64 - 4us
#define BIT_WAIT_100us 0xa0
#define REG_SLEEP 0x50
#define HIGH_NIBBLE 1
#define LOW_NIBBLE 0

int i, j;
char button, temp, temp2, cnt, vh, vl, vc;
static void led_on(void);
static void led_off(void);
static void UART_init(void);
static void UART_write(char);
static void UART_send(const char *s);
static void read_analog(void);
static void usleep(void);
static char get_button_state(void);
static char b2c(char, int);

void main()
{
     OSCCON = 0x70;
     TRISIO = 0x34; // input: GP2,GP4,GP5 output:GP0,GP1
     ANSEL = 4;     // GP2 analog
     ADCON0 = 0x85; // Right justified, AN2, ADON
     WPU = 0x30;
     T2CON = 0x4; // f/1, TMR2m on
     CMCON0 = 7;  // AN2
     led_off();
     UART_init();

     button = 1;
     while (1)
     {
          temp = get_button_state();
          if (button == temp)
               continue;
          button = temp;

          if (!button)
          {
               read_analog();

               // UART_send("TXDA\r\n   123\n\0");
               UART_write('T');
               UART_write('X');
               UART_write('D');
               UART_write('A');
               UART_write('\r');
               UART_write('\n');
               UART_write(' ');
               UART_write(' ');
               UART_write(' ');

               vc = b2c(vh, LOW_NIBBLE);
               UART_write(vc);

               vc = b2c(vl, HIGH_NIBBLE);
               UART_write(vc);

               vc = b2c(vl, LOW_NIBBLE);
               UART_write(vc);

               UART_write('\n');
               UART_write('\0');

               __asm BCF 3, 5;
               __asm MOVLW BIT_WAIT_100us;
               __asm MOVWF REG_SLEEP;
               usleep();

          }
     }
}

static void led_on()
{
     GPIO.B0 = 1;
}
static void led_off()
{
     GPIO.B0 = 0;
}

static void UART_init()
{
     GPIO.B1 = 1;
}

static void UART_send(const char *s)
{
     for (i = 0; s[i]; i++)
     {
          UART_write(s[i]);
     }
}

static void usleep(void)
{
     __asm BCF 3, 5;
     __asm MOVF REG_SLEEP;
     __asm BSF 3, 5;
     __asm MOVWF PR2;
     __asm BCF 3, 5;
     __asm CLRF TMR2;
     __asm BSF T2CON, 2;
     __asm sleep_loop: ;
     __asm MOVF TMR2;
     __asm SUBWF REG_SLEEP, 0;
     __asm BTFSC STATUS, 1;
     __asm GOTO sleep_loop;
}

static void UART_write(char send_char)
{
     GPIO.B1 = 0;
     __asm BCF 3, 5;
     __asm MOVLW BIT_WAIT_50us;
     __asm MOVWF REG_SLEEP;

     usleep();
     for (j = 0; j < 8; j++)
     {
          if (send_char & (1 << j))
          {
               GPIO.B1 = 1;
          }
          else
          {
               GPIO.B1 = 0;
          }
          __asm BCF 3, 5;
          __asm MOVLW BIT_WAIT_50us;
          __asm MOVWF REG_SLEEP;

          usleep();
     }
     GPIO.B1 = 1;
     __asm BCF 3, 5;
     __asm MOVLW BIT_WAIT_100us;
     __asm MOVWF REG_SLEEP;
     usleep();
}

static void read_analog()
{
     __asm BCF 3, 5; // bank 0
     __asm MOVLW 0x87;
     __asm MOVWF ADCON0; // Right justified, AN2, ADON, GO
     __asm analog_loop: ;
     __asm BTFSC ADCON0, 1;
     __asm GOTO analog_loop;

     vh = ADRESH;
     vl = ADRESL;
}

static char get_button_state(void)
{
     cnt = 0;
     temp = GPIO.B5;

     TMR2 = 0;
     PR2 = 0x60;
     T2CON.B2 = 1;
     while (TMR2 < 0x60)
     {
          temp2 = GPIO.B5;
          if (!temp2)
          {
               cnt++;
          }
     }

     if (cnt > 10)
     {
          temp = 0;
          led_on();
     }
     else
     {
          temp = 1;
          led_off();
     }
     T2CON.B2 = 0;
     while (!GPIO.B5)
          ;

     return temp;
}

static char b2c(char b, int d)
{

     if (d)
     {
          temp2 = (b & 0xF0) >> 4;
     }
     else
     {
          temp2 = (b & 0xF);
     }

     if (temp2 < 0xa)
     {
          temp2 += '0';
     }
     else
     {
          temp2 = temp2 - 0xa + 'A';
     }
     return temp2;
}