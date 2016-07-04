#import requests as req
import numpy as np
from flask import Flask,render_template,request,redirect,jsonify
from datetime import datetime, timedelta
import holidays
import urllib2
import json
import dill
import logging
import sys
import pandas as pd

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

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
    dates = []
    preds = []
    us_holidays = holidays.UnitedStates()
    for line in entries:
        predsdict = {'California Adventure': 0.0,
                    'Clear': 0.0,
                    'Disneyland': 0.0,
                    'Fog':0.0,
                    'Haze': 0.0,
                    'Heavy Rain': 0.0,
                    'Light Rain': 0.0,
                    'Mist': 0.0,
                    'Mostly Cloudy': 0.0,
                    'Overcast': 0.0,
                    'Partly Cloudy': 0.0,
                    'Rain': 0.0,
                    'Scattered Clouds': 0.0,
                    'Unknown': 0.0,
                    'hour': 99.9,
                    'hour2': 0.0,
                    'temp': 0.0,
                    'temp2': 0.0,
                    'business_day': 0.0,
                    'holiday': 0.0,
                    'wind': 0.0,
                    'wind2': 0.0}
        predsdict[code] = 1.0
        predsdict['temp'] = float(line[0].get('english'))
        predsdict['temp2'] = predsdict['temp']**2
        predsdict['wind'] = float(line[1].get('english'))
        predsdict['wind2'] = predsdict['wind']**2
        predsdict['hour'] = float(line[2].get('hour_padded'))
        predsdict['hour2'] = predsdict['hour']**2
        predsdict[line[3]] = 1.0 #set conditions

        dates.append(int(line[2]['epoch']))
        date=datetime.utcfromtimestamp(int(line[2]['epoch']))
        if(date.weekday() >= 5):
            predsdict['business_day'] = 1
        if(date in us_holidays):
            predsdict['holiday'] = 1
        preds.append(predsdict)
    
    #return variables needed later
    return {'predictors':preds, 'dates':dates}


def get_daily_forecast(key, code):
    #open webpage
    f = urllib2.urlopen('http://api.wunderground.com/api/%s/forecast10day/q/CA/KFUL.json'%(key))
    json_string = f.read()
    parsed_json = json.loads(json_string)
    f.close()

    #get needed dictionaries from json
    days = parsed_json['forecast']['simpleforecast']['forecastday']
    predvars = ['avehumidity', 'avewind', 'conditions', 'date', 'high', 'low', 'qpf_day']
    entries = [[x[column] for column in predvars] for x in days]

    #cycle through and assign values for predictors
    dailydates = []
    dailypreds = []
    us_holidays = holidays.UnitedStates()
    for line in entries:
        predsdict = {'California Adventure': 0.0,
                    'Clear': 0.0,
                    'Disneyland': 0.0,
                    'Haze': 0.0,
                    'Heavy Rain': 0.0,
                    'Light Rain': 0.0,
                    'Mostly Cloudy': 0.0,
                    'Overcast': 0.0,
                    'Partly Cloudy': 0.0,
                    'dow': 0,
                    'temp': 0.0,
                    'temp2': 0.0, 
                    'lotemp': 0.0,
                    'lotemp2': 0.0, 
                    'business_day': False,
                    'holiday': False,
                    'wind': 0.0,
                    'wind2': 0.0, 
                    'humidity':0.0, 
                    'precip': 0.0,
                     0:0,
                     1:0,
                     2:0,
                     3:0,
                     4:0,
                     5:0,
                     6:0}
        predsdict[code] = 1.0
        predsdict['humidity'] = float(line[0])
        predsdict['wind'] = float(line[1].get('mph'))
        predsdict['wind2'] = predsdict['wind']**2
        predsdict['wind'] = float(line[1].get('mph'))
        predsdict['temp'] = float(line[4].get('fahrenheit'))
        predsdict['temp2'] = predsdict['temp']**2
        predsdict['lotemp'] = float(line[5].get('fahrenheit'))
        predsdict['lotemp2'] = predsdict['lotemp']**2
        predsdict['precip'] = line[6].get('in')
        if not predsdict['precip']: predsdict['precip'] = 0.0
        predsdict[line[2]] = 1.0
        
        dailydates.append(int(line[3]['epoch'])-28800) #- timedelta(hours=8))
        date=datetime.utcfromtimestamp(int(line[3]['epoch'])) - timedelta(hours=8)
        predsdict['dow'] = date.weekday()
        predsdict['dow2'] = predsdict['dow']**2
        predsdict[date.weekday()] = 1.0
        if(date.weekday() >= 5):
            predsdict['business_day'] = True
        if(date in us_holidays):
            predsdict['holiday'] = True
        dailypreds.append(predsdict)
    #print dailypreds   
    #return variables needed later
    return {'predictors':dailypreds, 'dates':dailydates}


