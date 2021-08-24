import analyse
import ctypes

class Element:

    def __init__(self,aoiCode,x1,y1,x2,y2):
        self.aoiCode = aoiCode
        self.boundaries = self.convertToBoundaries(x1,y1,x2,y2)
        self.metrics = {}

    def convertToBoundaries(self,x1,y1,x2,y2):
        b = []
        user32 = ctypes.windll.user32
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)

        #Get dimensions of container
        #Double check if padding is equal to --whole-ui-paddingv value in style.css
        padding = 60
        containerWidth = width - 2*padding
        containerHeight = height - 2*padding

        #Compute boundary values
        b.append(round(x1 * containerWidth)+padding)
        b.append(round(y1 * containerHeight)+padding)
        b.append(round(x2 * containerWidth)+padding)
        b.append(round(y2 * containerHeight)+padding)
        return b