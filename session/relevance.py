import numpy as np
"""
The relevance of an AOI is computed by normalizing the metrics
with the corresponding average ov
"""
def computeRelevance(elements,range,id):
    results = {}

    for elem in elements:
        results[elem.aoiCode] = {
        'timeToFirstFixation': [],
        'firstPassGazeDuration': [],
        'secondPassGazeDuration': [],
        'refixationsCount': [],
        'sumOfFixations': [],
        'overallDwellTime': [],
    }

    #Compute z score of each metric for each recording
    for i in range:
        aveTFF,stdTFF,aveFPG,stdFPG,aveSPG,stdSPG,aveRFX,stdRFX,aveSFX,stdSFX,aveODT,stdODT = averageMetric(i,elements)
        for elem in elements:
            results[elem.aoiCode]['timeToFirstFixation'].append(np.divide((elem.metrics[str(i)]['timeToFirstFixation']-aveTFF),stdTFF))
            results[elem.aoiCode]['firstPassGazeDuration'].append(np.divide((elem.metrics[str(i)]['firstPassGazeDuration']-aveFPG),stdFPG))
            results[elem.aoiCode]['secondPassGazeDuration'].append(np.divide((elem.metrics[str(i)]['secondPassGazeDuration']-aveSPG),stdSPG))
            results[elem.aoiCode]['refixationsCount'].append(np.divide((elem.metrics[str(i)]['refixationsCount']-aveRFX),stdRFX))
            results[elem.aoiCode]['sumOfFixations'].append(np.divide((elem.metrics[str(i)]['sumOfFixations']-aveSFX),stdSFX))
            results[elem.aoiCode]['overallDwellTime'].append(np.divide((elem.metrics[str(i)]['overallDwellTime']-aveODT),stdODT))

    zscores = []
    votes = []
    adaptationDecision2Votes = {}
    adaptationDecision3Stages = {}

    #Check if metric z score is above average over all recordings
    for key,value in results.items():
        #For TFF we are looking for values below the average
        entryZscores = []
        entryVotes = []
        entryZscores.append(str(id))
        entryVotes.append(str(id))
        entryZscores.append(str(key))
        entryVotes.append(str(key))
        entryZscores.append('zscore')
        entryVotes.append('votes')

        entryZscores.append(str(np.average(value['timeToFirstFixation'])))
        if np.average(value['timeToFirstFixation']) > 0:
            results[key]['timeToFirstFixation'] = 0
            entryVotes.append('0')
            # print("AOI "+str(key)+" - TFF: "+ str(np.average(value['timeToFirstFixation'])))
        else:
            results[key]['timeToFirstFixation'] = 1
            entryVotes.append('1')
            # print("AOI "+str(key)+" - TFF: "+ str(np.average(value['timeToFirstFixation'])))

        entryZscores.append(str(np.average(value['firstPassGazeDuration'])))
        if np.average(value['firstPassGazeDuration']) > 0:
            results[key]['firstPassGazeDuration'] = 1
            entryVotes.append('1')
            # print("AOI "+str(key)+" - FPG: "+ str(np.average(value['firstPassGazeDuration'])))
        else:
            results[key]['firstPassGazeDuration'] = 0
            entryVotes.append('0')
            # print("AOI "+str(key)+" - FPG: "+ str(np.average(value['firstPassGazeDuration'])))

        entryZscores.append(str(np.average(value['secondPassGazeDuration'])))
        if np.average(value['secondPassGazeDuration']) > 0:
            results[key]['secondPassGazeDuration'] = 1
            entryVotes.append('1')
            # print("AOI "+str(key)+" - SPG: "+ str(np.average(value['secondPassGazeDuration'])))
        else:
            results[key]['secondPassGazeDuration'] = 0
            entryVotes.append('0')
            # print("AOI "+str(key)+" - SPG: "+ str(np.average(value['secondPassGazeDuration'])))

        entryZscores.append(str(np.average(value['refixationsCount'])))
        if np.average(value['refixationsCount']) > 0:
            results[key]['refixationsCount'] = 1
            entryVotes.append('1')
            # print("AOI "+str(key)+" - RFX: "+ str(np.average(value['refixationsCount'])))
        else:
            results[key]['refixationsCount'] = 0
            entryVotes.append('0')
            # print("AOI "+str(key)+" - RFX: "+ str(np.average(value['refixationsCount'])))

        entryZscores.append(str(np.average(value['sumOfFixations'])))
        if np.average(value['sumOfFixations']) > 0:
            results[key]['sumOfFixations'] = 1
            entryVotes.append('1')
            # print("AOI "+str(key)+" - SFX: "+ str(np.average(value['sumOfFixations'])))
        else:
            results[key]['sumOfFixations'] = 0
            entryVotes.append('0')
            # print("AOI "+str(key)+" - SFX: "+ str(np.average(value['sumOfFixations'])))

        entryZscores.append(str(np.average(value['overallDwellTime'])))
        if np.average(value['overallDwellTime']) > 0:
            results[key]['overallDwellTime'] = 1
            entryVotes.append('1')
            # print("AOI "+str(key)+" - ODT: "+ str(np.average(value['overallDwellTime'])))
        else:
            results[key]['overallDwellTime'] = 0
            entryVotes.append('0')
            # print("AOI "+str(key)+" - ODT: "+ str(np.average(value['overallDwellTime'])))

        voteCount = countVotes(key,results)
        ad2Votes, ad3Stages = checkConstraints(key,results,voteCount)

        adaptationDecision2Votes[key] = ad2Votes
        adaptationDecision3Stages[key] = ad3Stages

        entryZscores.append(str(ad2Votes))
        entryZscores.append(str(ad3Stages))
        entryVotes.append(str(ad2Votes))
        entryVotes.append(str(ad3Stages))

        zscores.append(entryZscores)
        votes.append(entryVotes)

    return adaptationDecision2Votes, adaptationDecision3Stages, results, votes, zscores

