__author__ = "Richard O'Dwyer"
__email__ = "richard@richard.do"
__license__ = "None"

import re
from operator import itemgetter

def process_log(log):
    requests = get_requests(log)
    files = get_files(requests)
    totals = file_occur(files)
    return totals

def get_requests(f):
    log_line = f.read()
    pat = (r''
           '(\d+.\d+.\d+.\d+)\s-\s-\s' #IP address
           '\[(.+)\]\s' #datetime
           '"GET\s(.+)\s\w+/.+"\s' #requested file
           '(\d+)\s' #status
           '(\d+)\s' #bandwidth
           '"(.+)"\s' #referrer
           '"(.+)"' #user agent
        )
    requests = find(pat, log_line)
    return requests

def find(pat, text):
    match = re.findall(pat, text)
    if match:
        return match
    return False

def get_files(requests):
    #get requested files with req
    requested_files = []
    for req in requests:
        # req[2] for req file match, change to
        # data you want to count totals
        requested_files.append(req[2])
    return requested_files

def file_occur(files):
    # file occurrences in requested files
    d = {}
    for file in files:
        d[file] = d.get(file,0)+1
    return d

if __name__ == '__main__':

    #nginx access log, standard format
    log_file = open('example.log', 'r')

    # return dict of files and total requests
    urls_with_counts = process_log(log_file)
    # sort them by total requests descending
    sorted_by_count = sorted(urls_with_counts.items(), key=itemgetter(1), reverse=True)
    print(sorted_by_count)
