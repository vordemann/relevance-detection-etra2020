import tobii_research as tobii
import csv

filePath = None


#Find available eye tracker
def findEyeTracker():
    temp = tobii.find_all_eyetrackers()
    if (len(temp) == 0):
        return findEyeTracker()
    else:
        et = temp[0]
        return et


###### Action methods ########3

def startTracking(path):
    global eyeTracker
    global filePath
    filePath = path
    eyeTracker = findEyeTracker()
    with open(path + '.csv',  'a') as csvfile, open(path + '_FULL' + '.csv', "a") as full_csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        full_filewriter = csv.writer(full_csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        filewriter.writerow(['LeftGazePointX', 'LeftGazePointY','LeftGazePointValidity', 'RightGazePointX', 'RightGazePointY','RightGazePointValidity','Timestamp'])
        full_filewriter.writerow(
            ['RightPupilValidity', 'RightPupilDiameter', 'LeftPupilValidity', 'LeftPupilDiameter',
                'RightGazePointValidity', 'RightGazePointOnDisplayAreaX', 'RightGazePointOnDisplayAreaY',
                'RightGazePointInUserCoordinateSystemX', 'RightGazePointInUserCoordinateSystemY',
                'RightGazePointInUserCoordinateSystemZ', 'LeftGazePointValidity', 'LeftGazePointOnDisplayAreaX',
                'LeftGazePointOnDisplayAreaY', 'LeftGazePointInUserCoordinateSystemX',
                'LeftGazePointInUserCoordinateSystemY', 'LeftGazePointInUserCoordinateSystemZ',
                'RightGazeOriginValidity', 'RightGazeOriginInUserCoordinateSystemX',
                'RightGazeOriginInUserCoordinateSystemY', 'RightGazeOriginInUserCoordinateSystemZ',
                'RightGazeOriginInTrackboxCoordinateSystemX', 'RightGazeOriginInTrackboxCoordinateSystemY',
                'RightGazeOriginInTrackboxCoordinateSystemZ', 'LeftGazeOriginValidity',
                'LeftGazeOriginInUserCoordinateSystemX', 'LeftGazeOriginInUserCoordinateSystemY',
                'LeftGazeOriginInUserCoordinateSystemZ', 'LeftGazeOriginInTrackboxCoordinateSystemX',
                'LeftGazeOriginInTrackboxCoordinateSystemY', 'LeftGazeOriginInTrackboxCoordinateSystemZ',
                'SystemTimestamp', 'DeviceTimestamp'])
    eyeTracker.subscribe_to(tobii.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
    return eyeTracker

def stopTracking(eyeTracker):
    global filePath
    print("Eye Tracker:")
    print(eyeTracker)
    eyeTracker.unsubscribe_from(tobii.EYETRACKER_GAZE_DATA, gaze_data_callback)
    filePath = None

##### Callback function for eye tracker #####
def gaze_data_callback(gaze_data):
    global filePath
    with open(filePath +'.csv',  'a') as csvfile, open(filePath + '_FULL' + '.csv', "a") as full_csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        full_filewriter = csv.writer(full_csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow([gaze_data['left_gaze_point_on_display_area'][0],gaze_data['left_gaze_point_on_display_area'][1],gaze_data['left_gaze_point_validity'],gaze_data['right_gaze_point_on_display_area'][0],gaze_data['right_gaze_point_on_display_area'][1],gaze_data['right_gaze_point_validity'],gaze_data['device_time_stamp']])
        full_filewriter.writerow([gaze_data['right_pupil_validity'],gaze_data['right_pupil_diameter'],gaze_data['left_pupil_validity'],gaze_data['left_pupil_diameter'],gaze_data['right_gaze_point_validity'],gaze_data['right_gaze_point_on_display_area'][0],gaze_data['right_gaze_point_on_display_area'][1],gaze_data['right_gaze_point_in_user_coordinate_system'][0],gaze_data['right_gaze_point_in_user_coordinate_system'][1],gaze_data['right_gaze_point_in_user_coordinate_system'][2],gaze_data['left_gaze_point_validity'],gaze_data['left_gaze_point_on_display_area'][0],gaze_data['left_gaze_point_on_display_area'][1],gaze_data['left_gaze_point_in_user_coordinate_system'][0],gaze_data['left_gaze_point_in_user_coordinate_system'][1],gaze_data['left_gaze_point_in_user_coordinate_system'][2],gaze_data['right_gaze_origin_validity'],gaze_data['right_gaze_origin_in_user_coordinate_system'][0],gaze_data['right_gaze_origin_in_user_coordinate_system'][1],gaze_data['right_gaze_origin_in_user_coordinate_system'][2],gaze_data['right_gaze_origin_in_trackbox_coordinate_system'][0],gaze_data['right_gaze_origin_in_trackbox_coordinate_system'][1],gaze_data['right_gaze_origin_in_trackbox_coordinate_system'][2],gaze_data['left_gaze_origin_validity'],gaze_data['left_gaze_origin_in_user_coordinate_system'][0],gaze_data['left_gaze_origin_in_user_coordinate_system'][1],gaze_data['left_gaze_origin_in_user_coordinate_system'][2],gaze_data['left_gaze_origin_in_trackbox_coordinate_system'][0],gaze_data['left_gaze_origin_in_trackbox_coordinate_system'][1],gaze_data['left_gaze_origin_in_trackbox_coordinate_system'][2],gaze_data['system_time_stamp'],gaze_data['device_time_stamp']])

