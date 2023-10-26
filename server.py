from flask import Flask, render_template, request
from flask import send_file
import os
import re
import sys
import smbus
import struct

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
    return render_template('index.html')

@app.route('/configure_pi', methods=['POST'])
def configure_pi():
    #PARSE FORM DATA
    ipstring = request.form['ipstring']
    gsipstring = request.form['gsipstring']
    hostname = request.form['hostname']
    
    #formatting bash command
    text = ' ' + ipstring + ' ' + gsipstring + ' ' + hostname
    cmd = 'sudo sh flashpi.sh ' + text

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

if __name__ == '__main__':
    app.run(localip)
   

