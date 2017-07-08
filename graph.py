from datetime import timedelta
from collections import OrderedDict
import pandas as pd
from copy import deepcopy
from matplotlib import dates
import matplotlib.pyplot as plt; plt.rcdefaults()
import datetime
from dateutil.parser import parse

from main import *

IVAL=5  #interval in minutes
ROLL=5  #how many intervals to roll

def process_log(log):
    requests = get_requests(log)
    #files = get_files(requests)
    #totals = file_occur(files)
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
    #03/Jul/2017:09:50:05 +1000
    # we will drop the +1000, so graph will be in UTC
    #return datetime.datetime.strptime(dtstr, "%d/%b/%Y:%H:%M:%S +")
    print dtstr
    return parse(dtstr)

def generate_graph_dict(times):
    block = timedelta(minutes=IVAL)
    start = times[0]
    graphdict = OrderedDict()
    #print start
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
            #print start

    return graphdict

def graphcumulative(graphdict):
    dates = graphdict.keys()
    counts = graphdict.values()
    cp = deepcopy(graphdict)
    i = 1
    for date in dates[1:]:
        cp[date] = counts[i] + counts[i-1]
        counts[i] = cp[date]
        #print date
        #print i
        #print counts[i-1]
        #print counts[i]
        #print graphdict[date]
        i += 1
    graph(cp, 'Cumulative')

def graph(graphdict, title='Graph'):
    x = graphdict.keys()
    y = graphdict.values()
    #print graphdict.keys()
    #plt.plot(x, y)
    print type(x)
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
    #put graphdict into a dataframe
    data = { 'date':graphdict.keys(), 'count':graphdict.values() }
    df = pd.DataFrame(data, columns = ['date', 'count'])
    #print(df)
    df.index = df['date']
    del df['date']
    #print df

    #create roll
    dfb = pd.rolling_mean(df, ROLL)
    #print dfb

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

    # return dict of files and total requests
    times = process_log(log_file)
    # sort them by total requests descending
    #sorted_by_count = sorted(urls_with_counts.items(), key=itemgetter(1), reverse=True)
    #print(times)
    gd = generate_graph_dict(times)
    for k,v in gd.items():
        if(v > 0):
            print(str(k) + " " + str(v))
            #pass
    ivalstr = "On interval " + str(IVAL) + " minutes"
    graph(gd, ivalstr)
    graphrolling(gd)
    graphcumulative(gd)
