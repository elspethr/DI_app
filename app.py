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
import numpy

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
        predsdict[line[3]] = 1.0

        #print line[2]
        #dates.append(datetime(int(line[2]["year"]),int(line[2]["mon"]),int(line[2]["mday"]),int(line[2]["hour"]),int(line[2]["min"]),int(line[2]["sec"])))
        dates.append(int(line[2]['epoch']))
        #dates.append(datetime.strptime(line[2].get('pretty'), "%I:%M %p %Z on %B %d, %Y"))
        date=datetime.utcfromtimestamp(int(line[2]['epoch']))
        if(date.weekday() >= 5 or date in us_holidays):
            predsdict['we_ho'] = 1
        #if predsdict['hour'] >= 8 and predsdict['hour'] <= 22:
        preds.append(predsdict)
    
    #return variables needed later
    return {'predictors':preds, 'dates':dates}


def make_predictions(hourdat):
    with open('tweet_model.pkl', 'rb') as f:
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
    #key = '85df9c6c899ae271'  #fix this later

    #GET CURRENT WEATHER DATA and PREDICT
    #hourdat = get_hourly_forecast(key, code)
    #estimates = np.ndarray.tolist(make_predictions(hourdat['predictors']))
    #estsend = json.dumps(estimates)

    #SET UP VARIABLES FOR HTML
    #temp = current['temp']
    #wind = current['wind']
    
    #RENDER
    return render_template('result.html', code=code)#, temp=temp, wind=wind)

    
@app.route('/info', methods=['GET','POST'])
def get_specs():
    if request.method=='GET':
        return render_template('info.html')

    
@app.route('/query', methods=['GET','POST'])
def get_query():
    if request.method=='GET':
        code = request.args.get('option')
        #print request.form
        key = '85df9c6c899ae271'  #fix this later

        #GET CURRENT WEATHER DATA and PREDICT
        hourdat = get_hourly_forecast(key, code)
        estimates = np.ndarray.tolist(numpy.asarray(make_predictions(hourdat['predictors'])))
        #xaxis = hourdat['xaxis']
        sendtojs = [{"x":hourdat["dates"][i],"y":estimates[i]} for i in range(len(estimates))]
        
        return json.dumps(sendtojs)
    
 ##########run my app##############
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    #app.run(debug=True)
