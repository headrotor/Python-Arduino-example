#!/usr/bin/python

# ----------------------------------------------------------------------------
#  HW_Thread.py
#  Classes for communication with asynchronous hardware
#  written by Jonathan Foote jtf@rotormind.com 3/2013
#
#  Works with example Arduino code from 
#  https://github.com/headrotor/Python-Arduino-example
#  Share & enjoy!
#
# -----------------------------------------------------------------------------
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as  as published 
# by the Free Software Foundation http://www.gnu.org/licenses/gpl-2.0.html
# This program is distributed WITHOUT ANY WARRANTY use at your own risk blah blah

import serial #get from http://pyserial.sourceforge.net/
import sys
import time
import threading

class GetHWPoller(threading.Thread):
  """ thread to repeatedly poll hardware
  sleeptime: time to sleep between pollfunc calls
  pollfunc: function to repeatedly call to poll hardware"""
  
  def __init__(self,sleeptime,pollfunc):

    self.sleeptime = sleeptime
    self.pollfunc = pollfunc  
    threading.Thread.__init__(self)
    self.runflag = threading.Event()  # clear this to pause thread
    self.runflag.clear()
      
  def run(self):
    self.runflag.set()
    self.worker()

  def worker(self):
    while(1):
      if self.runflag.is_set():
        self.pollfunc()
        time.sleep(self.sleeptime)
      else:
        time.sleep(0.01)

  def pause(self):
    self.runflag.clear()

  def resume(self):
    self.runflag.set()

  def running(self):
    return(self.runflag.is_set())

  def kill(self):
    print "WORKER END"
    sys.stdout.flush()
    self._Thread__stop()


class HW_Interface(object):
  """Class to interface with asynchrounous serial hardware.
  Repeatedly polls hardware, unless we are sending a command
  "ser" is a serial port class from the serial module """

  def __init__(self,ser,sleeptime):
    self.ser = ser
    self.sleeptime = float(sleeptime)
    self.worker = GetHWPoller(self.sleeptime,self.poll_HW)
    self.interlock = False  # set to prohibit thread from accessing serial port
    self.response = None # last response retrieved by polling
    self.worker.start()
    self.callback = None
    self.verbose = True # for debugging

  def register_callback(self,proc):
    """Call this function when the hardware sends us serial data"""
    self.callback = proc
    #self.callback("test!")
    
  def kill(self):
    self.worker.kill()


  def write_HW(self,command):
    """ Send a command to the hardware"""
    while self.interlock: # busy, wait for free, should timout here 
      print "waiting for interlock"
      sys.stdout.flush()
    self.interlock = True
    self.ser.write(command + "\n")
    self.interlock = False

  def poll_HW(self):
    """Called repeatedly by thread. Check for interlock, if OK read HW
    Stores response in self.response, returns a status code, "OK" if so"""
    if self.interlock:
      if self.verbose: 
        print "poll locked out"
        self.response = None
        sys.stdout.flush()
      return "interlock" # someone else is using serial port, wait till done!
    self.interlock = True # set interlock so we won't be interrupted
    # read a byte from the hardware
    response = self.ser.read(1)
    self.interlock = False
    if response:
      if len(response) > 0: # did something write to us?
        response = response.strip() #get rid of newline, whitespace
        if len(response) > 0: # if an actual character
          if self.verbose:
            self.response = response
            print "poll response: " + self.response 
            sys.stdout.flush()
          if self.callback:
            #a valid response so send it
            self.callback(self.response)
        return "OK"
    return "null" # got no response


def my_callback(response):
  """example callback function to use with HW_interface class.
     Called when the target sends a byte, just print it out"""
  print 'got HW response "%s"' % response


"""Designed to talk to Arduino running very simple demo program. 
Sending a serial byte to the Arduino controls the pin13 LED: ascii '1'
turns it on and ascii '0' turns it off. 

When the pin2 button state changes on the Arduino, it sends a byte:
ascii '1' for pressed, ascii '0' for released. """

if __name__ == '__main__':
  """ You can run this from the command line to test"""

  # Need to set the portname for your Arduino serial port:
  # see "Serial Port" entry in the Arduino "Tools" menu
  portname = "COM18"
  portbaud = "9600"
  ser = serial.Serial(portname,portbaud,timeout=0)
  # timeout=0 means "non-blocking," ser.read() will always return, but
  # may return a null string. 
  print "opened port " + portname + " at " + str(portbaud) +  " baud"

  sys.stdout.flush()
  hw = HW_Interface(ser,0.1)
  
  #when class gets data from the Arduino, it will call the my_callback function
  hw.register_callback(my_callback)

  print "Interactive mode. Commands:"
  print "  r to get last response byte"
  print "  s <str> to send string <str>"
  print "    's 1' turns on Arduino LED"
  print "    's 0' turns LED off"
  print "  x to exit "

  while(1):
    sys.stdout.flush()
    cmd = raw_input('--> ')
    cmd = cmd.split()
    sys.stdout.flush()
    if cmd[0] == 'r':
      print 'Last response: "%s"' % hw.response

    elif cmd[0] == 's':
      val = str(cmd[1])
      print "sending command " + val
      sys.stdout.flush()
      hw.write_HW(val)

    elif cmd[0] == 'x':
      print "exiting..."
      break

    else:
      print "No such command: " + ' '.join(cmd)

  #tidy up, or you can just Ctrl-C
  hw.kill()
  ser.close()
  sys.exit()