def averageMetric(counter,elements):
    aveTFF = []
    aveFPG = []
    aveSPG = []
    aveRFX = []
    aveSFX = []
    aveODT = []
    for elem in elements:
        aveTFF.append(elem.metrics[str(counter)]['timeToFirstFixation'])
        aveFPG.append(elem.metrics[str(counter)]['firstPassGazeDuration'])
        aveSPG.append(elem.metrics[str(counter)]['secondPassGazeDuration'])
        aveRFX.append(elem.metrics[str(counter)]['refixationsCount'])
        aveSFX.append(elem.metrics[str(counter)]['sumOfFixations'])
        aveODT.append(elem.metrics[str(counter)]['overallDwellTime'])
    return np.average(aveTFF),np.std(aveTFF),np.average(aveFPG),np.std(aveFPG),np.average(aveSPG),np.std(aveSPG),np.average(aveRFX),np.std(aveRFX),np.average(aveSFX),np.std(aveSFX),np.average(aveODT),np.std(aveODT)

def countVotes(key,results):
    votes = 0
    for metric,value in results[key].items():
        if value == 1:
            votes = votes + 1
    return votes

def checkConstraints(key, results, votes):

    #AOI needs a minimum of two votes to be relevant
    if votes >= 2:
        adaptationDecision2votes = 1
    else:
        adaptationDecision2votes = 0

    #AOI needs at least a vote from each stages to be relevant
    if votes <= 2:
        adaptationDecision3stages = 0
    else:
        #At least one vote of Stage 1 - Orientation
        if results[key]['timeToFirstFixation'] == 1 or results[key]['firstPassGazeDuration'] == 1:
            # At least one vote of Stage 2 - Evaluation
            if results[key]['secondPassGazeDuration'] == 1 or results[key]['refixationsCount'] == 1:
                # At least one vote of Stage 3 - Verification
                if results[key]['sumOfFixations'] == 1 or results[key]['overallDwellTime'] == 1:
                    adaptationDecision3stages = 1
                else:
                    adaptationDecision3stages = 0
            else:
                adaptationDecision3stages = 0
        else:
            adaptationDecision3stages = 0

    return str(adaptationDecision2votes), str(adaptationDecision3stages)