from __future__ import print_function
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect
from session.participant import Participant
import csv
from desktopmagic.screengrab_win32 import (getDisplayRects,getRectAsImage)

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
activeUser = None

################################################
############### Routing Requests ###############
################################################

# Initial routing request
@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

# Request to render info.html
@app.route('/info')
def info():
    return render_template('info.html', async_mode=socketio.async_mode)

# Request to render demographics.html
@app.route('/demographics')
def demographics():
    return render_template('demographics.html', async_mode=socketio.async_mode)

# Request to render calibration.html
@app.route('/calibration')
def calibration():
    return render_template('calibration.html', async_mode=socketio.async_mode)

# Request to render instruction.html
@app.route('/instruction')
def instruction():
    return render_template('instruction.html', async_mode=socketio.async_mode)

# Request to render conditionInstruction.html
@app.route('/conditionInstruction')
def conditionInstruction():
    return render_template('conditionInstruction.html', async_mode=socketio.async_mode)

# Request to render startpoint.html
@app.route('/startpoint')
def startpoint():
    return render_template('startpoint.html', async_mode=socketio.async_mode)

# Request to render advertisement.html
@app.route('/advertisement')
def advertisement():
    return render_template('advertisement.html', async_mode=socketio.async_mode)

# Request to render confidence.html
@app.route('/confidence')
def confidence():
    return render_template('confidence.html', async_mode=socketio.async_mode)

# Request to render evaluation.html
@app.route('/evaluation')
def evaluation():
    return render_template('evaluation.html', async_mode=socketio.async_mode)

# Request to render postInterview.html
@app.route('/postInterview')
def postInterview():
    return render_template('postInterview.html', async_mode=socketio.async_mode)

# Request to render postInterview.html
@app.route('/preInterview')
def preInterview():
    return render_template('preInterview.html', async_mode=socketio.async_mode)


###############################################
############### Socket Messages ###############
###############################################

# Logs incoming messages
@socketio.on('message')
def test_message(message):
    app.logger.info('Incoming message: %s',message)

# Client request to start a new survey session
# New session will be created and confirmation send to client
@socketio.on('start')
def start_study(message):
    global activeUser
    activeUser = Participant(message['participantID'],message['budget'])
    app.logger.info('Participant %s has started a new session',message['participantID'])
    emit('start')

# Client request the demographics questionaire
# Send acknowledgement
@socketio.on('demographics')
def go_demographics():
    app.logger.info('Participant proceeds to demographics questionaire!')
    emit('demographics')

# Client request to proceed to calibration
# Send acknowledgement
@socketio.on('preInterview')
def go_preInterview(message):
    global activeUser
    app.logger.info('Participant proceeds to preInterview!')
    print("demographics completed")
    print(message)
    print(activeUser.participantID)
    with open('./log/demographics.csv', 'a') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow([str(activeUser.participantID),str(activeUser.budget),
                             str(message['gender']),str(message['age']),str(message['visionCorrection']),str(message['subject']),str(message['lastSearch']),str(message['futureSearch'])])
    emit('preInterview')

@socketio.on('calibration')
def go_calibration():
    app.logger.info('Participant proceeds to initial calibration!')
    emit('calibration')

# Client request to proceed to calibration
# Send acknowledgement
@socketio.on('instruction')
def go_instruction():
    global activeUser
    app.logger.info('Participant proceeds to instruction!')
    if(activeUser.condition == 'FAMILIARIZATION'):
        emit('instruction')
    else:
        emit('conditionInstruction')


# Client request to proceed with session
# Send acknowledgement
@socketio.on('startpoint')
def go_startpoint():
    app.logger.info('Participant proceeds to startpoint!')
    emit('startpoint')

# Automatic request to load new advertisement
# Send acknowledgement
@socketio.on('advertisement')
def go_advertisement():
    app.logger.info('Participant receives advertisement!')
    emit('advertisement')