def make_hourly_predictions(hourdat):
    with open('hourly_model.pkl', 'rb') as f:
        model = dill.load(f)
    response = model.predict(hourdat)
    return response


def make_daily_predictions(dailydat):
    with open('fiveday_model.pkl', 'rb') as f:
        model = dill.load(f)
    response = model.predict(dailydat)
    return response


def get_hourly_averages(code):
    with open('hourly_averages.pkl', 'rb') as f:
        data = dill.load(f)
    hourly_averages = {}   
    for line in data:
        if line['search'] == code:
            hourly_averages[line['hour']] = line['peracre']
    return hourly_averages

            
def get_daily_averages(code):
    with open('day_averages.pkl', 'rb') as f:
        data = dill.load(f)
    daily_averages = {}   
    for line in data:
        if line['search'] == code:
             daily_averages[line['dow']] = line['peracre']
    return daily_averages


#########functions for running the app###########

@app.route('/')
def main():
  return redirect('/index')


@app.route('/index', methods=['GET','POST'])
def runmypage():
    if request.method=='GET':
        return render_template('index.html')
    
    
@app.route('/result', methods=['GET'])
def getresult():
    code = request.args.get('option')
    return render_template('result.html', code=code)

    
@app.route('/info', methods=['GET','POST'])
def get_specs():
    if request.method=='GET':
        return render_template('info.html')

    
@app.route('/query', methods=['GET','POST'])
def get_query():
    if request.method=='GET':
        code = request.args.get('option')
        key = '85df9c6c899ae271'
        hourlydat=get_hourly_forecast(key, code)
        hourlyavgs=get_hourly_averages(code)

        averages=[]
        estimates=[]
        predictions=make_hourly_predictions(hourlydat["predictors"])
        for i in range(len(hourlydat["predictors"])):
            hour=hourlydat["predictors"][i]["hour"]
            if hour in hourlyavgs:
                averages.append({"x":hourlydat["dates"][i],"y":hourlyavgs[hour]})
                estimates.append({"x":hourlydat["dates"][i],"y":predictions[i]})
            else:
                averages.append({"x":hourlydat["dates"][i],"y":None})
                estimates.append({"x":hourlydat["dates"][i],"y":None})
        
        results={"averages":averages,"estimates":estimates}
        
        return json.dumps(results)
    
    
@app.route('/dailyquery', methods=['GET','POST'])
def get_query2():
    if request.method=='GET':
        code = request.args.get('option')
        #code = 'Disneyland'
        key = '85df9c6c899ae271'
        dailydat = get_daily_forecast(key, code)
        daverages = get_daily_averages(code)
        dailyestimates = make_daily_predictions(dailydat['predictors'])
        #print dailyestimates
        dailyaverage = []
        dates = []
        for i in dailydat["dates"]:
            date = datetime.fromtimestamp(i)
            dow = date.weekday()
            dailyaverage.append(daverages[dow])
            dates.append(i)
        dailysendtojs = [{"x":dates[i],"y":dailyestimates[i], "y2":dailyaverage[i]} for i in range(len(dailyestimates))]
        
    return json.dumps(dailysendtojs)

    
##########run my app##############
import pprint
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    #app.run(debug=True)
    #get_query2()
