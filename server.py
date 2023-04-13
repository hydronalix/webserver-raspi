from flask import Flask, render_template, request
import os
import re

app = Flask(__name__)

def checkIP(ip):

    pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    if pattern.match(ip):
        return True
    else:
        return False   

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def my_form_post():
    #parse the form data
    ipstring = request.form['ipstring']
    gsipstring = request.form['gsipstring']
    hostname = request.form['hostname']

    #formating bash command
    text = ' '+ ipstring +' '+ gsipstring +' '+ hostname
    cmd = 'sudo sh flashpi.sh' + text

    print("DEBUG: Sample command " + cmd)

    #running commadn and checking if IP is valid (maybe use try blocks)
    if checkIP(ipstring) == True and checkIP(gsipstring) == True:
        os.system(cmd)
        print("address valid")
        return 'Success!'
    elif checkIP(ipstring) == False or checkIP(gsipstring) == False:
        print("One or more IP addresses invalid - please try again")
        return 'Failed due to invalid IP address (make sure to enter in the form xxx.xxx.xxx.xxx)'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')




    

    