from element import Element
import numpy as np
import analyse
import relevance
import json
import random
import tracker
import csv
import os

STATE = {
        '1':'FAMILIARIZATION',
        '2':'TRAINING',
        '3':'DEFAULT',
        '4':'COLORING',
        '5':'FADING',
        '6':'DONE'
}
"""" 
    UI_GRID is a representation of the UI for which the gaze is tracked.
    This information is necessary for the computation of the single gaze metrics for each AOI.
    We assume that the UI consists of rectangular elements.
    Every AOI of the UI is comprised of the following: AOI code, x1, y1, x2, y2, where x1,y1 is the upper left boundary,
    and x2, y2 the lower left boundary.
    All coordinates are in percentage eg. 0.2 == 20% and are therefore independent of screen dimension.
    We have the following AOI codes for our room search scenario:
    TIT = Title
    PIC = Picture
    MPC = Map close
    MPO = Map overview
    FAC = Facts
    COS = Costs
    LOC = Location
    OBJ = Object
    ROM = Roommates
    SUR = Surrounding
    FCT = Facilities
    FSD = Flatshare Details  
    COM = Commute
"""

ROOMSEARCH_GRID = [
    ['TIT',0,0,0.69,0.07], ['PIC',0.69,0,1,0.34], ['MPC',0.69,0.34,1,0.67],
    ['MPO',0.69,0.67,1,1], ['FAC',0,0.07,0.23,0.38], ['COS',0.23,0.07,0.46,0.38],
    ['LOC',0.46,0.07,0.69,0.38], ['OBJ',0,0.38,0.23,0.69], ['ROM',0.23,0.38,0.46,0.69],
    ['SUR',0.46,0.38,0.69,0.69], ['FCT',0,0.69,0.23,1], ['FSD',0.23,0.69,0.46,1],
    ['COM',0.46,0.69,0.69,1]
]

FINANCIAL_GRID = [
    [1,0,0,0.25,0.3333], [2,0.25,0,0.5,0.3333], [3,0.5,0,0.75,0.3333],
    [4,0.75,0,1,0.3333], [5,0,0.3333,0.25,0.6666], [6,0.25,0.3333,0.5,0.6666],
    [7,0.5,0.3333,0.75,0.6666], [8,0.75,0.3333,1,0.6666], [9,0,0.6666,0.25,1],
    [10,0.25,0.6666,0.5,1], [11,0.5,0.6666,0.75,1], [12,0.75,0.6666,1,1]
]

class Participant:

    def __init__(self,id,budget):

        self.participantID = id
        self.budget = budget
        self.condition = STATE['1']
        self.remainingConditions = [STATE['3'],STATE['4'],STATE['5']]
        random.shuffle(self.remainingConditions)
        self.adCounter = 0
        self.elements = self.generateElements(ROOMSEARCH_GRID)
        self.data = self.generateData(budget)
        self.lastAd = None
        self.adaptationDecision2Votes = None
        self.adaptationDecision3Stages = None
        self.generateLogFiles()
        self.eyeTracker = None

    #Generate a dataset for a given budget
    def generateData(self,budget):
        results = {}
        blacklist = [0, 1, 3, 4, 6, 20, 24, 27, 30, 33, 34, 35, 37, 38, 41, 51, 56, 57, 58, 59, 60, 69, 70, 87, 91, 101,
                     110,
                     111, 114, 120, 121, 122, 124, 129, 130, 131, 132, 136, 138, 142, 143, 144, 145, 147, 158, 160, 161,
                     163,
                     165, 166, 171, 178, 180, 181, 186, 188, 195, 196, 198, 200, 204, 205, 212, 214, 215, 218, 219, 220,
                     221, 222, 223, 226, 228, 236, 244, 247, 249, 251, 254, 255, 264, 270, 272, 275, 291, 300, 310, 312,
                     322, 323, 324, 326, 330, 334, 338, 344, 350, 354, 355, 358, 361, 367, 368, 375, 385, 389, 392, 397,
                     405, 406, 413, 416, 428, 429, 436, 439, 441, 455, 457, 462, 464, 465, 481, 484, 489, 490, 500, 7,
                     9, 15,
                     20, 25, 27, 41, 44, 55, 67, 94, 95, 97, 121, 129, 135, 193, 203, 233, 250, 252, 285, 286, 290, 311,
                     327,
                     336, 345, 365, 368, 372, 388, 405, 411, 413, 424, 433, 461, 467, 471, 472, 477, 309, 376]

        with open('./static/attentionUI_studyData.json') as json_file:
            jsonFile = json.load(json_file)
            i = 0
            while i < 35:
                selection = random.choice(list(jsonFile))
                if int(jsonFile[selection]['cost']['overall_cost']) <= 1.1 * float(budget) and int(
                        selection) not in blacklist:
                    results[selection] = jsonFile[selection]
                    jsonFile.pop(selection)
                    i += 1
                else:
                    jsonFile.pop(selection)
            return results


    def generateElements(self,uiGrid):
        elements = []
        for entry in uiGrid:
            elements.append(Element(entry[0],entry[1],entry[2],entry[3],entry[4]))
        return elements

    def generateLogFiles(self):
        dirName = './log/p'+str(self.participantID)
        if not os.path.exists(dirName):
            os.mkdir(dirName)
            os.mkdir(dirName+"/gazeData")
            os.mkdir(dirName + "/screenshots")
        else:
            os.mkdir(dirName+'_ID_Collision')
            dirName = dirName+'_ID_Collision'

        with open(dirName+'/confidence.csv', 'a') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['ID','AdCount','AdId','State','Apply','Confidence'])

        with open(dirName+'/metrics.csv', 'a') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['ID','AdCount','AdId','State','AOI','TFF','FPG','SPG','RFX','SFX','ODT'])

        with open(dirName+'/calibration.csv', 'a') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['ID','State','Accuracy','Precision'])

        with open(dirName+'/preInterview.txt', 'a') as txtfile:
            txtfile.write("Pre-Study Interview mit Teilnehmer "+str(self.participantID)+":\n")
            txtfile.write("Beschreibe Sie bitte was Ihnen bei der Wohnungssuche wichtig ist?\n")

        with open(dirName+'/postInterview.txt', 'a') as txtfile:
            txtfile.write("Post-Study Interview mit Teilnehmer "+str(self.participantID)+":\n")
            txtfile.write("1. Welche Darstellung verwenden Sie am liebsten und warum?\n\n")
            txtfile.write("2. Was hat Ihnen an den verschiedenen Darstellungen gefallen?\n\n")
            txtfile.write("3. Was waren die groessten Herausforderungen in der Entscheidungsfindung bei den verschiedenen Darstellungsformen?\n\n")
            txtfile.write("4. Was waren die ausschlaggebenden Punkte fuer Ihre Entscheidungsfindung?\n\n")
            txtfile.write("5. Reflektieren Sie ob und wie sich Ihr Verhalten zwischen den unterschiedlichen Darstellungsformen veraendert hat?\n\n")
            txtfile.write("6. Wie realistisch waren die Zimmeranzeigen? Wurden alle fuer Ihre Entscheidung relevanten Informationen angezeigt\n\n")
            txtfile.write("7. Sonstiges?")
        #optional to-do is session logger file


