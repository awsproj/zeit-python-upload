#!/usr/bin/env python
#   url_test_coms.py

from __future__ import print_function
import __builtin__
import sys
def print(*args, **kwargs):
    retv = __builtin__.print(*args, **kwargs)
    sys.stdout.flush()
    return retv


# com29:  power control through buspirate
# com28:  console port

import serial
import time

g_time0 = time.time()

class ComConn:
    def __init__(self, port, name):
        self._comPort = port
        self._comBaud = 115200
        self._designation = name
        self._baseTime = g_time0
        self._results = []
        self._opPort = serial.Serial(self._comPort, self._comBaud, timeout=0.050)

    def setBaseTime(self, basetime):
        self._baseTime = basetime

    def printClear(self, msg=None, prefix=None):
        if msg is not None:
            print("======== %12s ==== %12s ========" % (self._designation, msg))
        if prefix is None:
            prefix = self._designation
        for x in self._results:
            t_g = x[0] - g_time0
            t_t = x[0] - self._baseTime
            print("%s %6.2f %6.2f %s" % (prefix, t_g, t_t, x[1]))
        self._results = []

    def opSend(self, cmd_in):
        cmd = cmd_in.rstrip()
        self._opPort.write(cmd + "\r")

    def opRun(self, timeout_short=0.130, timeout_long=1.0):
        startTime = time.time()
        lastActive = startTime
        retv = 0 # return lines received
        while(True):
            reading = self._opPort.readline()
            nowTime = time.time()
            if len(reading) > 0:
                lastActive = nowTime
                self._results.append([nowTime, reading.rstrip()])
                retv += 1
            else:
                if (nowTime - lastActive) >= timeout_short:
                    break
            if (nowTime - startTime) >= timeout_long:
                break
        return retv

com_pwr = ComConn("COM29", "POWER  ")
com_con = ComConn("COM28", "CONSOLE")

com_pwr.opRun()
com_con.opRun()
com_pwr.printClear(msg="start")
com_con.printClear(msg="start")

com_pwr.opSend("list")
com_con.opSend("")
com_pwr.opRun()
com_con.opRun()
com_pwr.printClear(msg="start touch")
com_con.printClear(msg="start touch")

tm0 = time.time()
testcnt = 0
while True:
    testcnt += 1
    tm1 = time.time()
    print("\n\nTest %d\n" % testcnt)
    def test_run(pcmd, ccmd, run_length=1.0):
        tms1 = time.time()
        if pcmd is not None:
            com_pwr.opSend(pcmd)
        if ccmd is not None:
            com_con.opSend(ccmd)
        while True:
            com_pwr.opRun()
            com_con.opRun()
            com_pwr.printClear()
            com_con.printClear()
            tms2 = time.time()
            if tms2 - tms1 > run_length:
                break
    com_pwr.setBaseTime(tm1)
    com_con.setBaseTime(tm1)
    test_run("run", "", 80)
    test_run("", "", 50)
    test_run("", "/var/tmp/ctrl_main 2", 50)
    tm2 = time.time() - tm1
    print("\n\nTest %d done in %.2f seconds\n" % (testcnt, tm2))
    if testcnt >= 10:
        break

'''bus-pirate basic script in dio mode:

10 let a=adc
20 print "adc1=";a
30 psu 0
32 delay 3000
40 let a=adc
50 print "adc2=";a
60 let b=30000
62 print "delay b=";b
70 delay b
72 print "delay b=";b
74 delay b
80 psu 1
82 delay 3000
90 let a=adc
100 print "adc3=";a

'''

