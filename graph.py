#!/usr/bin/env python
from datetime import timedelta
from collections import OrderedDict
import pandas as pd
from copy import deepcopy
from matplotlib import dates
import matplotlib.pyplot as plt; plt.rcdefaults()
import datetime

from main import *

#these are globals that determine interval to tally on and number of elements to create rolling average over
#recommend setting to 5 for longer time range
IVAL=2  #interval in minutes
ROLL=2  #how many intervals to roll

def process_log(log):
    requests = get_requests(log)
    totals = get_times(requests)
    return totals

def get_times(requests):
    """
    return list of times
    """
    timelist = []
    for req in requests:
        timelist.append(convertStrToDatetime(req[1]))
    return timelist

def convertStrToDatetime(dtstr):
    # we will drop the timezone
    return datetime.datetime.strptime(dtstr[:-6], "%d/%b/%Y:%H:%M:%S")

def generate_graph_dict(times):
    """
    param list of times, returned from process_log in this file
    returns ordered dictionary of form { time_slice_start : request_count }
    """

    #block is the amount of time that we tally over, set with IVAL global
    block = timedelta(minutes=IVAL)
    start = times[0]
    graphdict = OrderedDict()

    # iterate through all times and tally up each request, if we reach end, move to next block
    for time in times:
        end = start + block
        if(time < end):
            try:
                graphdict[start] += 1
            except:
                graphdict[start] = 1
        else:
            # if we haven't yet created a count for the time (eg if no entries in time range) set to 0, then seek start to next block
            if start not in graphdict:
                graphdict[start] = 0
            start = end

    return graphdict

def graphcumulative(graphdict):
    """
    param graphdict returned from generate_graph_dict()
    graph total number of requests over time
    """
    dates = graphdict.keys()
    counts = graphdict.values()
    cp = deepcopy(graphdict)
    i = 1
    for date in dates[1:]:
        cp[date] = counts[i] + counts[i-1]
        counts[i] = cp[date]
        i += 1
    graph(cp, 'Cumulative')

def graph(graphdict, title='Graph'):
    """
    param graphdict returned from generate_graph_dict()
    basic graph of graphdict data
    """
    x = graphdict.keys()
    y = graphdict.values()

    fig, ax = plt.subplots(1)

    ax.xaxis_date()
    xfmt = dates.DateFormatter('%d-%m-%y %H:%M')
    ax.xaxis.set_major_formatter(xfmt)

    locs, labels = plt.xticks()
    plt.setp(labels, rotation=30, horizontalalignment='right')

    plt.plot(x,y)
    ax.set_title(title)

    plt.show()

def graphrolling(graphdict):
    """
    param of ordered dictionary of form { time_slice_start : request_count } returned from generate_graph_dict()
    displays a graph of the log with rolling average
    """
    #put graphdict into a dataframe
    data = { 'date':graphdict.keys(), 'count':graphdict.values() }
    df = pd.DataFrame(data, columns = ['date', 'count'])

    df.index = df['date']
    del df['date']

    #create roll
    dfb = pd.rolling_mean(df, ROLL)

    ax = dfb.plot()
    ax.xaxis_date()
    xfmt = dates.DateFormatter('%d-%m-%y %H:%M')
    ax.xaxis.set_major_formatter(xfmt)
    titlestr = "Rolling Average on " + str(ROLL) + " count roll"
    ax.set_title(titlestr)

    plt.sca(ax)
    plt.show()

if __name__ == '__main__':

    #nginx access log, standard format
    log_file = open('example.log', 'r')

    # return list of times
    times = process_log(log_file)
    # tally requests in each time slice
    gd = generate_graph_dict(times)

    ivalstr = "On interval " + str(IVAL) + " minutes"

    graph(gd, ivalstr)
    graphrolling(gd)
    graphcumulative(gd)
