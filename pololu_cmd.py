#! /usr/bin/env python3

# @file: pololu_cmd.py  --Pololu library using python
# @author: @cristinaluna
# @date: nov 2021
#

'''
Usage: ticcmd OPTIONS

General options:
  -s, --status                 Show device settings and info.
  --full                       When used with --status, shows more.
  -d SERIALNUMBER              Specifies the serial number of the device.
  --list                       List devices connected to computer.
  --pause                      Pause program at the end.
  --pause-on-error             Pause program at the end if an error happens.
  -h, --help                   Show this help screen.

Control commands:
  -p, --position NUM           Set target position in microsteps.
  --position-relative NUM      Set target position relative to current pos.
  -y, --velocity NUM           Set target velocity in microsteps / 10000 s.
  --halt-and-set-position NUM  Set where the controller thinks it currently is.
  --halt-and-hold              Abruptly stop the motor.
  --home DIR                   Drive to limit switch; DIR is 'fwd' or 'rev'.
  --reset-command-timeout      Clears the command timeout error.
  --deenergize                 Disable the motor driver.
  --energize                   Stop disabling the driver.
  --exit-safe-start            Send the exit safe start command.
  --resume                     Equivalent to --energize with --exit-safe-start.
  --enter-safe-start           Send the enter safe start command.
  --reset                      Make the controller forget its current state.
  --clear-driver-error         Attempt to clear a motor driver error.

Temporary settings:
  --max-speed NUM              Set the speed limit.
  --starting-speed NUM         Set the starting speed.
  --max-accel NUM              Set the acceleration limit.
  --max-decel NUM              Set the deceleration limit.
  --step-mode MODE             Set step mode: full, half, 1, 2, 2_100p, 4, 8,
                               16, 32.
  --current NUM                Set the current limit in mA.
  --decay MODE                 Set decay mode:
                               Tic T825/N825: mixed, slow, or fast
                               T834: slow, mixed25, mixed50, mixed75, or fast

Temporary settings for AGC on the Tic T249:
  --agc-mode MODE                    Set AGC mode: on, off, active_off
  --agc-bottom-current-limit LIMIT   Set AGC bottom current limit %:
                                     45, 50, 55, 60, 65, 70, 75, or 80.
  --agc-current-boost-steps STEPS    Set AGC current boost steps:
                                     5, 7, 9, or 11.
  --agc-frequency-limit LIMIT        Set AGC frequency limit in Hz:
                                     off, 225, 450, or 675.

Permanent settings:
  --restore-defaults           Restore device's factory settings
  --settings FILE              Load settings file into device.
  --get-settings FILE          Read device settings and write to file.
  --fix-settings IN OUT        Read settings from a file and fix them.

For more help, see: https://www.pololu.com/docs/0J71
'''

import os
import re
from datetime import datetime
import time
import subprocess

def cmd_test(turns, path):
    target = 200*turns # without microstepping with a simple 200 step stepper-motor.
    print("Number of turns: {}".format(turns))
    filename = "{}/target_{}".format(path, target)+".csv" # saves data in a csv file
    home = 0
    start = datetime.now()
    try:
        f = open(filename,"w+") 
        f.write("position,speed,encoder_position,analog_reading,analog_parsed,vin,time\n")
        # gets initial data
        position = go_target(f, start)
        
        # go to target position
        set_target_position(target)
        while position != target :
	        # get pololu status
	        position = go_target(f, start)
	    
	    
	    # go back to 0
        set_target_position(home)
        
        while position != home :
	        # get pololu status
	        position = go_target(f, start)
        

    except KeyboardInterrupt:
        #go_home("rev")
        set_target_position(home)
        stop_tic()
        f.close()
        pass

def start_tic():
    os.system("ticcmd --exit-safe-start")
    os.system("ticcmd --energize")
    set_target_position(0)
    time.sleep(2)
    
def stop_tic():
    set_target_position(0)
    time.sleep(4)
    os.system("ticcmd --deenergize")
    os.system("ticcmd --enter-safe-start")
    
def reset():
    os.system("ticcmd --reset")
    
def go_home(direction): # "fwd" or "rev"
    os.system("ticcmd --home {}".format(direction))
    
def restart():
    start_tic()
    go_home("rev")
    stop_tic()
    
def set_target_position(target):
    os.system("ticcmd --position {}".format(target))
    
def get_analog(): # gets SDA reading
    cmd = "ticcmd --status --full | grep Analog" # SCL, SDA, TX, RX
    analog = subprocess.check_output(cmd, shell=True)
    analog = analog.decode("utf-8")
    analog_reading = [int(s) for s in analog.split() if s.isdigit()]
    #print ("Current Analog SDA Reading: {}".format(analog_reading[1]))
    return analog_reading[1]
    
def get_current_pos():
    cmd = "ticcmd --status --full | grep \"Current position\""
    current_pos = subprocess.check_output(cmd, shell=True)
    current_pos = current_pos.decode("utf-8")
    #position = [int(s) for s in current_pos.split() if s.isdigit()]
    position = [int(d) for d in re.findall(r'-?\d+', current_pos)]
    #print ("Current position: {}".format(position[0]))
    return position[0]
    
def get_current_speed():
    cmd = "ticcmd --status --full | grep 'Current velocity'"
    current_speed = subprocess.check_output(cmd, shell=True)
    current_speed = current_speed.decode("utf-8")
    #position = [int(s) for s in current_pos.split() if s.isdigit()]
    speed = [int(d) for d in re.findall(r'-?\d+', current_speed)]
    #print ("Current speed: {}".format(speed[0]))
    return speed[0]
    
def get_encoder_pos():
    cmd = "ticcmd --status --full | grep Encoder"
    encoder_pos = subprocess.check_output(cmd, shell=True)
    encoder_pos = encoder_pos.decode("utf-8")
    encoder = [int(s) for s in encoder_pos.split() if s.isdigit()]
    #print ("Encoder position: {}".format(encoder[0]))
    return encoder[0]
    
def get_vin():
    cmd = "ticcmd --status --full | grep VIN"
    vin_data = subprocess.check_output(cmd, shell=True)
    vin_data = vin_data.decode("utf-8")
    #print(vin_data)
    vin = [float(d) for d in re.findall(r'\d+.\d+', vin_data)]
    #print ("VIN: {}".format(vin))
    return vin[0]
    
def parse_encoder(encoder):
    # helps to get the relative value using and encoder
    encoder = encoder/160 #change this value with your own encoder measures
    return encoder
    
def get_time(start):
    now = (datetime.now() - start )
    now_m = now.microseconds
    now_s = now.seconds
    now_t = now_s + (now.microseconds*0.000001)
    return now_t
    
def go_target(f, start):
    position = get_current_pos()
    speed = get_current_speed()
    encoder = get_encoder_pos()
    analog = get_analog()
    parsed = parse_encoder(analog)
    vin = get_vin()
    now = get_time(start)
    f.write("{},{},{},{},{},{},{}\n".format(position, speed, encoder, 
        analog, parsed, vin, str(now)))
    return position

def get_status_full():
    cmd = "ticcmd --status --full"
    status = subprocess.check_output(cmd)
    return status
    
def mkdir():
    path = "test_{}".format(str(datetime.now().strftime("%Y%m%d_%H%M%S")))
    os.system("mkdir {}".format(path))
    return path

if __name__=="__main__":
    path = mkdir()    
    start_tic()
    for i in range (1, 5):
        cmd_test(i, path)
    stop_tic()
else:
    pass
    
