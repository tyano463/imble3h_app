GOTO main

led_off:
    ;BANKSEL 0
    BCF GPIO 0
    RETURN

led_on:
    ;BANKSEL 0
    BSF GPIO 0
    RETURN

read_analog:
    BSF ADCON0 GO ;Start conversion
    BTFSC ADCON0 GO ;Is conversion done?
    GOTO -1 ;No, test again
    ; BANKSEL 0
    MOVF ADRESH, 1
    MOVWF GP40
    ; BANKSEL 1
    MOVF ADRESL, 1
    MOVWF GP41 ;Store in GPR space
    RETURN

save_const:
    ;BANKSEL 0
    MOVLW 'T'
    MOVWF GP7f
    MOVLW 'X'
    MOVWF GP7e
    MOVLW 'D'
    MOVWF GP7d
    MOVLW 'A'
    MOVWF GP7c
    MOVLW '\r'
    MOVWF GP7b
    MOVLW '\n'
    MOVWF GP7a
    MOVLW '\0'
    MOVWF GP79
    RETURN

delay_us:
    ; GP20
    MOVLW 0
    MOVWF TMR2
    MOVF GP20, 1
    MOVWF PR2
    BCF PIR1 TMR2IF
    BSF T2CON TMR2ON
    BTFSS PIR1 TMR2IF
    GOTO -1
    BCF T2CON TMR2ON
    RETURN

UART_write:
    ;GP30
    
    ; start bit
    BCF GPIO 1
    MOVLW 68
    MOVWF GP20
    CALL delay_us

    BTFSC GP30 0
    GOTO +3
    BSF GPIO 0
    GOTO +2
    BCF GPIO 1
    
    MOVLW 68
    MOVWF GP20
    CALL delay_us

    BTFSC GP30 1
    GOTO +3
    BSF GPIO 0
    GOTO +2
    BCF GPIO 1
    
    MOVLW 68
    MOVWF GP20
    CALL delay_us

    BTFSC GP30 2
    GOTO +3
    BSF GPIO 0
    GOTO +2
    BCF GPIO 1
    
    MOVLW 68
    MOVWF GP20
    CALL delay_us

    BTFSC GP30 3
    GOTO +3
    BSF GPIO 0
    GOTO +2
    BCF GPIO 1
    
    MOVLW 68
    MOVWF GP20
    CALL delay_us

    BTFSC GP30 4
    GOTO +3
    BSF GPIO 0
    GOTO +2
    BCF GPIO 1
    
    MOVLW 68
    MOVWF GP20
    CALL delay_us

    BTFSC GP30 5
    GOTO +3
    BSF GPIO 0
    GOTO +2
    BCF GPIO 1
    
    MOVLW 68
    MOVWF GP20
    CALL delay_us

    BTFSC GP30 6
    GOTO +3
    BSF GPIO 0
    GOTO +2
    BCF GPIO 1
    
    MOVLW 68
    MOVWF GP20
    CALL delay_us

    BTFSC GP30 7
    GOTO +3
    BSF GPIO 0
    GOTO +2
    BCF GPIO 1
    
    MOVLW 68
    MOVWF GP20
    CALL delay_us

    RETURN

main:
    ; BANKSEL 1
    MOVLW 70
    MOVWF OSCCON

    MOVLW 34
    MOVWF TRISIO

    MOVLW 74
    IORWF ANSEL, 0 ; and GP0 as analog
    
    ; BANKSEL 0
    MOVLW 89 ; Right justify, AN2, ADON
    MOVWF ADCON0

    MOVLW 2
    MOVWF T2CON

    BSF GPIO 1

    CALL save_const

    CALL led_off

loop:
    BTFSC GPIO 5 ; skip if clear
    GOTO loop 

    CALL led_on

wait_button:
    BTFSS GPIO 5
    GOTO wait_button

    call read_analog

    ; BANKSEL 0
    BCF GPIO 1

    MOVLW 68
    MOVF GP20, 1
    CALL delay_us

;txda\r\n start
    MOVF GP7f, 1
    MOVWF GP30
    CALL UART_write

    MOVF GP7e, 1
    MOVWF GP30
    CALL UART_write

    MOVF GP7d, 1
    MOVWF GP30
    CALL UART_write
    
    MOVF GP7c, 1
    MOVWF GP30
    CALL UART_write

    MOVF GP7b, 1
    MOVWF GP30
    CALL UART_write

    MOVF GP7a, 1
    MOVWF GP30
    CALL UART_write

    MOVF GP40, 1
    ADDLW '0'
    MOVWF GP30
    CALL UART_write
    
    MOVF GP41, 1
    MOVWF GP30
    SWAPF GP30, 0
    ANDLW f
    ADDLW '0'
    MOVWF GP30
    CALL UART_write

    MOVF GP41, 1
    MOVWF GP30
    MOVF GP30, 1
    ANDLW f
    ADDLW '0'
    MOVWF GP30
    CALL UART_write

    MOVF GP79, 1
    MOVWF GP30
    CALL UART_write

    ; BANKSEL 0
    BSF GPIO 1

    MOVLW d0
    MOVF GP20, 1
    CALL delay_us

;txda\r\n end

    CALL led_off
    GOTO loop
