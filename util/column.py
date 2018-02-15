
from htm.cell import Cell 
from htm.synapse import Synapse 
from htm.config import Config as Config 
from htm.segment import Segment 
import math 

#using an exponential average, so AS*old+(1-AS*current) => new
AVG_SCALE = 0.995
BOOST_RATE = 1

class Column(object):

    MIN_OVERLAP = 5

    def __init__(self, htm, x, y, cellsPerColumn):

        self.htm = htm 
        self.cells = [Cell(self, i) for i in range(cellsPerColumn)]
        self.overlap = 0

        self.segment = Segment(distal = False)
        self.boost = 1 
        self.x = x 
        self.y = y
        self.dutyCycleMin = 0
        self.dutyCycleActive = 0
        self.dutyCycleOverlap = 0
        self.active = False

    def old_firing_synapses(self):
        return self.segment.old_firing_synapses()

    def increase_permanences(self, byAmount):
        return self.segment.increase_permanences(byAmount)

    def get_duty_cycle_active(self):
        newDutyCycle = AVG_SCALE * self.dutyCycleActive
        if self.active:
            newDutyCycle += (1 - AVG_SCALE)

        return newDutyCycle

    def get_duty_cycle_overlap(self):
        newDutyCycle = AVG_SCALE * self.dutyCycleOverlap
        if self.overlap > self.MIN_OVERLAP:
            newDutyCycle += (1 - AVG_SCALE)
        return newDutyCycle

    def next_boost(self):
        if self.dutyCycleActive >= self.dutyCycleMin:
            return 1
        elif self.dutyCycleActive == 0:
            return self.boost * 1.05

        else:
            return self.dutyCycleMin / self.dutyCycleActive 

    @property
    def synapses(self):
        return self.segment.synapses 

    @property 
    def synapsesConnected(self):
        return self.segment.synapsesConnected()

    @property
    def neighbors(self):
        return self.htm.neighbors(self)

    def bestCell(self, nextStep = True):
        'htm doc 0.2 p 45 get best batchingcell'

        bestCell = None
        bestCellFiringSynapseCount = 0
        bestSeg = None

        # find cell best matching segment 
        for cell in self.cells:
            seg = cell.bestMatchingSegment(nextStep)
            numSynapses = len(seg.old_firing_synapses(requiredConnection = False)) if seg else 0

            if numSynapses > bestCellFiringSynapseCount:
                bestCellFiringSynapseCount = numSynapses
                bestCell = cell 
                bestSeg = seg 

        if bestCell is None:
            bestSeg = None
            fewSegments = len(self.cells[0].segments)
            bestCell = self.cells[0]
            for cell in self.cells[1:]:
                if len(cell.segments) < fewestSegments:
                    bestCell = cell 
                    fewestSegments = len(cell.segments)

            bestSeg = cell.bestMatchingSegment(nextStep) 

        return (bestCell, bestSeg)

    def distance_to(self, x, y):
        #map column's x,y values to input space:
        inputx = self.htm.inputCompression * self.x
        inputy = self.htm.inputCompression * self.y

        #assume 2d distances for now
        return math.sqrt((x-inputx)**2 + (y-inputy)**2)

     def __str__(self):
        #TODO: much more
        return "pos %s,%s; active? %s\n\t%s" % (self.x, self.y, self.active, self.segment)

    def neighbor_duty_cycle_max(self):
        '''
        (Adapted from maxDutyCycle)
        Numenta docs: Returns the maximum active duty cycle of the columns in the 
        neighborhood  
        '''
        return max((c.dutyCycleActive for c in self.neighbors))

    def kth_neighbor(self, k):
        '''
        
        Numenta docs: Given the list of columns, return the kth highest overlap value
        '''
        allNeighbors = sorted(self.neighbors, reverse=True, key=lambda col: col.overlap)
        index = min(k-1,len(allNeighbors)-1)
        return allNeighbors[index]

    @property
    def predicting(self):
        for cell in self.cells:
            if cell.predicting:
                return True
        return False
    
    @property
    def predictedNext(self):
        'is this column expected to get excited next?'
        for cell in self.cells:
            if cell.predictedNext:
                return True
        return False
    
    def __hash__(self):
        return self.x * self.y * hash(self.htm)
    
    def __eq__(self, another):
        if not hasattr(another, 'htm') or not hasattr(another, 'x') or \
            not hasattr(another, 'y') or not hasattr(another, 'boost'):
            return False
        return self.htm == another.htm and self.x == another.x and self.y == another.y