from __future__ import division
import pandas as pd
import numpy as np
import ctypes
import detectors

""""
Inputs dataset and list of all UI elements
Computes all metrics for each element
Returns updated version of elements
"""
def analyseDataset(elements,adCounter,dataset):
    elements = elements
    #Add new metric entry to metrics dictionairy of each element
    for elem in elements:
        elem.metrics[str(adCounter)] = {
        'timeToFirstFixation' : 0,
        'firstPassGazeDuration': 0,
        'secondPassGazeDuration': 0,
        'refixationsCount': 0,
        'sumOfFixations': 0,
        'overallDwellTime': 0,
    }

    #Loading new dataset
    gazeData = pd.read_csv(dataset)

    #Run validity check and filtering
    gazeData = filterUnvalidEntries(gazeData)
    gazeData = computeActualGazePoint(gazeData)
    gazeData = filterOffDisplayValues(gazeData)
    gazeData.reset_index()

    #If no gaze data returm elements
    if gazeData.empty or len(gazeData) == 1:
        return elements
    else:
        pass

    #Extract timestamps, coordinates and events
    timestamps = getTimestampsInMilliseconds(gazeData)
    x_gazePoints, width = getXGazePointsAsPixel(gazeData)
    y_gazePoints, height = getYGazePointsAsPixel(gazeData)
    x_gazePoints, y_gazePoints, timestamps = discardEdgeGazePoints(x_gazePoints,y_gazePoints,timestamps, elements)

    fixations = detectors.fixation_detection(x_gazePoints, y_gazePoints, timestamps)

    #If no fixation were detected return elements
    if len(fixations) == 0 or len(timestamps) == 0:
        return elements
    else:
        pass

    ##################################################
    ######## Start with metric computation ###########
    ##################################################

    #Time to first fixation -- Orientation
    #First pass gaze duration -- Orientation
    #Second pass gaze duration -- Evaluation
    #Refixations count -- Evaluation
    elements = computeTemporalFixationMetrices(fixations,elements,adCounter)

    #Sum of fixations -- Verification
    elements = computeSumOfFixations(fixations,elements, adCounter)

    #Overall Dwell Time -- Verification
    elements = computeDwellTime(x_gazePoints,y_gazePoints,timestamps,elements,adCounter)

    return elements


######### Helper methods to filter and process dataframe ###########

#Map points to elements
def mapToAOI(x,y,elements):
    for e in elements:
        if (x in np.arange(e.boundaries[0],e.boundaries[2]+1)):
            if (y in np.arange(e.boundaries[1],e.boundaries[3]+1)):
                return e.aoiCode
    return 'OFF'

#Get element from aoiCode
def getElementOfAOI(elements,aoi):
    for e in elements:
        if (aoi == e.aoiCode):
            return e


#Delete all unvalid gaze data
def filterUnvalidEntries(dataframe):
    validLeft = dataframe[dataframe['LeftGazePointValidity'] == 1]
    allValid = validLeft[validLeft['RightGazePointValidity'] == 1]
    return allValid


#Compute GazePoint from Left and Right Eye GazeData
def computeActualGazePoint(dataframe):
    actualGazePointX = []
    actualGazePointY = []

    for index, row in dataframe.iterrows():
        leftX = row['LeftGazePointX']
        leftY = row['LeftGazePointY']
        rightX = row['RightGazePointX']
        rightY = row['RightGazePointY']

        actualX = leftX+(rightX-leftX)/2
        actualY = leftY+(rightY-leftY)/2

        actualGazePointX.append(actualX)
        actualGazePointY.append(actualY)

    s = pd.Series(actualGazePointX)
    t = pd.Series(actualGazePointY)
    dataframe = dataframe.assign(ActualGazePointX=s.values)
    dataframe = dataframe.assign(ActualGazePointY=t.values)
    return dataframe

#Remove all off Display values
def filterOffDisplayValues(dataframe):

    inboundAll = dataframe[dataframe['ActualGazePointX'] <= 1]
    inboundAll = inboundAll[inboundAll['ActualGazePointX'] >= 0]

    inboundAll = inboundAll[inboundAll['ActualGazePointY'] <= 1]
    inboundAll = inboundAll[inboundAll['ActualGazePointY'] >= 0]

    return inboundAll

def  getTimestampsInMilliseconds(dataframe):
    time = dataframe.Timestamp
    time.reset_index(drop=True, inplace=True)
    t_temp = []
    initalTime = time[1]/1000
    for t in time[1:]:
        #print round(t/1000-initalTime)
        t_temp.append(t/1000-initalTime)
    return t_temp