#Site is requesting new dataset to show as advertisement
@socketio.on('adRequest')
def load_Page():
    global activeUser
    adID, dataset = activeUser.getNewDataSet()
    print(activeUser.participantID)
    print(activeUser.condition)
    print(adID)
    print(dataset)
    if activeUser.adaptationDecision2Votes is None or activeUser.adaptationDecision3Stages is None:
        emit('adRequest',{'id':adID,'data':dataset,'adaptation':'None', 'state':activeUser.condition})
    else:
        if activeUser.condition == 'COLORING':
            emit('adRequest', {'id': adID, 'data': dataset, 'adaptation': activeUser.adaptationDecision3Stages, 'state':activeUser.condition})
        elif activeUser.condition == 'FADING':
            emit('adRequest',{'id': adID, 'data': dataset, 'adaptation': activeUser.adaptationDecision2Votes, 'state': activeUser.condition})
        else:
            emit('adRequest', {'id': adID, 'data': dataset, 'adaptation': 'None', 'state':activeUser.condition})
    activeUser.startRecording()


# Client request to go to confidence questionnaire
# Send acknowledgement
@socketio.on('confidence')
def go_confidence():
    global activeUser
    print(activeUser.participantID)
    activeUser.stopRecording()
    app.logger.info('Participant proceeds to confidence questionnaire!')
    emit('confidence')

# Client submits confidence answers and system checks next steps
# Send acknowledgement and instruction to next step
@socketio.on('confidenceResponse')
def next_ad(message):
    global activeUser
    decision = str(message['decision'])
    confidence = str(message['confidence'])
    print(activeUser.lastAd)
    lastAd = str(activeUser.lastAd)
    adCounter = str(activeUser.adCounter)
    id = str(activeUser.participantID)
    state = str(activeUser.condition)
    dirName = './log/p' + str(id)
    with open(dirName + '/confidence.csv', 'a') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow([id,adCounter, lastAd, state, decision, confidence])
    activeUser.updateState()
    if(activeUser.condition == 'FAMILIARIZATION'):
        emit('startpoint')
    elif(activeUser.condition == 'TRAINING'):
        if (activeUser.adCounter == 4):
            emit('calibration')
        else:
            emit('startpoint')
    elif(activeUser.condition == 'DEFAULT'):
        if (activeUser.adCounter == 14 or activeUser.adCounter == 21 or activeUser.adCounter == 28):
            emit('calibration')
        else:
            emit('startpoint')
    elif(activeUser.condition == 'COLORING'):
        if (activeUser.adCounter == 14 or activeUser.adCounter == 21 or activeUser.adCounter == 28):
            emit('calibration')
        else:
            emit('startpoint')
    elif(activeUser.condition == 'FADING'):
        if (activeUser.adCounter == 14 or activeUser.adCounter == 21 or activeUser.adCounter == 28):
            emit('calibration')
        else:
            emit('startpoint')
    elif(activeUser.condition == 'DONE'):
        emit('evaluation')

# Client request to go to interview
# Send acknowledgement
@socketio.on('interview')
def go_interview(message):
    global activeUser
    with open('./log/evaluation.csv', 'a') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow([
            str(activeUser.participantID),
            str(message['horrible']),
            str(message['difficult']),
            str(message['frustrating']),
            str(message['reading']),
            str(message['coloring']),
            str(message['fading']),
            str(message['structure']),
            str(message['content']),
            str(message['terminology']),
            str(message['handling']),
            str(message['instruction']),
            str(message['defaultDensity']),
            str(message['coloringDensity']),
            str(message['fadingDensity']),
            str(message['understandable'])
        ])
    app.logger.info('Participant proceeds to interview!')
    emit('interview')

# Client received payment, study completed
# Send acknowledgement
@socketio.on('end')
def end_study():
    global activeUser
    activeUser = None
    app.logger.info('Participant has finished the user study!')
    emit('end')

# Client requests to take a screenshot
@socketio.on('screenshot')
def screenshot(message):
    adID = message['adID']
    for displayNumber, rect in enumerate(getDisplayRects(), 1):
        if displayNumber == 1:
            imDisplay = getRectAsImage(rect)
            imDisplay.save("./log/p" + str(activeUser.participantID) + "/screenshots/screenshot" + "_" + str(activeUser.adCounter) + "_" + str(activeUser.condition) + "_" + str(activeUser.lastAd)+"_display%d.png" % (displayNumber,), format='png')


if __name__ == '__main__':
    socketio.run(app, debug=True)
    # app.run()
