#!/usr/bin/env python3

import sys
import os
import re
import ast
import inspect

from functools import cmp_to_key

def usage():
    command = sys.argv[0]
    explain = f"""usage:
    {command} <file>
"""
    print(explain, end="")

def get_file_path():
    if len(sys.argv) != 2:
        return None
    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        return None
    return file_path

def d(s):
    frame = inspect.currentframe().f_back
    function_name = frame.f_code.co_name
    line_number = frame.f_lineno
    print(f"({line_number}) {function_name} ", end="")
    print(s)

registers = None
_registers = [ [
"00h	INDF									xxxx xxxx",
"01h	TMR0									xxxx xxxx",
"02h	PCL									0000 0000",
"03h	STATUS	IRP	RP1	RP0	TO	PD	Z	DC	C	0001 1xxx",
"04h	FSR									xxxx xxxx",
"05h	GPIO			GP5	GP4	GP3	GP2	GP1	GP0	--xx xxxx",
"0Ah	PCLATH									---0 0000",
"0Bh	INTCON	GIE	PEIE	T0IE	INTE	GPIE	T0IF	INTF	GPIF	0000 0000",
"0Ch	PIR1	EEIF	ADIF	CCP1IF		CMIF	OSFIF	TMR2IF	TMR1IF	0000 0000",
"0Eh	TMR1L									xxxx xxxx",
"0Fh	TMR1H									xxxx xxxx",
"10h	T1CON	T1GINV	TMR1GE	T1CKPS1	T1CKPS0	T1OSCEN	T1SYNC	TMR1CS	TMR1ON	0000 0000",
"11h	TMR2									0000 0000",
"12h	T2CON		TOUTPS3	TOUTPS2	TOUTPS1	TOUTPS0	TMR2ON	T2CKPS1	T2CKPS0	0000 0000",
"13h	CCPR1L									xxxx xxxx",
"14h	CCPR1H									xxxx xxxx",
"15h	CCP1CON			DC1B1	DC1B0	CCP1M3	CCP1M2	CCP1M1	CCP1M0	--00 0000",
"18h	WDTCON				WDTP3	WDTP2	WDTP1	WDTP0	SWDTEN	---0 1000",
"19h	CMCON0		COUT			CIS	CM2	CM1	CM0	0000 0000",
"1Ah	CMCON1							T1GSS	CMSYNC	---- --10",
"1Eh	ADRESH									xxxx xxxx",
"1Fh	ADCON0	ADFM	VCFG			CHS1	CHS0	GO	ADON	00-- 0000",
], [
"80h	INDF									xxxx xxxx",
"81h	OPTION_REG	GPPU	INTEGD	TOCS	TOSE	PSA	PS2	PS1	PS0	1111 1111",
"82h	PCL									0000 0000",
"83h	STATUS	IRP	RP1	RP0	TO	PD	Z	DC	C	0001 1xxx",
"84h	FSR									xxxx xxxx",
"85h	TRISIO			TRISIO5	TRISIO4	TRISIO3	TRISIO2	TRISIO1	TRISIO0	--11 1111",
"8Ah	PCLATH									---0 0000",
"8Bh	INTCON	GIE	PEIE	TOIE	INTE	GPIE	T0IF	INTF	GPIF	0000 0000",
"8Ch	PIE1	EEIE	ADIE	CCP1IE		CMIE	OSFIE	TMR2IE	TMR1IE	000- 0000",
"8Eh	PCON			ULPWUE	SBOREN			POR	BOR	--01 –qq",
"8Fh	OSCCON		IRCF2	IRCF1	IRCF0	OSTS	HTS	LTS	SCS	-110 x000",
"90h	OSCTUNE				TUN4	TUN3	TUN2	TUN1	TUN0	---0 0000",
"92h	PR2									1111 1111",
"95h	WPU			WPU5	WPU4		WPU2	WPU1	WPU0	--11 -111",
"96h	IOC			IOC5	IOC4	IOC3	IOC2	IOC1	IOC0	--00 0000",
"99h	VRCON	VREN		VRR		VR3	VR2	VR1	VR0	0-0- 0000",
"9Ah	EEDAT	EEDAT7	EEDAT6	EEDAT5	EEDAT4	EEDAT3	EEDAT2	EEDAT1	EEDAT0	0000 0000",
"9Bh	EEADR	EEADR7	EEADR6	EEADR5	EEADR4	EEADR3	EEADR2	EEADR1	EEADR0	0000 0000",
"9Ch	EECON1					WRERR	WREN	WR	RD	---- x000",
"9Dh	EECON2									---- ----",
"9Eh	ADRESL									xxxx xxxx",
"9Fh	ANSEL		ADCS2	ADCS1	ADCS0	ANS3	ANS2	ANS1	ANS0	-000 1111",
] ]

