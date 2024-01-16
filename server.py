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

@app.route('/', methods=['POST', 'GET'])
def index():
    temp = bus.read_i2c_block_data(0x3d, 0, 8)
    tmax = temp[0] | temp[1] << 8
    tlimp= temp[2] | temp[3] << 8
    tlightvalue = temp[4] 
    tbootstate = temp[7]
    if tlightvalue == 1 :
        lightstatus = "on"
    else:
        lightstatus = "off"
    if tbootstate == 1 :
        bootstate = "auto"
    else:
        bootstate = "manual"    
    return render_template('index.html', tmax=tmax, tlimp=tlimp, lightstatus=lightstatus, bootstate=bootstate)

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
        statement = "Successfully configured pi"
        return render_template('landing.html', statement=statement)
    else:
        statement = "Failed due to invalid IP address (make sure to enter in the form xxx.xxx.xxx.xxx)"
        return render_template('landing.html', statement=statement)
            
@app.route('/configure_throttle', methods=['POST'])
def configure_throttle():
    thrmax = int(request.form['thrmax'])
    limp = int(request.form['limp'])
    tbytes = thrmax.to_bytes(2, 'little') 
    lbytes = limp.to_bytes(2, 'little') 
    
    if (1500 <= thrmax <= 2200) and (1500 <= limp <= 2200) and (limp < thrmax) :
        bus.write_i2c_block_data(0x3d, 0, list(tbytes) + list(lbytes))
        # y'know, above is kinda hardcoded and sketchy but we're going fast here
        statement = "successfully wrote new throttle max / limp values"
        return render_template('landing.html', statement=statement)
    else: 
        statement = "bad throttle max / limp values"
        return render_template('landing.html', statement=statement)

@app.route('/download')
def download():
    path = "lawnmower.BIN"
    return send_file(path, as_attachment=True)

@app.route('/calibrate', methods=['POST'])
def calibrate():
    bus.write_byte_data(0x3d, 6, 1)
    time.sleep(2)
    bus.write_byte_data(0x3d, 6, 0)
    statement = "Calibrating"
    return render_template('landing.html', statement=statement)

@app.route('/light_on', methods=['POST'])
def light_on():
    bus.write_byte_data(0x3d, 4, 1) 
    statement = "successfully turned lights on"
    return render_template('landing.html', statement=statement)

@app.route('/light_off', methods=['POST'])
def light_off():
    bus.write_byte_data(0x3d, 4, 0)
    statement = "successfully turned lights off"
    return render_template('landing.html', statement=statement)

@app.route('/pair', methods=['POST'])
def pair():
    bus.write_byte_data(0x3d, 5, 1)
    time.sleep(2)
    bus.write_byte_data(0x3d, 5, 0)
    statement = "attempting to pair, check transmitter to see if it was successful"
    return render_template('landing.html', statement=statement)

@app.route('/set_auto', methods=['POST'])
def set_auto():
    bus.write_byte_data(0x3d, 7, 1)
    statement = "set default boot state to auto"
    return render_template('landing.html', statement=statement)

@app.route('/set_manual', methods=['POST'])
def set_manual():
    bus.write_byte_data(0x3d, 7, 0)
    statement = "set default boot state to manual"
    return render_template('landing.html', statement=statement)

if __name__ == '__main__':
    app.run(localip)
   
