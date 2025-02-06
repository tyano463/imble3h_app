#!/usr/bin/env python3

import sys
import os
import re
from functools import cmp_to_key

def usage():
    explain = """usage:
    ./disas.py <file>
"""
    print(explain, end="")

def get_file_path():
    if len(sys.argv) != 2:
        return None
    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        return None
    return file_path

class HexRecord:
    def __init__(self, address, data):
        self.address = address
        self.data = (data[1] << 8) | data[0]

    def __str__(self):
        data_str = "{:04x}".format(self.data)
        return f"{self.address:04X}: {data_str}"


class IntelHexParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.records = []

    def parse(self):
        last_data = None
        with open(self.filepath, 'r') as file:
            for line in file:
                if not line.startswith(":"):
                    continue

                byte_count = int(line[1:3], 16)
                address = int(line[3:7], 16)
                record_type = int(line[7:9], 16)
                data = [int(line[i:i + 2], 16) for i in range(9, 9 + byte_count * 2, 2)]

                if last_data:
                    address = address - 1
                    byte_count = byte_count + 1
                    data = data.append(last_data)
                    last_data = None

                # データレコードのみ追加
                if record_type != 0x00:
                    continue
                if (byte_count % 2) != 0:
                    last_data = data.pop()
                    byte_count = byte_count - 1

                temp = []
                pairs = list(zip(data[::2], data[1::2]))

                for x in pairs:
                    record = HexRecord(address, x)
                    self.records.append(record)
                    address = address + 2

    def get_records(self):
        return self.records

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

instructions = []

_init_opcode = False

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
    val = custom_strcmp(a[3], b[3])
    return val

def init_opcode():
    global _init_opcode 
    global instructions
    temp = []
    if not _init_opcode:
        _init_opcode = True
        for inst in _instructions:
            cols = inst.split("\t")
            temp.append(cols)
        instructions = [[row[0], row[1], row[2], ''.join(row[3:])] for row in temp]
        instructions.sort(key=cmp_to_key(compare_inst))
#        for inst in instructions:
#            print(inst)

def check_bits_match(value: int, pattern: str) -> bool:
    value_bits = f"{value:014b}"
    
    for bit, char in zip(value_bits, pattern):
        if char == '1' and bit != '1':
            return False
        if char == '0' and bit != '0':
            return False
        if char not in '01':
            continue
    return True

def get_opcode(r):
    global instructions
    init_opcode()

    for inst in instructions:
        if check_bits_match(r, inst[3]):
            return inst
    return None


def description(value: int, operands: str, bit_mask: str) -> dict:
    value_bits = f"{value:014b}"
    
    operand_list = operands.split(', ')
    
    result = {}
    
    for operand in operand_list:
        operand_bits = []

        if operand not in bit_mask:
            break

        l = len(bit_mask)
        if len(value_bits) != l: 
            print(f"#### Error v:{value_bits} m:{bit_mask}")
            break

        bit_index = 0
        found = False
        for i in range(l):
            if operand == bit_mask[i]:
                operand_bits.append(value_bits[i])
                found = True
            else:
                if found:
                    break
                continue
            
            bit_index += 1

        # print(operand_bits)
        if operand_bits:
            result[operand] = int(''.join(operand_bits), 2)
    
    return result

def analyze(data):
    for x in data:
        inst = get_opcode(x.data)
        desc = description(x.data, inst[1], inst[3])
        if inst[0] == 'GOTO' or inst[0] == 'CALL':
            desc = {k: v * 2 for k, v in desc.items()}
        desc_str = ','.join([f"{k}: {v:X}" for k, v in desc.items()])
        print(f"{x} {inst[0]} {desc_str} {inst[2]} {inst[3]}")

def main():

    file_path = get_file_path()
    if not file_path:
        usage()
        exit()
    hex_parser = IntelHexParser(file_path)
    hex_parser.parse()
    
    analyze(hex_parser.records)

if __name__ == "__main__":
    main()