def getXGazePointsAsPixel(dataframe):
    user32 = ctypes.windll.user32
    width = user32.GetSystemMetrics(0)
    x_temp = []
    actualX = dataframe['ActualGazePointX']
    for x in actualX[1:]:
        x_temp.append(round(x*width))
    return x_temp, width


def getYGazePointsAsPixel(dataframe):
    user32 = ctypes.windll.user32
    height = user32.GetSystemMetrics(1)
    y_temp = []
    actualY = dataframe['ActualGazePointY']
    for y in actualY[1:]:
        y_temp.append(round(y*height))
    return y_temp, height

def discardEdgeGazePoints(x_gazePoints, y_gazePoints, timestamp, elements):
    x_temp = []
    y_temp = []
    time_temp = []
    for i in range(0,len(x_gazePoints)):
        aoi = mapToAOI(x_gazePoints[i],y_gazePoints[i],elements)
        if aoi != 'OFF':
            x_temp.append(x_gazePoints[i])
            y_temp.append(y_gazePoints[i])
            time_temp.append(timestamp[i])
    return x_temp, y_temp, time_temp


######### Computation of single metrics ###########

#Compute temporal fixation metrices
#Inputs list of detected fixations and elements
#Computes Time to firs fixation, first- and second-pass-gaze as well as refixation count
def computeTemporalFixationMetrices(fixations,elements,adCounter):
    firstPass = 0
    secondPass = 0
    for i in np.arange(0, len(fixations)-1, 1):
        aoi_one = mapToAOI(fixations[i][3], fixations[i][4],elements)
        aoi_two = mapToAOI(fixations[i + 1][3], fixations[i + 1][4], elements)
        elem = getElementOfAOI(elements, aoi_one)
        if elem.metrics[str(adCounter)]['timeToFirstFixation'] == 0:
            elem.metrics[str(adCounter)]['timeToFirstFixation'] = fixations[i][0]
            firstPass = fixations[i][2]
        secondPass = secondPass + fixations[i][2]
        if aoi_one == aoi_two:
            firstPass = firstPass+fixations[i+1][2]
            secondPass = secondPass + fixations[i+1][2]
        else:
            if elem.metrics[str(adCounter)]['refixationsCount'] == 0:
                elem.metrics[str(adCounter)]['firstPassGazeDuration'] = firstPass
            elif elem.metrics[str(adCounter)]['refixationsCount'] == 1:
                elem.metrics[str(adCounter)]['secondPassGazeDuration'] = secondPass
            firstPass = 0
            secondPass = 0
            elem.metrics[str(adCounter)]['refixationsCount'] += 1
    aoi_last = mapToAOI(fixations[(len(fixations) - 1)][3], fixations[(len(fixations) - 1)][4], elements)
    elem = getElementOfAOI(elements, aoi_last)
    if firstPass != 0 or secondPass != 0:
        if elem.metrics[str(adCounter)]['refixationsCount'] == 0:
            elem.metrics[str(adCounter)]['firstPassGazeDuration'] = firstPass
        elif elem.metrics[str(adCounter)]['refixationsCount'] == 1:
            elem.metrics[str(adCounter)]['secondPassGazeDuration'] = secondPass
    elem.metrics[str(adCounter)]['refixationsCount'] += 1
    return elements

#Compute sum of fixations
def computeSumOfFixations(fixations,elements, adCounter):
    for fix in fixations:
        aoi_hit = mapToAOI(fix[3],fix[4],elements)
        elem = getElementOfAOI(elements,aoi_hit)
        elem.metrics[str(adCounter)]['sumOfFixations'] += 1
    return elements

#Compute overall Dwell Time
def computeDwellTime(x_gazePoints,y_gazePoints,timestamps,elements,adCounter):
    current = 0
    startT = 0
    lastT = 0
    for i in np.arange(1, len(timestamps), 1):
        x = x_gazePoints[i]
        y = y_gazePoints[i]
        t = timestamps[i]
        aoi = mapToAOI(x, y, elements)
        if current == 0:
            current = aoi
            startT = t
        elif aoi == current and i != len(timestamps) - 1:
            lastT = t
        else:
            try:
                d = lastT - startT  # add to aoi dwell time
                e = getElementOfAOI(elements, current)
                e.metrics[str(adCounter)]['overallDwellTime'] = e.metrics[str(adCounter)]['overallDwellTime'] + d
                current = aoi
                startT = t
                lastT = t
            except AttributeError:
                current = aoi
                print 'Error'
                print i
    return elements