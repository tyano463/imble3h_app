
_main:

;main.c,39 :: 		void main()
;main.c,41 :: 		OSCCON = 0x70;
	MOVLW      112
	MOVWF      IRCF2_bit
;main.c,42 :: 		TRISIO = 0x34; // input: GP2,GP4,GP5 output:GP0,GP1
	MOVLW      52
	MOVWF      TRISIO0_bit
;main.c,43 :: 		ANSEL = 4;     // GP2 analog
	MOVLW      4
	MOVWF      ADCS2_bit
;main.c,44 :: 		ADCON0 = 0x85; // Right justified, AN2, ADON
	MOVLW      133
	MOVWF      GO_DONE_bit
;main.c,45 :: 		WPU = 0x30;
	MOVLW      48
	MOVWF      WPUA5_bit
;main.c,46 :: 		T2CON = 0x4; // f/1, TMR2m on
	MOVLW      4
	MOVWF      TOUTPS3_bit
;main.c,47 :: 		CMCON0 = 7;  // AN2
	MOVLW      7
	MOVWF      CM2_bit
;main.c,48 :: 		led_off();
	CALL       main_led_off+0
;main.c,49 :: 		UART_init();
	CALL       main_UART_init+0
;main.c,51 :: 		button = 1;
	MOVLW      1
	MOVWF      _button+0
;main.c,52 :: 		while (1)
L_main0:
;main.c,54 :: 		temp = get_button_state();
	CALL       main_get_button_state+0
	MOVF       R0+0, 0
	MOVWF      _temp+0
;main.c,55 :: 		if (button == temp)
	MOVF       _button+0, 0
	XORWF      R0+0, 0
	BTFSS      RP1_bit, 2
	GOTO       L_main2
;main.c,56 :: 		continue;
	GOTO       L_main0
L_main2:
;main.c,57 :: 		button = temp;
	MOVF       _temp+0, 0
	MOVWF      _button+0
;main.c,59 :: 		if (!button)
	MOVF       _temp+0, 0
	BTFSS      RP1_bit, 2
	GOTO       L_main3
;main.c,61 :: 		read_analog();
	CALL       main_read_analog+0
;main.c,64 :: 		UART_write('T');
	MOVLW      84
	MOVWF      FARG_main_UART_write+0
	CALL       main_UART_write+0
;main.c,65 :: 		UART_write('X');
	MOVLW      88
	MOVWF      FARG_main_UART_write+0
	CALL       main_UART_write+0
;main.c,66 :: 		UART_write('D');
	MOVLW      68
	MOVWF      FARG_main_UART_write+0
	CALL       main_UART_write+0
;main.c,67 :: 		UART_write('A');
	MOVLW      65
	MOVWF      FARG_main_UART_write+0
	CALL       main_UART_write+0
;main.c,68 :: 		UART_write('\r');
	MOVLW      13
	MOVWF      FARG_main_UART_write+0
	CALL       main_UART_write+0
;main.c,69 :: 		UART_write('\n');
	MOVLW      10
	MOVWF      FARG_main_UART_write+0
	CALL       main_UART_write+0
;main.c,70 :: 		UART_write(' ');
	MOVLW      32
	MOVWF      FARG_main_UART_write+0
	CALL       main_UART_write+0
;main.c,71 :: 		UART_write(' ');
	MOVLW      32
	MOVWF      FARG_main_UART_write+0
	CALL       main_UART_write+0
;main.c,72 :: 		UART_write(' ');
	MOVLW      32
	MOVWF      FARG_main_UART_write+0
	CALL       main_UART_write+0
;main.c,74 :: 		vc = b2c(vh, LOW_NIBBLE);
	MOVF       _vh+0, 0
	MOVWF      FARG_main_b2c+0
	CLRF       FARG_main_b2c+0
	CLRF       FARG_main_b2c+1
	CALL       main_b2c+0
	MOVF       R0+0, 0
	MOVWF      _vc+0
