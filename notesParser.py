import os
import re
import pprint
from collections import defaultdict
import csv
import json
import itertools
import glob
import sys, getopt
import argparse
import numpy as np
from datetime import datetime, timedelta
import pandas as pd

re1='(N)'	# Any Single Word Character (Not Whitespace) 1
re2='(o)'	# Any Single Word Character (Not Whitespace) 2
re3='(t)'	# Any Single Word Character (Not Whitespace) 3
re4='(e)'	# Any Single Word Character (Not Whitespace) 4
re5='(s)'	# Any Single Word Character (Not Whitespace) 5
re6='(_)'	# Any Single Character 1
re7='(\\d)'	# Any Single Digit 1
re8='(\\d)'	# Any Single Digit 2
re9='(\\d)'	# Any Single Digit 3
re10='(\\d)'	# Any Single Digit 4
re11='(\\d)'	# Any Single Digit 5
re12='(\\d)'	# Any Single Digit 6
re13='(\\d)'	# Any Single Digit 7
re14='(\\d)'	# Any Single Digit 8
re15='(\\.)'	# Any Single Character 2
re16='(l)'	# Any Single Word Character (Not Whitespace) 6
re17='(o)'	# Any Single Word Character (Not Whitespace) 7
re18='(g)'	# Any Single Word Character (Not Whitespace) 8


runCompleteRe = re.compile(r'Run "(.+)" completed. (.+)')
errorCoeRe = re.compile(r'(Start|End) Run Unsuccessful, ErrorCode = (\d+),')
fileName_pattern = re.compile( r'(N)(o)(t)(e)(s)(_)(\d)(\d)(\d)(\d)(\d)(\d)(\d)(\d)(\.)(l)(o)(g)')
#text = "Notes_2017"
#fileName_pattern  = re.compile(re1+re2+re3+re4+re5+re6+re7+re8+re9+re10+re11+re12+re13+re14+re15+re16+re17+re18,re.IGNORECASE|re.DOTALL)
#m = rg.search(txt)
filePattern = re.compile(r'".*?"')
nameVariations = re.compile(r'(?<=NameVariations).*')
totalTimeInSystem = re.compile(r'(?<=TotalTimeInSystem\(Ms\)).*')
lookupQueryTime = re.compile(r'(?<=LookupQueryTime\(Ms\)).*')
cloudLookupTraveAndPT = re.compile(r'(?<=CloudLookupTravelAndProcessTime\(Ms\)).*')
cloudLookupTravelTime = re.compile(r'(?<=CloudLookupTravelTime\(Ms\)).*')
timingRe = re.compile(r'(.+) \( (Count): (\d+) (Min): (\d+) (Max): (\d+) (Average): (\d+)\)')
datePattern = re.compile(r'Notes_(\d+).log')

['Date','NameVariations Count','NameVariations Max','NameVariations Average','NameVariations Min','LookupQueryTime(Ms) Count','LookupQueryTime(Ms) Max','LookupQueryTime(Ms) Average','LookupQueryTime(Ms) Min','TotalProcessTime(Ms) Count','TotalProcessTime(Ms) Max','TotalProcessTime(Ms) Average','TotalProcessTime(Ms) Min','CheckMoveRequestsPerSecond Count','CheckMoveRequestsPerSecond Max','CheckMoveRequestsPerSecond Average','CheckMoveRequestsPerSecond Min','TimeRemainingAtReceipt(Ms) Count','TimeRemainingAtReceipt(Ms) Max','TimeRemainingAtReceipt(Ms) Average','TimeRemainingAtReceipt(Ms) Min','CloudLookupTravelAndProcessTime(Ms) Count','CloudLookupTravelAndProcessTime(Ms) Max','CloudLookupTravelAndProcessTime(Ms) Average','CloudLookupTravelAndProcessTime(Ms) Min','TotalTimeInSystem(Ms) Count','TotalTimeInSystem(Ms) Max','TotalTimeInSystem(Ms) Average','TotalTimeInSystem(Ms) Min','ResponseSendTime(Ms) Count','ResponseSendTime(Ms) Max','ResponseSendTime(Ms) Average','ResponseSendTime(Ms) Min','CloudLookupTravelTime(Ms) Count','CloudLookupTravelTime(Ms) Max','CloudLookupTravelTime(Ms) Average','CloudLookupTravelTime(Ms) Min']