instructions = []
_instructions = [
"ADDWF	f, d	Add W and f	00	0111	dfff	ffff",
"ANDWF	f, d	AND W with f	00	0101	dfff	ffff",
"CLRF	f	Clear f	00	0001	lfff	ffff",
"CLRW	–	Clear W	00	0001	0xxx	xxxx",
"COMF	f, d	Complement f	00	1001	dfff	ffff",
"DECF	f, d	Decrement f	00	0011	dfff	ffff",
"DECFS	f, dZ	Decrement f, Skip if 0	00	1011	dfff	ffff",
"INCF	f, d	Increment f	00	1010	dfff	ffff",
"INCFS	f, dZ	Increment f, Skip if 0	00	1111	dfff	ffff",
"IORWF	f, d	Inclusive OR W with f	00	0100	dfff	ffff",
"MOVF	f, d	Move f	00	1000	dfff	ffff",
"MOVWF	f	Move W to f	00	0000	lfff	ffff",
"NOP	–	No Operation	00	0000	0xx0	0000",
"RLF	f, d	Rotate Left f through Carry	00	1101	dfff	ffff",
"RRF	f, d	Rotate Right f through Carry	00	1100	dfff	ffff",
"SUBWF	f, d	Subtract W from f	00	0010	dfff	ffff",
"SWAPF	f, d	Swap nibbles in f	00	1110	dfff	ffff",
"XORWF	f, d	Exclusive OR W with f	00	0110	dfff	ffff",
"BCF	f, b	Bit Clear f	01	00bb	bfff	ffff",
"BSF	f, b	Bit Set f	01	01bb	bfff	ffff",
"BTFSC	f, b	Bit Test f, Skip if Clear	01	10bb	bfff	ffff",
"BTFSS	f, b	Bit Test f, Skip if Set	01	11bb	bfff	ffff",
"ADDLW	k	Add literal and W	11	111x	kkkk	kkkk",
"ANDLW	k	AND literal with W	11	1001	kkkk	kkkk",
"CALL	k	Call Subroutine	10	0kkk	kkkk	kkkk",
"CLRWDT	–	Clear Watchdog Timer	00	0000	0110	0100",
"GOTO	k	Go to address	10	1kkk	kkkk	kkkk",
"IORLW	k	Inclusive OR literal with W	11	1000	kkkk	kkkk",
"MOVLW	k	Move literal to W	11	00xx	kkkk	kkkk",
"RETFIE	–	Return from interrupt	00	0000	0000	1001",
"RETLW	k	Return with literal in W	11	01xx	kkkk	kkkk",
"RETURN	–	Return from Subroutine	00	0000	0000	1000",
"SLEEP	–	Go into Standby mode	00	0000	0110	0011",
"SUBLW	k	Subtract W from literal	11	110x	kkkk	kkkk",
"XORLW	k	Exclusive OR literal with W	11	1010	kkkk	kkkk",
]

