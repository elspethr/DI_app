#import requests as req
import numpy as np
import pandas as pd
from flask import Flask,render_template,request,redirect
#from bokeh.plotting import figure, show
#from bokeh.io import output_notebook
#from bokeh.embed import components
from datetime import datetime
import holidays
import urllib2
import json


app = Flask(__name__)


######functions for getting data and plotting########

def get_hourly_forecast(key, code):
    #open webpage
    f = urllib2.urlopen('http://api.wunderground.com/api/%s/hourly/q/CA/KFUL.json'%(key))
    json_string = f.read()
    parsed_json = json.loads(json_string)
    print parsed_json
    f.close()
    
    #get needed dictionaries from json
    predvars = ['temp', 'wspd', 'FCTTIME', 'condition']
    entries = [[x[column] for column in predvars] for x in parsed_json['hourly_forecast']]
    
    #pre-load dictionaries for filling in prediction variables
    predsdict = {'California Adventure': 0.0,
            'Clear': 0.0,
            'Disneyland': 0.0,
            'Haze': 0.0,
            'Mostly Cloudy': 0.0,
            'Overcast': 0.0,
            'Partly Cloudy': 0.0,
            'Scattered Clouds': 0.0,
            'hour': 99.9,
            'hour2': 0,
            'temp': 0.0,
            'temp2': 0.0,
            'we_ho': 0,
            'wind': 0.0,
            'wind2': 0.0}
    predsdict[code] = 1.0
    lod = [predsdict for y in entries]
    
    #cycle through and assign values for predictors
    xaxis = []
    dates = []
    us_holidays = holidays.UnitedStates()
    for line in range(0,len(entries)):
        lod[line]['temp'] = float(entries[line][0].get('english'))
        lod[line]['temp2'] = lod[line]['temp']**2
        lod[line]['wind'] = float(entries[line][1].get('english'))
        lod[line]['hour'] = float(entries[line][2].get('hour_padded'))
        lod[line]['hour2'] = lod[line]['hour']**2    
        xaxis.append(entries[line][2].get('civil'))   
        lod[line][entries[line][3]] = 1.0
        dates.append(datetime.strptime(entries[line][2].get('pretty'), 
                                       "%H:%M %p %Z on %B %d, %Y"))
        if (dates[-1].weekday() >= 5 or dates[-1] in us_holidays):
            lod[line]['we_ho'] = 1
    
    #return variables needed later
    return {'predictors':lod, 'xaxis':xaxis, 'dates':dates}


#########functions for running the app###########

@app.route('/')
def main():
  return redirect('/index')


@app.route('/index', methods=['GET','POST'])
def runmypage():
    if request.method=='GET':
        return render_template('index.html')

    
@app.route('/result', methods=['GET','POST'])
def getresult():
    code = request.form['option']
    key = '85df9c6c899ae271'  #fix this later
    #GET CURRENT WEATHER DATA and SEND TO PLOT
    hourdat = get_hourly_forecast(key, code)
    today = hourdat['dates'][1]
  

    #RENDER
    return render_template('result.html', code=code, date=today, data=hourdat['predictors']) #, script=script, div=div) #send values you need in the result page


@app.route('/info', methods=['GET','POST'])
def get_specs():
    if request.method=='GET':
        return render_template('info.html')

if __name__ == '__main__':
    #app.run(host='0.0.0.0', debug=True)
    app.run()