;main.c,75 :: 		UART_write(vc);
	MOVF       R0+0, 0
	MOVWF      FARG_main_UART_write+0
	CALL       main_UART_write+0
;main.c,77 :: 		vc = b2c(vl, HIGH_NIBBLE);
	MOVF       _vl+0, 0
	MOVWF      FARG_main_b2c+0
	MOVLW      1
	MOVWF      FARG_main_b2c+0
	MOVLW      0
	MOVWF      FARG_main_b2c+1
	CALL       main_b2c+0
	MOVF       R0+0, 0
	MOVWF      _vc+0
;main.c,78 :: 		UART_write(vc);
	MOVF       R0+0, 0
	MOVWF      FARG_main_UART_write+0
	CALL       main_UART_write+0
;main.c,80 :: 		vc = b2c(vl, LOW_NIBBLE);
	MOVF       _vl+0, 0
	MOVWF      FARG_main_b2c+0
	CLRF       FARG_main_b2c+0
	CLRF       FARG_main_b2c+1
	CALL       main_b2c+0
	MOVF       R0+0, 0
	MOVWF      _vc+0
;main.c,81 :: 		UART_write(vc);
	MOVF       R0+0, 0
	MOVWF      FARG_main_UART_write+0
	CALL       main_UART_write+0
;main.c,83 :: 		UART_write('\n');
	MOVLW      10
	MOVWF      FARG_main_UART_write+0
	CALL       main_UART_write+0
;main.c,84 :: 		UART_write('\0');
	CLRF       FARG_main_UART_write+0
	CALL       main_UART_write+0
;main.c,86 :: 		__asm BCF 3, 5;
	BCF        RP1_bit, 5
;main.c,87 :: 		__asm MOVLW BIT_WAIT_100us;
	MOVLW      160
;main.c,88 :: 		__asm MOVWF REG_SLEEP;
	MOVWF      80
;main.c,89 :: 		usleep();
	CALL       main_usleep+0
;main.c,91 :: 		}
L_main3:
;main.c,92 :: 		}
	GOTO       L_main0
;main.c,93 :: 		}
L_end_main:
	GOTO       $+0
; end of _main

main_led_on:

;main.c,95 :: 		static void led_on()
;main.c,97 :: 		GPIO.B0 = 1;
	BSF        GP0_bit, 0
;main.c,98 :: 		}
L_end_led_on:
	RETURN
; end of main_led_on

main_led_off:

;main.c,99 :: 		static void led_off()
;main.c,101 :: 		GPIO.B0 = 0;
	BCF        GP0_bit, 0
;main.c,102 :: 		}
L_end_led_off:
	RETURN
; end of main_led_off

main_UART_init:

;main.c,104 :: 		static void UART_init()
;main.c,106 :: 		GPIO.B1 = 1;
	BSF        GP0_bit, 1
;main.c,107 :: 		}
L_end_UART_init:
	RETURN
; end of main_UART_init

main_UART_send:

;main.c,109 :: 		static void UART_send(const char *s)
;main.c,111 :: 		for (i = 0; s[i]; i++)
	CLRF       _i+0
	CLRF       _i+1
L_main_UART_send4:
	MOVF       _i+0, 0
	ADDWF      FARG_main_UART_send_s+0, 0
	MOVWF      R0+0
	MOVF       FARG_main_UART_send_s+1, 0
	BTFSC      RP1_bit, 0
	ADDLW      1
	ADDWF      _i+1, 0
	MOVWF      R0+1
	MOVF       R0+0, 0
	MOVWF      ___DoICPAddr+0
	MOVF       R0+1, 0
	MOVWF      ___DoICPAddr+1
	CALL       _____DoICP+0
	MOVWF      R0+0
	MOVF       R0+0, 0
	BTFSC      RP1_bit, 2
	GOTO       L_main_UART_send5