class CFileRegister:
    def __init__(self, bankno, address, name, bitmask=None, bitname=None):
        self.bankno = bankno
        self.address = address
        self.name = name
        self.bitmask = bitmask
        self.bitname = bitname if bitname is not None else [None] * 8
        self.bitname = self.bitname[::-1]

    def bitname_index(self,name):
        return next((i for i, bit in enumerate(self.bitname)
         if bit and len(bit) > 0 and name in bit), -1)

class Bank:
    def __init__(self, number):
        self.number = number
        self.file_registers = []

    def add_file_register(self, file_register):
        self.file_registers.append(file_register)

    def get_register_by_name(self, name):
        for reg in self.file_registers:
            # print("name:" + str(reg.name))
            if reg.name.lower() == name.lower():
                return reg
        return None

class Registers:
    def __init__(self):
        self.banks = []

    def add_bank(self, bank):
        self.banks.append(bank)

    def get_register_by_name(self, name):
        for bank in self.banks:
            reg = bank.get_register_by_name(name)
            if reg:
                return reg
        return None
    
    def get_bank(self, bankno):
        if len(self.banks) > bankno:
            return self.banks[bankno]
        else:
            return None

class CInstructionBase:
    def __init__(self, name, operands, description, bitmask):
        self.name = name
        self.operands = self.read_operands(operands)
        self.description = description
        self.bitmask = bitmask

    def __str__(self):
        return f"CInstructionBase({self.name} {self.operands} {self.bitmask} {self.description})"

    def read_operands(self, operands_str):
        operands = []
        for operand in operands_str.split(','):
            operand = operand.strip()
            if operand and operand[0] != '–':
                operands.append(operand[0])
        return operands

initialized = False

def init_regs():
    global registers

    registers = Registers()

    bankno = 0
    for b in _registers:
        bank = Bank(bankno)
        for r in b:
            cols = r.split('\t')
            addr = int(cols[0].rstrip('h'), 16)
            addr &= 0x7f
            name = cols[1]
            if len(name) == 0:
                d("#### Error: " + r)
                continue
            bank.add_file_register(
                    CFileRegister(bankno, addr, name, bitmask=cols[10], bitname=cols[2:10]))
        registers.add_bank(bank)
        bankno = bankno + 1
    
    # for gp register
    bankno = 0
    bank = registers.get_bank(bankno)
    if bank:
        for i in range(0x20 , 0x7f + 1):
            bank.add_file_register(
                CFileRegister(bankno, i, f"GP{i:x}"))

def custom_strcmp(a: str, b: str) -> int:
    la = sum(1 for char in a if char in {'0', '1'})
    lb = sum(1 for char in b if char in {'0', '1'})

    if la != lb:
        return lb - la
    for x, y in zip(a, b):
        if x == y:
            continue
        if x == '1':
            return -1
        if y == '1':
            return 1
        if x == '0':
            return -1
        if y == '0':
            return 1
    return 0


def compare_inst(a, b) -> int:
    val = custom_strcmp(a.bitmask, b.bitmask)
    return val

def init_instructions():
    global instructions

    temp = []
    for inst in _instructions:
        cols = inst.split("\t")
        temp.append(cols)
    instructions = [CInstructionBase(row[0], row[1], row[2], ''.join(row[3:])) for row in temp]
    instructions.sort(key=cmp_to_key(compare_inst))

def init():
    global initialized
    if initialized: return

    init_regs()
    init_instructions()

    initialized = True

def get_instruction(name):
    for inst in instructions:
        if name.upper() == inst.name.upper():
            return inst
    return None