########################################################
############## Actions of Participant ##################
########################################################

    #Return dataset and adaptation parameters
    def getNewDataSet(self):
        selection = random.choice(list(self.data))
        dataset = self.data[selection]
        self.lastAd = selection
        del self.data[selection]
        return selection,dataset

    #Start a new recording
    def startRecording(self):
        path = "./log/p"+str(self.participantID)+"/gazeData/gaze"+"_"+str(self.adCounter)+"_"+str(self.condition)+"_"+str(self.lastAd)
        self.eyeTracker = tracker.startTracking(path)

    #Stop ongoing recording
    def stopRecording(self):
        tracker.stopTracking(self.eyeTracker)
        self.eyeTracker = None

        path = "./log/p"+str(self.participantID)+"/gazeData/gaze"+"_"+str(self.adCounter)+"_"+str(self.condition)+"_"+str(self.lastAd)+".csv"
        self.elements = analyse.analyseDataset(self.elements,self.adCounter,path)
        dirName = './log/p'+str(self.participantID)
        with open(dirName+'/metrics.csv', 'a') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for elem in self.elements:
                row = []
                row.append(str(self.participantID))
                row.append(str(self.adCounter))
                row.append(str(self.lastAd))
                row.append(str(self.condition))
                row.append(str(elem.aoiCode))
                row.append(str(elem.metrics[str(self.adCounter)]['timeToFirstFixation']))
                row.append(str(elem.metrics[str(self.adCounter)]['firstPassGazeDuration']))
                row.append(str(elem.metrics[str(self.adCounter)]['secondPassGazeDuration']))
                row.append(str(elem.metrics[str(self.adCounter)]['refixationsCount']))
                row.append(str(elem.metrics[str(self.adCounter)]['sumOfFixations']))
                row.append(str(elem.metrics[str(self.adCounter)]['overallDwellTime']))
                filewriter.writerow(row)


    def runOptimization(self):
        decision2Votes, decision3Stages, VotingResults, votes, zscores = relevance.computeRelevance(self.elements,np.arange(4,14),self.participantID)
        self.adaptationDecision2Votes = decision2Votes
        self.adaptationDecision3Stages = decision3Stages
        with open('./log/relevance.csv', 'a') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for i in np.arange(0,len(votes)):
                filewriter.writerow(votes[i])
                filewriter.writerow(zscores[i])

    def updateState(self):
        self.adCounter = self.adCounter + 1
        if self.adCounter == 4:
            self.condition = STATE['2']
        if self.adCounter == 14:
            self.condition = self.remainingConditions.pop()
            self.runOptimization()
        if self.adCounter == 21:
            self.condition = self.remainingConditions.pop()
        if self.adCounter == 28:
            self.condition = self.remainingConditions.pop()
        if self.adCounter == 35:
            self.condition = STATE['6']