def checkAnomalies(dict, fileName):
    #lookupQueryTimeAvg
    LookupQueryTimeAvg = 0
    CloudLookupTravelTimeAvg = 0
    if dict:
        for statType, statistics in dict.items():
            if 'LookupQueryTime' in statType:
                for stat,value in statistics.items():
                    if 'Average' in stat:
                        LookupQueryTimeAvg = value
                        #print str(statType) + ' : ' + str(stat) + ' : ' + str(value)
            if 'CloudLookupTravelAndProcessTime(Ms)' in statType:
                for stat,value in statistics.items():
                    if 'Average' in stat:
                        CloudLookupTravelTimeAvg = value
                        # print str(statType) + ' : ' + str(stat) + ' : ' + str(value)
        if LookupQueryTimeAvg > CloudLookupTravelTimeAvg:
            print 'WARNING CLOUDLookupTravelTimeAvg is greater than LookupQueryTimeAvg in runlogFile Entry will not be added to runlog dictionary ' + str(fileName)
            return True
            #print 'WARNING CLOUDLookupTravelTimeAvg is greater than LookupQueryTimeAvg in runlogFile ' + str(fileName)
        else:
            return False
    #print dict
    else:
        return False
    pass

def regexCompile(patterns):
    patternCompile = re.compile('(?<=)' + pattern + '.*')
    return patternCompile

def processTransportLog(logDir, fileName):
    #LogFilesDirectory = r'C:\Users\ccole\Documents\Playground\python_project\logFiles\\'
    #fileName = LogFilesDirectory + file + '.log'
    fileName = os.path.join(logDir, fileName)
    timingData = {}
    #print fileName
    if os.path.exists(fileName):
        #print 'file exists'
        lines = [line.rstrip() for line in open(fileName, 'r')]
        for line in lines:
            timingMatch = timingRe.match(line)
            if timingMatch:
                statsDict = {}
                name = timingMatch.group(1)
                if name in timingData:
                    #print '%s already found in file %s' % (name, fileName)
                    pass
                else:
                    count = int( timingMatch.group(3) )
                    min = int(timingMatch.group(5))
                    max = int(timingMatch.group(7))
                    avg = int(timingMatch.group(9))
                    statsDict[timingMatch.group(2)] = count
                    statsDict[timingMatch.group(4)] = min
                    statsDict[timingMatch.group(6)] = max
                    statsDict[timingMatch.group(8)] = avg
                    timingData[name]= statsDict
            '''
            lookupQueryTimeStats = lookupQueryTime.search(line)
            cloudLookupTravelTimeStats = cloudLookupTravelTime.search(line)
            cloudLookupTravelAndPTStats = cloudLookupTravelTime.search(line)

            if lookupQueryTimeStats:
                pass
                #print regexCompile(fileName, 'LookupQueryTime\(Ms\)').search(line).group(0)
            if cloudLookupTravelTimeStats:
                pass
            if cloudLookupTravelAndPTStats:
                #print cloudLookupTravelAndPTStats.group(0)
                stats = re.findall(r"[^\W\d_]+|\d+", cloudLookupTravelAndPTStats.group(0))
                statsDict = dict(itertools.izip_longest(*[iter(stats)] * 2, fillvalue=""))
                #print statsDict
                countIndex = stats.index('Count')
                minIndex = stats.index('Min')
                maxIndex = stats.index('Max')
                avgIndex = stats.index('Average')
                #print stats[countIndex + 1] + ' ' + stats[minIndex + 1]

                pass
            '''
    else:
        pass
        #print 'file doesn\'t exist'
    #print timingData
    #print 'In processTransportLog'
    #print timingData
    if checkAnomalies(timingData, fileName) is True:
        return None
    else:
        return timingData


