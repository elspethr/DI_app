#import requests as req
import numpy as np
import pandas as pd
from flask import Flask,render_template,request,redirect
#from bokeh.plotting import figure, show
#from bokeh.io import output_notebook
#from bokeh.embed import components
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def main():
  return redirect('/index')


@app.route('/index', methods=['GET','POST'])
def runmypage():
    if request.method=='GET':
        return render_template('index.html')

    
#def stock_chart(opening, adjopen, close, adjclose, x, y1, y2, y3, y4):
#    p = figure(tools="pan,wheel_zoom,box_zoom,reset,resize", x_axis_type="datetime", title='Date from Quandle WIKI set')
#    if opening:
#        p.line(x, y1, legend="Open", line_color="purple", line_width=2)
#    if adjopen:
#        p.line(x, y2, legend="Adj. open", line_color="darkslateblue", line_width=2)
#    if close:   
#       p.line(x, y3, legend="Close", line_color="crimson", line_width=1.5)
#    if adjclose:  
#       p.line(x, y4, legend="Adj. close", line_color="lightseagreen", line_width=1.5)
#    p.xaxis.axis_label = 'Date'
#    p.yaxis.axis_label = 'Price'
#    p.legend.location = "bottom_right"
#    return p
    

@app.route('/result', methods=['GET','POST'])
def getresult():
    code = request.form['option']
    #if 'feature1' in request.form:
        #code = "Disneyland"
    #if 'feature2' in request.form:
        #code = "California Adventure"
    #
    #try:
        #api_url = 'https://www.quandl.com/api/v3/datasets/WIKI/%s/data.json' %code
        #session = req.Session()
        #session.mount('https://', req.adapters.HTTPAdapter(max_retries=3))
        #data = session.get(api_url).json()
    #except requests.exceptions.RequestException as e:
        #print e
        #sys.exit(1)
    #EXTRACT
    #d1 = data["dataset_data"]["data"]
    #colnames = data["dataset_data"]["column_names"]
    #MAKE A NICE DATAFRAME
    #df = pd.DataFrame(d1, columns=colnames)
    #df.set_index("Date")
    #SEND TO PLOT
    #dates = [datetime.strptime(x, '%Y-%m-%d') for x in df["Date"]] #convert x to dates
    #bplt = stock_chart(opening, adjopen, close, adjclose,
                       #dates, df["Open"], df["Adj. Open"], df["Close"], df["Adj. Close"])
    #script, div = components(bplt)
    #RENDER
    return render_template('result.html', code=code) #, script=script, div=div) #send values you need in the result page
   

if __name__ == '__main__':
    #app.run(host='0.0.0.0', debug=True)
    app.run()
