#!/usr/bin/env python3

import sys
import os
import glob
import argparse
import inspect
import time
import serial
import stat

S_PORT = 'port'


ser = None
settings = {}
pics = []

def usage():
    command = sys.argv[0]
    explain = f"""usage:
    {command} <file>
"""
    print(explain, end="")

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(f"--{S_PORT}", type=int )

    args, unknown_args = parser.parse_known_args()

    options = vars(args)
    options = {k: v for k, v in vars(args).items() if v is not None}

    positional_args = unknown_args

    return options, positional_args

def argcheck(arg):
    if len(arg) < 1:
        return False

    return arg[0] if len(arg[0]) > 0 else None

def d(s):
    frame = inspect.currentframe().f_back
    function_name = frame.f_code.co_name
    line_number = frame.f_lineno
    print(f"({line_number}) {function_name} ", end="")
    print(s)

def num_base(a):
    s = a.strip().lower()
    base = 10
    if s.startwith('0b'):
        base = 2
    elif s.startwith('0o'):
        base = 8
    elif s.startwith('0b'):
        base = 16
    elif s.isdigit():
        base = 10
    else:
        raise ValueError(f"Invalid number format: {s}")

    return 0

def str_number(number: int, base : int = 10) -> str:
    if base == 2:
        return f"0b{number:b}"
    elif base == 8:
        return f"0o{number:o}"
    elif base == 10:
        return str(number)
    elif base == 16:
        return f"0x{number:x}"
    else:
        raise ValueError("Base must be 2, 8, 10, or 16")

def or_str(a, b):
    base = num_base(a)
    return str_number( int(a, 0) | int(b, 0), base)
def and_str(a, b):
    base = num_base(a)
    return str_number( int(a, 0) & int(b, 0), base)
def exor_str(a, b):
    base = num_base(a)
    return str_number( int(a, 0) ^ int(b, 0), base)

def writeable():
    return os.geteuid() == 0

class CPic:
    name = None
    def __init__(self):
        pass

    def __str__(self):
        return self.name

    def is_supported(self, name):
        return name == 'PIC12F683'



def get_commport(options):
    comm_port = None
    if S_PORT in options:
        port = options[S_PORT]
        s_port = f"/dev/ttyUSB{port}"
        if stat.S_ISCHR(os.stat(s_port).st_mode):
            comm_port = s_port
    else:
        ttys = glob.glob("/dev/ttyUSB*")
        if not ttys:
            return None

        if (len(ttys) == 1):
            comm_port = ttys[0]
            return comm_port

        for index, device in enumerate(ttys):
            print(f"{index}: {device}")        

        while True:
            try:
                selection = int(input("番号を入力してください: "))
                if 0 <= selection < len(ttys):
                    print(f"選択されたデバイス: {ttys[selection]}")
                    comm_port = ttys[selection]
                    break
                else:
                    break
            except ValueError:
                break
    return comm_port

def serial_read(count = 0, end=b'@', text=True):
    decoded_response = None
    d(f"c:{count} t:{text}")
    try:
        if count > 0:
            response = ser.read(count)
        else:
            response = ser.read_until(end)
        if text and response:
            decoded_response = response.decode('utf-8').replace('\r', '\n')
        else:
            return response
    except serial.SerialTimeoutException:
        d("")
    return decoded_response

def serial_close():
    global ser
    if ser:
        ser.close()
        ser = None
        time.sleep(0.1)

def serial_open(port):
    global ser
    if not ser:
        ser = serial.Serial(
            port=port,
            baudrate=57600,
            timeout=5,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            # xonoff=False,
            rtscts=False,
            dsrdtr=False
        )

def serial_check(port):
    serial_open(port)

    ser.reset_input_buffer()

    for i in range(0,3):
        ser.write(b'*')
        time.sleep(0.001)
    time.sleep(0.1)

    ser.reset_input_buffer()
    ser.write(b'?')
    s = serial_read()

    if s and len(s) >= 18:
        ser.write(b"mD\n")
        s = serial_read(count = 1)

    return s and len(s) >= 18


def check_port(port):
    global ser

    result = False
    serial_open(port)

    ser.write(b'?')
    s = serial_read()
    if s and len(s) >= 18 and s[17] == '@':
        print(s[:17])
        result = True

    return result

def serial_send_str(s):
    for i in range(len(s)):
        ser.write(bytes(s[i], 'utf-8'))
        time.sleep(0.001)

def serial_send_int(s):
    ser.write(bytes(s))
    time.sleep(0.001)

def serial_command(s, reset = True):
    global ser
    if not ser:
        d("#### ERROR: serial error")
        return

    if reset:
        ser.reset_input_buffer()

    if isinstance(s, str):
        serial_send_str(s)
    elif isinstance(s, int):
        serial_send_int(s)
    elif isinstance(s, list):
        for v in s:
            serial_send_int(v)

def pic_is_set(port):
    result = False
    serial_open(port)
    serial_command("nrsc")
    serial_command([0, 8, 0x40], reset=False)
    s = serial_read(count=17, text=False)
    if s and len(s) == 17:
        check = int((((s[12] & 0x3f ) << 8) + s[13] ) / 32)
        result = (check == 0x23)
        print(f"s:{s} c:{check:} r:{result}")
    #serial_close()
    return result

def read_arg(hi, lo):
    addr = (hi << 8) | lo
    addr = addr + 1 
    repeat = (addr + 1) // 8
    end = addr * 2 + 1 
    return repeat, end, ((addr >> 8) & 0xff), (addr & 0xff)