;main.c,113 :: 		UART_write(s[i]);
	MOVF       _i+0, 0
	ADDWF      FARG_main_UART_send_s+0, 0
	MOVWF      R0+0
	MOVF       FARG_main_UART_send_s+1, 0
	BTFSC      RP1_bit, 0
	ADDLW      1
	ADDWF      _i+1, 0
	MOVWF      R0+1
	MOVF       R0+0, 0
	MOVWF      ___DoICPAddr+0
	MOVF       R0+1, 0
	MOVWF      ___DoICPAddr+1
	CALL       _____DoICP+0
	MOVWF      FARG_main_UART_write+0
	CALL       main_UART_write+0
;main.c,111 :: 		for (i = 0; s[i]; i++)
	INCF       _i+0, 1
	BTFSC      RP1_bit, 2
	INCF       _i+1, 1
;main.c,114 :: 		}
	GOTO       L_main_UART_send4
L_main_UART_send5:
;main.c,115 :: 		}
L_end_UART_send:
	RETURN
; end of main_UART_send

main_usleep:

;main.c,117 :: 		static void usleep(void)
;main.c,119 :: 		__asm BCF 3, 5;
	BCF        RP1_bit, 5
;main.c,120 :: 		__asm MOVF REG_SLEEP;
	MOVF       80, 0
;main.c,121 :: 		__asm BSF 3, 5;
	BSF        RP1_bit, 5
;main.c,122 :: 		__asm MOVWF PR2;
	MOVWF      PR2
;main.c,123 :: 		__asm BCF 3, 5;
	BCF        RP1_bit, 5
;main.c,124 :: 		__asm CLRF TMR2;
	CLRF       TMR2
;main.c,125 :: 		__asm BSF T2CON, 2;
	BSF        TOUTPS3_bit, 2
;main.c,126 :: 		__asm sleep_loop: ;
sleep_loop:
;main.c,127 :: 		__asm MOVF TMR2;
	MOVF       TMR2, 0
;main.c,128 :: 		__asm SUBWF REG_SLEEP, 0;
	SUBWF      80, 0
;main.c,129 :: 		__asm BTFSC STATUS, 1;
	BTFSC      RP1_bit, 1
;main.c,130 :: 		__asm GOTO sleep_loop;
	GOTO       sleep_loop
;main.c,131 :: 		}
L_end_usleep:
	RETURN
; end of main_usleep

main_UART_write:

;main.c,133 :: 		static void UART_write(char send_char)
;main.c,135 :: 		GPIO.B1 = 0;
	BCF        GP0_bit, 1
;main.c,136 :: 		__asm BCF 3, 5;
	BCF        RP1_bit, 5
;main.c,137 :: 		__asm MOVLW BIT_WAIT_50us;
	MOVLW      100
;main.c,138 :: 		__asm MOVWF REG_SLEEP;
	MOVWF      80
;main.c,140 :: 		usleep();
	CALL       main_usleep+0
;main.c,141 :: 		for (j = 0; j < 8; j++)
	CLRF       _j+0
	CLRF       _j+1
L_main_UART_write8:
	MOVLW      128
	XORWF      _j+1, 0
	MOVWF      R0+0
	MOVLW      128
	SUBWF      R0+0, 0
	BTFSS      RP1_bit, 2
	GOTO       L_main_UART_write32
	MOVLW      8
	SUBWF      _j+0, 0
L_main_UART_write32:
	BTFSC      RP1_bit, 0
	GOTO       L_main_UART_write9
;main.c,143 :: 		if (send_char & (1 << j))
	MOVF       _j+0, 0
	MOVWF      R2+0
	MOVLW      1
	MOVWF      R0+0
	MOVLW      0
	MOVWF      R0+1
	MOVF       R2+0, 0
L_main_UART_write33:
	BTFSC      RP1_bit, 2
	GOTO       L_main_UART_write34
	RLF        R0+0, 1
	RLF        R0+1, 1
	BCF        R0+0, 0
	ADDLW      255
	GOTO       L_main_UART_write33
