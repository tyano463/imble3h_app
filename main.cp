#line 1 "C:/workspace/microc/12f683/main.c"
#pragma config FOSC = INTOSCIO
#pragma config WDTE = OFF
#pragma config PWRTE = OFF
#pragma config MCLRE = OFF
#pragma config CP = OFF
#pragma config CPD = OFF
#pragma config BOREN = OFF
#pragma config IESO = OFF
#pragma config FCMEN = OFF
#line 27 "C:/workspace/microc/12f683/main.c"
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
 TRISIO = 0x34;
 ANSEL = 4;
 ADCON0 = 0x85;
 WPU = 0x30;
 T2CON = 0x4;
 CMCON0 = 7;
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


 UART_write('T');
 UART_write('X');
 UART_write('D');
 UART_write('A');
 UART_write('\r');
 UART_write('\n');
 UART_write(' ');
 UART_write(' ');
 UART_write(' ');

 vc = b2c(vh,  0 );
 UART_write(vc);

 vc = b2c(vl,  1 );
 UART_write(vc);

 vc = b2c(vl,  0 );
 UART_write(vc);

 UART_write('\n');
 UART_write('\0');

 __asm BCF 3, 5;
 __asm MOVLW  0xa0 ;
 __asm MOVWF  0x50 ;
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
 __asm MOVF  0x50 ;
 __asm BSF 3, 5;
 __asm MOVWF PR2;
 __asm BCF 3, 5;
 __asm CLRF TMR2;
 __asm BSF T2CON, 2;
 __asm sleep_loop: ;
 __asm MOVF TMR2;
 __asm SUBWF  0x50 , 0;
 __asm BTFSC STATUS, 1;
 __asm GOTO sleep_loop;
}

static void UART_write(char send_char)
{
 GPIO.B1 = 0;
 __asm BCF 3, 5;
 __asm MOVLW  0x5C ;
 __asm MOVWF  0x50 ;

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
 __asm MOVLW  0x5C ;
 __asm MOVWF  0x50 ;

 usleep();
 }
 GPIO.B1 = 1;
 __asm BCF 3, 5;
 __asm MOVLW  0xa0 ;
 __asm MOVWF  0x50 ;
 usleep();
}

static void read_analog()
{
 __asm BCF 3, 5;
 __asm MOVLW 0x87;
 __asm MOVWF ADCON0;
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
