#!/usr/bin/env python3

import argparse
import logging
from re import T
import serial
import time

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)

class UsbRelay:
    begin_byte = 0xa0
    end_byte_base = 0xa0
    on_byte = 0x01
    off_byte = 0x00

    def __init__(self, port:str, id:int, log_level=logging.INFO) -> None:
        self.__init_logger__(log_level)
        if id > 200:
            self.logger.critical('Invalid relay id:%d' % id)
            exit(-1)

        self.id = id
        self.id_byte = id
        self.end_byte_on = self.end_byte_base + id + 1
        self.end_byte_off = self.end_byte_base + id
        self.__init_serial__(port)


    def __init_logger__(self, log_level):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)


    def __init_serial__(self, port:str):
        self.ser = serial.Serial()
        self.ser.port = port

        # 9600, 8n1
        self.ser.baudrate = 9600
        self.ser.bytesize = serial.EIGHTBITS #number of bits per bytes
        self.ser.parity = serial.PARITY_NONE #set parity check
        self.ser.stopbits = serial.STOPBITS_ONE #number of stop bits
        try:
            self.ser.open()
        except Exception as ex:
            print('Failed to open serial port: %s' % str(ex))
            exit(-1)


    def __write__(self, byte_array):
        try:
            self.ser.write(byte_array)
        except Exception as ex:
            print ('Failed to write serial port %s' % str(ex))
            exit(-1)


    def action_on(self):
        if not self.ser.isOpen():
            self.logger.critical('Serial port is not opened\n')
            exit(-1)

        byte_array = [self.begin_byte, self.id_byte, self.on_byte, self.end_byte_on]
        self.logger.info('%s turns on' % self.ser.port)
        self.logger.debug(' with [%x, %x, %x, %x]' % (byte_array[0],
                            byte_array[1], byte_array[2], byte_array[3]))
        self.__write__(byte_array)


    def action_off(self):
        if not self.ser.isOpen():
            self.logger.critical('Serial port is not opened\n')
            exit(-1)

        byte_array = [self.begin_byte, self.id_byte, self.off_byte, self.end_byte_off]
        self.logger.info('%s turns off' % self.ser.port)
        self.logger.debug(' with [%x, %x, %x, %x]' % (byte_array[0],
                            byte_array[1], byte_array[2], byte_array[3]))
        self.__write__(byte_array)


    def action_click(self):
        self.action_on()
        time.sleep(0.5)
        self.action_off()


def parse_argument():
    parser = argparse.ArgumentParser(description='Shopee daily checkin bot.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")
    parser.add_argument("--com-port", type=str, required=True,
                        help="(Required) serial port name")
    parser.add_argument("--id", type=int, default=1,
                        help="relay index (starts from 1)")
    parser.add_argument("--action", type=str, choices=['on', 'off', 'click'], default='click',
                        help="Relay actions:")
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_argument()

    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    relay = UsbRelay(args.com_port, args.id, log_level)

    if args.action == 'on':
        relay.action_on()
    elif args.action == 'off':
        relay.action_off()
    elif args.action == 'click':
        relay.action_click()
