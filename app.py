#import requests as req
import numpy as np
import pandas as pd
from flask import Flask,render_template,request,redirect,jsonify
from datetime import datetime
import holidays
import urllib2
import json
import matplotlib as plt
import dill

app = Flask(__name__)


######functions for getting data and plotting########

def get_hourly_forecast(key, code):
    #open webpage
    f = urllib2.urlopen('http://api.wunderground.com/api/%s/hourly/q/CA/KFUL.json'%(key))
    json_string = f.read()
    parsed_json = json.loads(json_string)
    f.close()
    
    #get needed dictionaries from json
    predvars = ['temp', 'wspd', 'FCTTIME', 'condition']
    entries = [[x[column] for column in predvars] for x in parsed_json['hourly_forecast']]
    
    #cycle through and assign values for predictors
    xaxis = []
    dates = []
    preds = []
    us_holidays = holidays.UnitedStates()
    for line in entries:
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
        predsdict['temp'] = float(line[0].get('english'))
        predsdict['temp2'] = predsdict['temp']**2
        predsdict['wind'] = float(line[1].get('english'))
        predsdict['wind2'] = predsdict['wind']**2
        predsdict['hour'] = float(line[2].get('hour_padded'))
        predsdict['hour2'] = predsdict['hour']**2 
        xaxis.append(line[2].get('civil'))   
        predsdict[line[3]] = 1.0
        dates.append(datetime.strptime(line[2].get('pretty'), 
                                       "%H:%M %p %Z on %B %d, %Y"))
        if (dates[-1].weekday() >= 5 or dates[-1] in us_holidays):
            predsdict['we_ho'] = 1
        preds.append(predsdict)
    
    #return variables needed later
    return {'predictors':preds, 'xaxis':xaxis, 'dates':dates}


def make_predictions(hourdat):
    with open('meanwait_model.pkl', 'rb') as f:
        model = dill.load(f)
    response = model.predict(hourdat)
    return response

#def make_plot()


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

    #GET CURRENT WEATHER DATA and PREDICT
    hourdat = get_hourly_forecast(key, code)
    estimates = np.ndarray.tolist(make_predictions(hourdat['predictors']))
    estsend = json.dumps(estimates)

    #SET UP VARIABLES FOR HTML
    xlabels = hourdat['dates']
    current = hourdat['predictors'][1]
    temp = current['temp']
    wind = current['wind']
    
    #RENDER
    return render_template('result.html', code=code, temp=temp, wind=wind, xlabels=xlabels, estimates=estsend)

    
@app.route('/info', methods=['GET','POST'])
def get_specs():
    if request.method=='GET':
        return render_template('info.html')

    
@app.route('/query', methods=['GET','POST'])
def get_query():
    if request.method=='GET':
        code = request.args.get('option')
        print request.form
        key = '85df9c6c899ae271'  #fix this later

        #GET CURRENT WEATHER DATA and PREDICT
        hourdat = get_hourly_forecast(key, code)
        estimates = np.ndarray.tolist(make_predictions(hourdat['predictors']))
        xaxis = hourdat['xaxis']
        print estimates
        
        return json.dumps(estimates)
    
 ##########run my app##############
    
if __name__ == '__main__':
    #app.run(host='0.0.0.0', debug=True)
    app.run()

