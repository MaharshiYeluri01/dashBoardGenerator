from flask import Flask, render_template,request
import json
import plotly
import chart_studio.plotly as py
import plotly.graph_objs as go
import numpy as np

import pandas as pd

app = Flask(__name__)
db=pd.read_csv("data/sampleData.csv")
Min,Max=pd.to_datetime('2020-07-01'),pd.to_datetime('2020-07-31')

modeDictionary={'1':'Air','2':'Land','3':'Sea'}
lanes=list(db['Lane'].unique())
modes=list(modeDictionary.values())

def applyFilters(mode,lane,applyDateFilter=None):
    filteredData=db.query(f"Mode=='{mode}'")
    filteredData=filteredData.query(f"Lane=='{lane}'")
    return filteredData

def calculateMetrics(filteredData):
    filteredFrameGrouped=filteredData.groupby("Supplier reference name")
    unitCostMetric=filteredFrameGrouped.apply(lambda f:f['Cost calc'].mean()).sort_values()
    inFullMetric=filteredFrameGrouped.apply(lambda f:f['In full calc'].mean()*100).sort_values()
    onTimeMetric=filteredFrameGrouped.apply(lambda f:f['On time calc'].sum()).sort_values()
    return unitCostMetric,inFullMetric,onTimeMetric
#marker={'color':colors}

def ovdColor(colorset,index):
    colorset[index]='yellow'
    return colorset

def generateBarColors(unitCostMetric,inFullMetric,onTimeMetric):
    targetBar=unitCostMetric.index[0]
    ci2=list(inFullMetric.index).index(targetBar)
    ci3=list(onTimeMetric.index).index(targetBar)
    colorSet=['blue']*len(unitCostMetric)
    return ovdColor(colorSet.copy(),0),ovdColor(colorSet.copy(),ci2),ovdColor(colorSet.copy(),ci3)


def createJson(trace):
    return json.dumps(trace, cls=plotly.utils.PlotlyJSONEncoder)




@app.route('/')
def index():
    
    return render_template('index.html',lanes=lanes,modes=modes)

@app.route('/Metrics/<mode>/<lane>')
def bar(mode,lane):
    mode=modeDictionary[mode]
    data=applyFilters(mode,lane)
    if len(data)>=1:

        unitCostMetric,inFullMetric,onTimeMetric=calculateMetrics(data)
        colors=generateBarColors(unitCostMetric,inFullMetric,onTimeMetric)
        trace1 = go.Bar(x=unitCostMetric.index, y=unitCostMetric.values,width=0.5,marker={'color':colors[0]})
        trace2 = go.Bar(x=inFullMetric.index, y=inFullMetric.values,width=0.5,marker={'color':colors[1]})
        trace3 = go.Bar(x=onTimeMetric.index, y=onTimeMetric.values,width=0.5,marker={'color':colors[2]})
        
        return render_template('chart.html',barJSON1=createJson(trace1),
        barJSON2=createJson(trace2),barJSON3=createJson(trace3),mode=mode,lane=lane)
    return f'No enough data, {mode},{lane},{len(data)} out of {len(db)} records'


if __name__ == '__main__':
    app.run(debug=True)