class CInstruction():
    op = None
    goto = None
    banksel = False
    def __init__(self, address, inst, op1, op2, label = None):
        self.address = address
        self.inst = inst
        self.op1 = op1
        self.op2 = op2
        self.label = label
        self.opread()

    def __str__(self):
        label = self.label + ": " if self.label else "        "
        label = "{:04x}: ".format(self.address) + label
        if self.op2:
            return f"{label}{self.inst} {self.op1} {self.op2}"
        if self.op1:
            return f"{label}{self.inst} {self.op1}"
        return f"{label}{self.inst}"

    def need_label(self, name):
        return name.upper() == 'GOTO' or name.upper() == 'CALL'
        
    def from_literal(self, name):
        need_literal = [
            "ADDLW", 
            "ANDLW", 
            "IORLW", 
            "MOVLW", 
            "RETLW", 
            "SUBLW", 
            "XORLW", 
        ]
        return name.upper() in map(str, need_literal)
    
    def is_return(self):
        return self.inst.upper() == "RETURN"
    
    def need_bankselect(self):
        need_banksel = [
            "ADDWF",
            "ANDWF",
            "CLRF",
            "COMF",
            "DECF",
            "DECFSZ",
            "INCF",
            "INCFSZ",
            "IORWF",
            "MOVF",
            "MOVWF",
            "RLF",
            "RRF",
            "SUBWF",
            "SWAPF",
            "XORWF",
            "BCF",
            "BSF",
            "BTFSC",
            "BTFSS"
        ]

        if self.inst.upper() in map(str, need_banksel):
            return 2 if self.op[0] < 0x80 else 1
        else:
            return 0

    def extract_literal(self):
        op1 = self.op1
    
        if op1.startswith("'") and op1.endswith("'") and len(op1) >= 3:
            try:
                return ord(ast.literal_eval(op1))
            except (ValueError, SyntaxError):
                return None

        return int(op1, 16)

    def is_bankselect(self):
        return self.banksel

    def bit_oriented(self):
        bit_register = [
            "BCF",
            "BSF",
            "BTFSC",
            "BTFSS",
        ]
        return self.inst.upper() in bit_register

    def byte_oriented(self):
        byte_register = [
            "ADDWF",
            "ANDWF",
            "CLRF",
            "COMF",
            "DECF",
            "DECFSZ",
            "INCF",
            "INCFSZ",
            "IORWF",
            "MOVF",
            "MOVWF",
            "RLF",
            "RRF",
            "SUBWF",
            "SWAPF",
            "XORWF",
        ]
        return self.inst.upper() in byte_register

    def convert_label(self, addr):
        self.op = []
        self.op.append(addr)

    def opread(self):
        init()
        inst_base = get_instruction(self.inst)
        if not inst_base:
            d(f"#### ERROR: {self}")
            exit()

        self.base = inst_base

        if self.need_label(self.inst):
            if (not self.op1) or (len(self.op1) == 0):
                d(f"#### ERROR: {self}")
                exit()
            self.goto = self.op1
        elif self.from_literal(self.inst):
            self.op = []
            val = self.extract_literal()
            if (val > 255):
                d("#### ERROR:" + str(inst_base))
            self.op.append(val)
        elif self.bit_oriented():
            reg = registers.get_register_by_name(self.op1)
            self.op = []
            self.op.append(reg.address)
            try:
                op2 = int(self.op2, 16)
                self.op.append(op2)
            except ValueError:
                self.op.append(reg.bitname_index(self.op2))
        elif self.byte_oriented():
            reg = registers.get_register_by_name(self.op1)
            self.op = []
            self.op.append(reg.address)

            if self.op2 and len(self.op2) > 0:
                try:
                    op2 = int(self.op2, 16)
                    self.op.append(op2)
                except ValueError:
                    self.op.append(reg.bitname_index(self.op2))
        
    def assemble(self):
        op = ' '.join(f'{x:02x}' for x in self.op if isinstance(x, int)) if self.op else ''
        d(f"{self.address:04x}: {self.inst} {self.base.bitmask} {self.base.operands} {op}")
        bitmask = self.base.bitmask

        for index, operand in enumerate(self.base.operands):
            count = bitmask.count(operand)
            if (len(self.op) <= index):
                print(self)
            op_bin = f'{self.op[index]:0{count}b}'
            bitmask = re.sub(f'{operand}+', lambda match: op_bin[:len(match.group(0))], bitmask)

        bitmask = bitmask.replace('l', '0')
        if (self.inst.upper() in ["MOVLW","ADDLW"]):
            bitmask = bitmask.replace('x', '0')

        if bool(re.search(r'[^01]', bitmask)):
            d(f"#### ERROR: {self}")
            exit()

        hex_value = int(bitmask, 2)

        self.hex = hex_value