L_main_UART_write34:
	MOVF       FARG_main_UART_write_send_char+0, 0
	ANDWF      R0+0, 1
	MOVLW      0
	ANDWF      R0+1, 1
	MOVF       R0+0, 0
	IORWF      R0+1, 0
	BTFSC      RP1_bit, 2
	GOTO       L_main_UART_write11
;main.c,145 :: 		GPIO.B1 = 1;
	BSF        GP0_bit, 1
;main.c,146 :: 		}
	GOTO       L_main_UART_write12
L_main_UART_write11:
;main.c,149 :: 		GPIO.B1 = 0;
	BCF        GP0_bit, 1
;main.c,150 :: 		}
L_main_UART_write12:
;main.c,151 :: 		__asm BCF 3, 5;
	BCF        RP1_bit, 5
;main.c,152 :: 		__asm MOVLW BIT_WAIT_50us;
	MOVLW      100
;main.c,153 :: 		__asm MOVWF REG_SLEEP;
	MOVWF      80
;main.c,155 :: 		usleep();
	CALL       main_usleep+0
;main.c,141 :: 		for (j = 0; j < 8; j++)
	INCF       _j+0, 1
	BTFSC      RP1_bit, 2
	INCF       _j+1, 1
;main.c,156 :: 		}
	GOTO       L_main_UART_write8
L_main_UART_write9:
;main.c,157 :: 		GPIO.B1 = 1;
	BSF        GP0_bit, 1
;main.c,158 :: 		__asm BCF 3, 5;
	BCF        RP1_bit, 5
;main.c,159 :: 		__asm MOVLW BIT_WAIT_100us;
	MOVLW      160
;main.c,160 :: 		__asm MOVWF REG_SLEEP;
	MOVWF      80
;main.c,161 :: 		usleep();
	CALL       main_usleep+0
;main.c,162 :: 		}
L_end_UART_write:
	RETURN
; end of main_UART_write

main_read_analog:

;main.c,164 :: 		static void read_analog()
;main.c,166 :: 		__asm BCF 3, 5; // bank 0
	BCF        RP1_bit, 5
;main.c,167 :: 		__asm MOVLW 0x87;
	MOVLW      135
;main.c,168 :: 		__asm MOVWF ADCON0; // Right justified, AN2, ADON, GO
	MOVWF      GO_DONE_bit
;main.c,169 :: 		__asm analog_loop: ;
analog_loop:
;main.c,170 :: 		__asm BTFSC ADCON0, 1;
	BTFSC      GO_DONE_bit, 1
;main.c,171 :: 		__asm GOTO analog_loop;
	GOTO       analog_loop
;main.c,173 :: 		vh = ADRESH;
	MOVF       ADRESH, 0
	MOVWF      _vh+0
;main.c,174 :: 		vl = ADRESL;
	MOVF       ADRESL, 0
	MOVWF      _vl+0
;main.c,175 :: 		}
L_end_read_analog:
	RETURN
; end of main_read_analog

main_get_button_state:

;main.c,177 :: 		static char get_button_state(void)
;main.c,179 :: 		cnt = 0;
	CLRF       _cnt+0
;main.c,180 :: 		temp = GPIO.B5;
	MOVLW      0
	BTFSC      GP0_bit, 5
	MOVLW      1
	MOVWF      _temp+0
;main.c,182 :: 		TMR2 = 0;
	CLRF       TMR2
;main.c,183 :: 		PR2 = 0x60;
	MOVLW      96
	MOVWF      PR2
;main.c,184 :: 		T2CON.B2 = 1;
	BSF        TOUTPS3_bit, 2
;main.c,185 :: 		while (TMR2 < 0x60)
L_main_get_button_state14:
	MOVLW      96
	SUBWF      TMR2, 0
	BTFSC      RP1_bit, 0
	GOTO       L_main_get_button_state15
