
from config import config

CONNECTED_CUTOFF = 0.2 #this is the permanence cutoff to be considered connected
PERMANENCE_INCREMENT = 0.04 #TODO: choose a reasonable number
PERMANENCE_DECREMENT = 0.04 #TODO: choose a reasonable number
MIN_THRESHOLD = config.getint('constants','min_synapses_per_segment_threshold')
SYNAPSES_PER_SEGMENT = config.getint('init', 'synapses_per_segment')

class Synapse(object):

    '''
    The simulation of a single synapse between dendrite and axon

    -contains a permanence value and the source of input index
    '''

    def __init__(self, _input, permanence = (CONNECTED_CUTOFF-.001)):

        # default synapse is not connected so set it lower than cutoff
        self.permanence = permanence
        self.input = _input

    @property
    def connected(self):
        return self.permanence >= CONNECTED_CUTOFF

    def was_firing(self, requiredConnection = True):

        '''
        - require if self.inout was firing in the property.

        @param requiredConnection: only return True if the synapse is connected
        if the false, then return true 
        '''

        return self.input.wasActive and (self.connected or (not requiredConnection))

    def is_firing(self, requiredConnection = True):
        '''
        - require if self.inout was firing in the property.

        @param requiredConnection: only return True if the synapse is connected
        if the false, then return true 
        '''

        return self.input.active and (self.connected or (not requiredConnection))

    def firing_at(self, timeDelta, requiredConnection = True):
        # if now that time is not error
        if timeDelta == 0:
            return self.is_firing(requiredConnection)
        # if time delta is in the past
        elif timeDelta == -1:
            return self.was_firing(requiredConnection)

        else:
            raise NotImplementedError

    def wasInputLearning(self):
        if not hasattr(input, learning):
            return False 

        else:
            return input.learning

    def permanence_increment(self, increment_by = PERMANENCE_INCREMENT):
        self.permanence = min(self.permanence + increment_by, 1.0)

    def permanence_decrement(self, decrement_by = PERMANENCE_DECREMENT):
        self.permanence = min(self.permanence + decrement_by, 0.0)

    def __str__(self):

        return return '{permanence:%.3f,connected:%s,was_firing:%s,is_firing:%s}' % (self.permanence, self.connected, self.was_firing(False), self.is_firing(False))

class SynapseState(object):
    
    def __init__(self, synapse, inputWasActive, segment):
        self.synapse = synapse 
        self.inputWasActive = inputWasActive 
        self.segment = segment 

    @classmethod
    def captureSegmentState(cls, segment, timeDelta):
        '''
        @param timeDelta: when capturing state, do you capture current or previous state?
            current = 0; previous = -1
        '''

        return map(lambda syn: cls(syn, syn.firing_at(timeDelta, requireConnection=False), segment), segment.synapses)