def load_file(fpath):
    label = None
    address = 0
    data = []
    with open(fpath) as f:
        for line in f:
            line_content = re.sub(r';.*$','', line).strip()
            if len(line_content) == 0: continue

            if line_content.endswith(':'):
                label = line_content[:-1]
                continue

            inst, op1, op2 = (re.split(r'[,\s]+', line_content.strip()) + [None, None])[:3]
            data.append(CInstruction(address, inst, op1, op2, label))
            address = address + 2
            label = None
    return data

def add_bankselect(data):
    start = -1
    banksel = 0
    add_addrs = []
    for inst in data:
        if inst.label:
            start = inst.address
            banksel = 0
        if start >= 0:
            temp = inst.need_bankselect()
            if temp and (banksel != temp):
                banksel = temp
                if banksel == 1:
                    opcode = "BCF"
                else:
                    opcode = "BSF"
                cls = CInstruction(inst.address, opcode, "STATUS", "RP0", inst.label)
                cls.banksel = True
                add_addrs.append(cls)
                inst.label = None

        if inst.is_return():
            if start < 0:
                d("#### Error:" + inst)
                exit()
            if banksel:
                start = -1
                banksel = 0

    for addr in add_addrs:
        data.append(addr)
    data.sort(key=lambda x: (x.address, not x.is_bankselect()))
    for i in range(1, len(data)):
        if data[i].address <= data[i-1].address:
            data[i].address = data[i-1].address + 2

def lookup_label_address(data, addr, label):
    try:
        diff = int(label)
        diff = diff * 2
        return addr + diff
    except ValueError: 
        return next((item.address for item in data if item.label == label), None)
            
def convert_label_to_address(data):          
    for inst in data:
        label = inst.goto
        if label:
            addr = lookup_label_address(data, inst.address, label)
            # d(f"label:{label} addr:{addr}")
            inst.convert_label(addr)

def assemble(data):

    add_bankselect(data)

    convert_label_to_address(data)

    for inst in data:
        inst.assemble()

        

def get_output(fpath):
    return os.path.splitext(fpath)[0] + ".hex"

def write_to_file(data, fpath):
    def to_hex_string(byte_value, length=2):
        return f"{byte_value:0{length}X}"
    
    with open(fpath, 'w') as f:
        for i in range(0, len(data), 8):
            record_data = ""
            start_addr = data[i].address
            
            for inst in data[i:i + 8]:
                record_data += to_hex_string(inst.hex >> 8)
                record_data += to_hex_string(inst.hex & 0xFF)
            
            byte_count = len(record_data) // 2
            addr_str = to_hex_string(start_addr, 4)
            record_type = "00"
            checksum_data = (
                byte_count + (start_addr >> 8) + (start_addr & 0xFF) +
                sum(int(record_data[j:j + 2], 16) for j in range(0, len(record_data), 2))
            )
            checksum = (-checksum_data) & 0xFF
            
            f.write(f":{to_hex_string(byte_count)}{addr_str}{record_type}{record_data}{to_hex_string(checksum)}\n")
        f.write(":00000001FF\n")

def main():
    file_path = get_file_path()
    if not file_path:
        usage()
        exit()
    data = load_file(file_path)
    if len(data) > 0:
        assemble(data)
        output = get_output(file_path)
        write_to_file(data, output)
        d("done.")
    else:
        usage()

if __name__ == "__main__":
    main()

