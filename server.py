from flask import Flask, render_template, request
from flask import send_file
from flask import redirect
from flask import url_for
import os
import re
import sys
import smbus
import struct
import time

bus = smbus.SMBus(1)

app = Flask(__name__)

localip = sys.argv[1]

def checkIP(ip):
    pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    if pattern.match(ip):
        return True
    else: 
        return False

@app.route('/')
def index():
    temp = bus.read_i2c_block_data(0x3d, 0, 5)
    tmax = temp[0] | temp[1] << 8
    tlimp= temp[2] | temp[3] << 8
    tlightvalue = temp[4] 
    if tlightvalue == 255 :
        lightstatus = "on"
    else:
        lightstatus = "off"
    return render_template('index.html', tmax=tmax, tlimp=tlimp, lightstatus=lightstatus)

@app.route('/configure_pi', methods=['POST'])
def configure_pi():
    #PARSE FORM DATA
    ipstring = request.form['ipstring']
    gsipstring = request.form['gsipstring']
    hostname = request.form['hostname']
    
    #formatting bash command
    text = ' ' + ipstring + ' ' + gsipstring + ' ' + hostname
    cmd = 'sudo bash flashpi ' + text

    #debug
    print("DEBUG: Command is " + cmd)

    #running command 
    if checkIP(ipstring) == True and checkIP(gsipstring) == True:
        os.system(cmd)
        return 'Success!'
    else:
        return 'Failed due to invalid IP address (make sure to enter in the form xxx.xxx.xxx.xxx)'
            
@app.route('/configure_throttle', methods=['POST'])
def configure_throttle():
    thrmax = int(request.form['thrmax'])
    limp = int(request.form['limp'])
    tbytes = thrmax.to_bytes(2, 'little') 
    lbytes = limp.to_bytes(2, 'little') 
    
    if (1500 <= thrmax <= 2200) and (1500 <= limp <= 2200) and (limp < thrmax) :
        bus.write_i2c_block_data(0x3d, 0, list(tbytes) + list(lbytes))
        # y'know, above is kinda hardcoded and sketchy but we're going fast here
        return 'successfully wrote new throttle max / limp values'
    else: 
        return 'bad throttle max / limp values'

@app.route('/download')
def downloadFile():
    path = "lawnmower.BIN"
    return send_file(path, as_attachment=True)

app.route('/calibrate')
def calibrate():
    bus.write_byte_data(0x3d, 6, 1)
    time.sleep(2)
    bus.write_byte_data(0x3d, 6, 0)
    return 'Calibrating'


@app.route('/light_on')
def light_on():
    bus.write_byte_data(0x3d, 4, 1)
    return 'successfully turned lights on'

@app.route('/light_off')
def light_off():
    bus.write_byte_data(0x3d, 4, 0)
    return 'successfully turned lights off'

@app.route('/pair')
def pairing():
    bus.write_byte_data(0x3d, 5, 1)
    time.sleep(2)
    bus.write_byte_data(0x3d, 5, 0)
    return 'attempting to pair, check transmitter to see if it was successful'

if __name__ == '__main__':
    app.run(localip)
   