def flash_read(port):
    global settings

    data = {}

    if not pic_is_set(port):
        return None

    if 'PmEndAdr' in settings:
        hi = settings['PmEndAdrHi']
        lo = settings['PmEndAdrLo']
        repeat, end_addr,hi,lo  = read_arg(hi, lo)
        serial_command("nrsp")
        serial_command([hi, lo])
        serial_command([b'@'] * repeat)
        data['code'] = serial_read(count = end_addr,text=False)

        hi = settings['DmEndAdrHi']
        lo = settings['DmEndAdrLo']
        repeat, end_addr, hi, lo = read_arg(hi, lo)
        serial_command("nrsd")
        serial_command([hi, lo])
        serial_command([b'@'] * repeat)
        data['eeprom'] = serial_read(count = end_addr,text=False) 

        hi = 0
        lo = 0xf 
        repeat, end_addr, hi, lo = read_arg(hi, lo)
        serial_command("nrsc")
        serial_command([hi, lo])
        serial_command([b'@'] * repeat)
        data['eeprom'] = serial_read(count = end_addr,text=False) 
        
    return data


def load_configx(index, cols):
    global settings

    if 'config' not in settings:
        configs = {}
    else:
        configs = settings['config']
    config = {}
    config['DeviceDatConfigErase'] = int(cols[1], 0)
    config['DeviceDatConfig'] = int(cols[1], 0)
    config['DeviceDatOther0'] = int(cols[2], 0)
    config['DeviceDatOther1'] = int(cols[3], 0)
    config['DeviceBitLength'] = int(cols[4], 0)

    if not 'MCU_MemoryReadFlag' in settings or not settings['MCU_MemoryReadFlag']:
        config['DeviceDatConfig'] = (config['DeviceDatConfig'] & config['DeviceDatOther0']) | config['DeviceDatOther1']  

    if 'cw_data' not in settings:
        cw_data = [0] * 0x100
    else:
        cw_data = settings['cw_data']

    if (index == 1):
        cw_data[14] = config['DeviceDatConfig'] & 0xff
        cw_data[15] = (config['DeviceDatConfig'] & 0xff00) >> 8


    configs[str(index)] = config
    settings['config'] = configs

def load_settings():
    global pics
    global settings
    with open('settings.ini', 'r') as f:
        pic = None
        for line in f:
            if pic and not pic.name:
                name = line.strip()
                if pic.is_supported(name):
                    pic.name = name
                continue
            cols = line.strip().split()
            if len(cols) == 0:
                continue
            if cols[0] == '#BEGIN':
                pic = CPic()
                continue
            elif cols[0] == '#END':
                pics.append(pic)
            elif cols[0] == 'PACKAGE':
                pass
            elif cols[0] == 'PGM_SIZE_WORD':
                end_addr = int(cols[1], 0)
                print(f"end_addr:{end_addr}")
                settings['PmEndAdr'] = end_addr
                settings['PmEndAdrHi'] = (end_addr & 0xff00 )>> 8
                settings['PmEndAdrLo'] = (end_addr & 0xff )>> 0
            elif cols[0] == 'EEPROM_BYTE':
                end_addr = int(cols[1], 0)
                if end_addr == 0:
                    pass
                else:
                    end_addr = end_addr + 1
                settings['DmEndAdrHi'] = (end_addr & 0xff00) >> 8
                settings['DmEndAdrLo'] = (end_addr & 0xff) >> 0
                settings['DmEndAdr'] = end_addr

            elif cols[0] == 'CONFIG1':
                load_configx(1, cols)
            elif cols[0] == 'CONFIG2':
                load_configx(2, cols)
            elif cols[0] == 'POWER_MODE':
                settings['POWER_MODE'] = cols[1]
            elif cols[0] == 'PGM_TYPE':
                settings['PGM_Type'] = cols[1]
            elif cols[0] == 'COMMENT':
                settings['DeviceDatCmt'] = " ".join(cols[1:])
            elif cols[0] == 'PACKAGE':
                if int(cols[1],0) == 8:
                    settings['Shape_8P'] = True
            elif cols[0] == 'JP2':
                settings['DeviceDatFirm'] = cols[1]
            elif cols[0] == 'VDD_VPP_DELAY':
                settings['PowerOptionVddVppDelay'] = cols[1]
            elif cols[1] == 'CP':
                settings['DeviceDatCpMask_PIC12_16'] = int(cols[3], 0)
            else:
                # col = 
                pass
    print(f"settings:\n{settings}")

def dump(data):
    for offset in range(0, len(data), 16):
        chunk = data[offset:offset + 16]
        
        hex_output = " ".join(f"{byte:02x}" for byte in chunk)
        
        ascii_output = "".join(chr(byte) if 32 <= byte <= 126 else '.' for byte in chunk)
        
        print(f"{offset:08x}  {hex_output:<47}  {ascii_output}")

def main():
    global settings

    options, arg = parse_arguments()
    fpath = argcheck(arg)
    if not fpath:
        usage()
        exit()
    elif not writeable():
        d("#### ERROR: super user required")
        exit()

    port = get_commport(options)
    if not port:
        d("#### ERROR: Comm Port options:{options}")
        exit()
    
    if not check_port(port):
        d("#### ERROR: Comm Port")
        serial_close()
        exit()

    serial_close()

    load_settings()

    if not serial_check(port):
        d("#### ERROR: Communication Error")
        serial_close()
        exit()

    readed = flash_read(port)
    serial_close()
    dump(readed)

    print("OK")


if __name__ == "__main__":
    main()