def writeLogCSV(fileName, runlogDict, statsNames):
    runlogDictHeader = ['Date']
    '''
    ,'NameVariations Count','NameVariations Min','NameVariations Max','NameVariations Average',
    'LookupQueryTime(Ms) Count','LookupQueryTime(Ms) Min','LookupQueryTime(Ms) Max','LookupQueryTime(Ms) Average',
    'TotalProcessTime(Ms) Count','TotalProcessTime(Ms) Min','TotalProcessTime(Ms) Max','TotalProcessTime(Ms) Average',
    'CheckMoveRequestsPerSecond Count','CheckMoveRequestsPerSecond Min','CheckMoveRequestsPerSecond Max','CheckMoveRequestsPerSecond Average',
    'TimeRemainingAtReceipt(Ms) Count','TimeRemainingAtReceipt(Ms) Min','TimeRemainingAtReceipt(Ms) Max','TimeRemainingAtReceipt(Ms) Average',
    'CloudLookupTravelAndProcessTime(Ms) Count','CloudLookupTravelAndProcessTime(Ms) Min','CloudLookupTravelAndProcessTime(Ms) Max','CloudLookupTravelAndProcessTime(Ms) Average',
    'TotalTimeInSystem(Ms) Count','TotalTimeInSystem(Ms) Min','TotalTimeInSystem(Ms) Max','TotalTimeInSystem(Ms) Average',
    'ResponseSendTime(Ms) Count','ResponseSendTime(Ms) Min','ResponseSendTime(Ms) Max','ResponseSendTime(Ms) Average',
    'CloudLookupTravelTime(Ms) Count','CloudLookupTravelTime(Ms) Min','CloudLookupTravelTime(Ms) Max','CloudLookupTravelTime(Ms) Average']
    '''
    order = ['Count', 'Min', 'Max', 'Average']
    records = []
    runlogDict.viewkeys()
    #print runlogDict
    #for Date, stat0 in runlogDict.items():
    for Date in sorted(runlogDict):
        stat0 = runlogDict[Date]
        localDict = {}
        localDict['Date'] = Date.strftime("%A %B %d %Y")
        for statsName, statsDict in stat0.items():
            if statsName not in statsNames:
                continue
            for statsType in order:
                #print statsType
                value = statsDict[statsType]
                if type(value) == np.float64:
                    value = '%.1f' % value
                if statsType in statsDict:
                    newKey = statsName + ' ' + statsType
                    if newKey not in runlogDictHeader:
                        runlogDictHeader.append(newKey)
                    localDict[newKey] = value
        #print localDict
        #sorted(localDict.items(), key=lambda i:keyorder.index(i[0]))
        records.append(localDict)

    with open(fileName, 'wb') as f:
        writer = csv.DictWriter(f, fieldnames=runlogDictHeader)
        writer.writeheader()
        writer.writerows(records)


def process_files(logFiles):
    #cwd = os.getcwd()

    runlogDateDict = {}
    header = ['Date']
    startErrorHeader = []
    endErrorHeader = []
    records = []
    dateLogDict = {}

    for file in logFiles:

        date = datetime(year = int((datePattern.search(file)).group(1)[:4]), month=int((datePattern.search(file)).group(1)[4:6]), day=int((datePattern.search(file)).group(1)[6:8]))
        dateLogDict[date] = file

    for date in sorted(dateLogDict):
        fileHeader, fileStartErrorHeader, fileEndErrorHeader, fileRecordData, runlogDict = process_file(dateLogDict[date])
        fileRecordData['Date'] = date.strftime("%A %B %d %Y")
        runlogDateDict[date] = runlogDict
        runlogsummaryOut = os.path.join(os.path.dirname(os.path.abspath(logFiles[0])), 'runlogsummary.csv')
        #writeLogCSV(runlogsummaryOut, runlogDateDict)
        #print fileRecordData
        for column in fileHeader:
            if column not in header:
                header.append(column)



        fileStartErrorHeaderSet = set(fileStartErrorHeader)
        globalStartErrorHeaderSet = set(startErrorHeader)
        diff = fileStartErrorHeaderSet.difference(globalStartErrorHeaderSet)
        startErrorHeader = startErrorHeader + list(diff)

        fileEndErrorHeaderSet = set(fileEndErrorHeader)
        globalEndErrorHeaderSet = set(endErrorHeader)
        diff = fileEndErrorHeaderSet.difference(globalEndErrorHeaderSet)
        endErrorHeader = endErrorHeader + list(diff)
        records.append(fileRecordData)

    writeLogCSV(runlogsummaryOut, runlogDateDict, ['LookupQueryTime(Ms)', 'CloudLookupTravelAndProcessTime(Ms)', 'CloudLookupTravelTime(Ms)'])
    startErrorHeader.sort()
    endErrorHeader.sort()

    for errorNo in startErrorHeader:
        header.append("Start Error " + str(errorNo))
    for errorNo in endErrorHeader:
        header.append("End Error " + str(errorNo))

    with open(os.path.join(os.path.dirname(os.path.abspath(logFiles[0])), 'summary.csv'), 'wb') as f:
        writer = csv.DictWriter(f, header)
        writer.writeheader()
        writer.writerows(records)
    pass