;main.c,187 :: 		temp2 = GPIO.B5;
	MOVLW      0
	BTFSC      GP0_bit, 5
	MOVLW      1
	MOVWF      _temp2+0
;main.c,188 :: 		if (!temp2)
	MOVF       _temp2+0, 0
	BTFSS      RP1_bit, 2
	GOTO       L_main_get_button_state16
;main.c,190 :: 		cnt++;
	INCF       _cnt+0, 1
;main.c,191 :: 		}
L_main_get_button_state16:
;main.c,192 :: 		}
	GOTO       L_main_get_button_state14
L_main_get_button_state15:
;main.c,194 :: 		if (cnt > 10)
	MOVF       _cnt+0, 0
	SUBLW      10
	BTFSC      RP1_bit, 0
	GOTO       L_main_get_button_state17
;main.c,196 :: 		temp = 0;
	CLRF       _temp+0
;main.c,197 :: 		led_on();
	CALL       main_led_on+0
;main.c,198 :: 		}
	GOTO       L_main_get_button_state18
L_main_get_button_state17:
;main.c,201 :: 		temp = 1;
	MOVLW      1
	MOVWF      _temp+0
;main.c,202 :: 		led_off();
	CALL       main_led_off+0
;main.c,203 :: 		}
L_main_get_button_state18:
;main.c,204 :: 		T2CON.B2 = 0;
	BCF        TOUTPS3_bit, 2
;main.c,205 :: 		while (!GPIO.B5)
L_main_get_button_state19:
	BTFSC      GP0_bit, 5
	GOTO       L_main_get_button_state20
;main.c,206 :: 		;
	GOTO       L_main_get_button_state19
L_main_get_button_state20:
;main.c,208 :: 		return temp;
	MOVF       _temp+0, 0
	MOVWF      R0+0
;main.c,209 :: 		}
L_end_get_button_state:
	RETURN
; end of main_get_button_state

main_b2c:

;main.c,211 :: 		static char b2c(char b, int d)
;main.c,214 :: 		if (d)
	MOVF       FARG_main_b2c_d+0, 0
	IORWF      FARG_main_b2c_d+1, 0
	BTFSC      RP1_bit, 2
	GOTO       L_main_b2c21
;main.c,216 :: 		temp2 = (b & 0xF0) >> 4;
	MOVLW      240
	ANDWF      FARG_main_b2c_b+0, 0
	MOVWF      _temp2+0
	RRF        _temp2+0, 1
	BCF        _temp2+0, 7
	RRF        _temp2+0, 1
	BCF        _temp2+0, 7
	RRF        _temp2+0, 1
	BCF        _temp2+0, 7
	RRF        _temp2+0, 1
	BCF        _temp2+0, 7
;main.c,217 :: 		}
	GOTO       L_main_b2c22
L_main_b2c21:
;main.c,220 :: 		temp2 = (b & 0xF);
	MOVLW      15
	ANDWF      FARG_main_b2c_b+0, 0
	MOVWF      _temp2+0
;main.c,221 :: 		}
L_main_b2c22:
;main.c,223 :: 		if (temp2 < 0xa)
	MOVLW      10
	SUBWF      _temp2+0, 0
	BTFSC      RP1_bit, 0
	GOTO       L_main_b2c23
;main.c,225 :: 		temp2 += '0';
	MOVLW      48
	ADDWF      _temp2+0, 1
;main.c,226 :: 		}
	GOTO       L_main_b2c24
L_main_b2c23:
;main.c,229 :: 		temp2 = temp2 - 0xa + 'A';
	MOVLW      10
	SUBWF      _temp2+0, 1
	MOVLW      65
	ADDWF      _temp2+0, 1
;main.c,230 :: 		}
L_main_b2c24:
;main.c,231 :: 		return temp2;
	MOVF       _temp2+0, 0
	MOVWF      R0+0
;main.c,232 :: 		}
L_end_b2c:
	RETURN
; end of main_b2c
