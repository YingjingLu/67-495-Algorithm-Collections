
from htm.config import Config as config
from htm.segment import segment
from htm.synapse import MIN_THRESHOLD, SYNAPSES_PER_SEGMENT
import random

SEGMENTS_PER_CELL = getint('init', 'segment_per_cell')

class Cell(object):

    def __init__(self, column = None, layer = None):
        '''
        @param layer the inner layer of the cell, so an HTM with 3 cells per column
            would have cells with layers 0, 1 and 2
        '''

        self.column = column
        self.layer = layer

        self.active = False
        self._wasActive = False
        self.predicting = False
        self._predicted = False
        self.learning = False
        self._wasLearning = False
        self.predictingNext = False
        self._predictedNext = False

        self.segments = [Segments for i in range(SEGMENTS_PER_CELL)]

    @property 
    def wasActive(self):
        return self._wasActive

    @property
    def wasLearning(self):
        return self._wasLearning

    @property
    def predicted(self):
        return self.__predicted
    
    @property
    def predictedNext(self):
        return self.__predictedNext
    
    @property
    def segmentsNear(self):
        return self.__segmentsFilterNextStep(True)
    
    @property
    def segmentsFar(self):
        return self.__segmentsFilterNextStep(False)

    @property
    def predictingNext(self):

        if self._predictingNext is not None:
            return self._predictingNext

        cache = False
        for segment in self.segmentsNear:
            if segment.active:
                cache = True
                break

        self._predictingNext = cache
        return self._predictingNext

    @predictingNext.setter
    def predictingNext(self, value):
        self._predictingNext = value

    def _segmentsFilterNextStep(self, nextStep):
        return filter(lambda seg: seg.nextStep == nextStep, self.segments)

    def clockTick(self):
        self._predicted = self.predicting
        self.__wasActive = self.active
        self.__wasLearning = self.learning
        self.__predictedNext = self.predictingNext

        self.predicting = False
        self.predictingNext = None
        self.active = False
        self.learning = False

    def active_segments(self, input):
        'prefer distal/sequence over proximal/input, if available'
        pass

    def create_segment(self, htm, nextStep):
        '''
        @param htm: the htm network that contains the cell
        @param nextStep: boolean for whether this segment indicates predicted 
            firing in the very next time step 
        '''

        seg = Segment(nextStep = nextStep)

        # randomly choose input cells, from active non-self cells
        synapseLen = self._createSynapses(seg, htm.cells, SYNAPSES_PER_SEGMENT, lambda c: c.wasLearning)

        lif not nextStep and synapseLen < SYNAPSES_PER_SEGMENT:
        addSynapseLen = SYNAPSES_PER_SEGMENT - synapseLen
        activeSynapseLen = self._createSynapses(seg, htm.cells, addSynapseLen, lmbda c: c.wasActive)

        self.segments.append(seg)

        return seg 

    def _createSynapses(self, segment, cells, maxSynapses, filterFunc):
        if filterFunc is None:
            filterFunc = lambda cell: True

        alsoFilterSelf = lambda cell: fulterFunc(cell) and self != cell 

        matchingCells = filter(alsoFilterSelf, cells)
        sampleSize = min(len(matchingCells), maxSynapses)
        synapsesFrom = random.sample(matchingCells, sampleSize)

        for cell in synapseFrom:
            segment.create_synapse(cell)

        return len(synapseFrom)

    def __hash__(self):
        return self.layer * hash(self.column)

    def __eq__(self, other):
        if not hasattr(other, 'column') or not hasattr(other, 'layer'):
            return False

        return self.layer == other.layer and self.column == other.column 

    def __ne__(self, other):
        return not(self == other)

    def findSegmentWasActive(self, nextStep = True):
        'prefer distal, return hits from segments connected to other cells'

        if nextStep:
            segments = self.segmentsNear
        else:
            segments = self.segments 

        for seg in segments:
            if seg.wasActive:
                return seg 

    def bestMatchingSegment(self, nextStep):
        '''
        For this cell, find the segment with the largest number of 
        previously active synapses. This routine is aggressive in finding the best 
        match. The permanence value of synapses is allowed to be below 
        connectedPerm. The number of active synapses is allowed to be below 
        activationThreshold, but must be at or above minThreshold. The routine 
        returns the segment index. If no segments are found, then None is 
        returned. 
        @param nextStep: should the segment be of the nextStep type, or all-time prediction?
        '''
        bestSegment = None
        bestSegmentSynapseCount = MIN_THRESHOLD - 1
        for seg in filter(lambda seg: seg.nextStep == nextStep, self.segments):
            synapseCount = len(seg.old_firing_synapses(requireConnection = False))
            if synapseCount > bestSegmentSynapseCount:
                bestSegmentSynapseCount = synapseCount 
                bestSegment = seg 
        return bestSegment 

    def __str__(self):
        base = "cell layer %s in column(%s,%s) (active,predicting,learning) = now(%s,%s,%s) last(%s,%s,%s)" % (
            self.layer, self.column.x, self.column.y, self.active, self.predicting, self.learning, self.wasActive, 
            self.predicted, self.wasLearning)
        
        segText = [base]
        for seg in self.segments:
            segText.append(str(seg))
            
        return '\n\t'.join(segText)