def process_path(path):
    cwd = os.getcwd()
    logFiles = []
    if not(os.path.isabs(path)):
        path = os.getcwd()+ '\\' + path
    #print path

    if os.path.isdir(path):
        #process_files(dirName)
        #get log files from directory
        #print 'Its a directory'
        for file in glob.glob(os.path.join(path, "Notes_*.log")):
            #print file
            logFiles.append(os.path.join(path, file))
    elif os.path.isfile(path):
        #r'C:\Notes\nothing.log'
        filename = os.path.basename(path)
        if "Notes_" in filename and ".log" in filename:
            filename = os.getcwd() + filename
            #print filename
            logFiles.append(os.path.abspath(path))
            #print path

    if len(logFiles) == 0:
        print 'No Log files found'
    else:
        process_files(logFiles)

    #print logFiles
    #process_files(logFiles)


def process_file(inputFile):
    lines = [line.rstrip() for line in open(inputFile, 'r')]
    header = []
    recordData = {}
    runlogDict = {}
    runlogFiles = []
    #Create list of error codes.
    for line in lines:
        match = runCompleteRe.search(line)
        if match:
            stats = match.group(2).strip()
            filename = match.group(1) + '.log'
            #print filename
            thislogFileDict =  processTransportLog(os.path.dirname(os.path.abspath(inputFile)), filename)
            #print filename
            #print thislogFileDict
            #print 'DONE Printing Dict'


            print filename
            #pprint.pprint (thislogFileDict)
            if thislogFileDict:


                for key in thislogFileDict:
                    #print key

                    if key not in runlogDict:
                        runlogDict[key] = thislogFileDict[key]

                    elif thislogFileDict[key]['Count'] > 0:
                        runlogDict[key]['Count'] = runlogDict[key]['Count'] + thislogFileDict[key]['Count']
                        runlogDict[key]['Min'] = min(runlogDict[key]['Min'], thislogFileDict[key]['Min'])
                        runlogDict[key]['Max'] = max(runlogDict[key]['Max'], thislogFileDict[key]['Max'])
                        runlogDict[key]['Average'] = np.average([runlogDict[key]['Average'], thislogFileDict[key]['Average']], weights=[runlogDict[key]['Count'],thislogFileDict[key]['Count']])

            stats = stats.split(',')
            for stat in stats:
                stat = stat.split(':')
                key = stat[0].strip()
                value = int(stat[1].strip())

                if key not in recordData:
                    recordData[key] = 0

                recordData[key] += value

                if key not in header:
                    header.append(key)
            continue

    startErrorHeader = []
    endErrorHeader = []

    for line in lines:
        match = errorCoeRe.search(line)
        if match:
            startOrEnd = match.group(1)
            errNo = int(match.group(2))
            errorCode = startOrEnd + " Error " + str(errNo)

            if errorCode not in recordData:
                recordData[errorCode] = 0

            recordData[errorCode] += 1

            if startOrEnd == 'Start':
                if errNo not in startErrorHeader:
                    startErrorHeader.append(errNo)
            elif startOrEnd == 'End':
                if errNo not in endErrorHeader:
                    endErrorHeader.append(errNo)
            continue
    #print list(set(runlogDict))
    #print runlogDict
    return header, startErrorHeader, endErrorHeader, recordData, runlogDict









def find_error_codes(line):
    match = re.search(r' ErrorCode...(\d+)', line)
    if match:
        #print line
        return match.group(1)


def error_code_dictionary(errorCodeList):
    errorCodeDict = {}
    for x in errorCodeList:
        if(x in errorCodeDict):
            errorCodeDict[x] += 1
        else:
            errorCodeDict[x] = 1
    return errorCodeDict


def global_csv_columns(*dictionaries ):
    header_list = []
    for dictionary in dictionaries:
        for key in dictionary:
            header_list.append(key)
    return header_list

def __main__():
    parser = argparse.ArgumentParser(description='This script will parse and generate a summary of >= 1')
    parser.add_argument('-i', '--input', help='Input file name', required=False)

    args = parser.parse_args()

    ## show values ##
    print ("Input file/Directory is: %s" % args.input)
    process_path(args.input)


if __name__ == "__main__":
    __main__()
