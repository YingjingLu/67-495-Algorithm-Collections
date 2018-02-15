

class Dataset(object):
    pass

    def __init__(self, dataset_path):
        
        # each with a line of 
        # uplherc.upl.com - - [01/Aug/1995:00:00:43 -0400] "GET /shuttle/missions/sts-71/mission-sts-71.html HTTP/1.0" 200 13450
        self.dataset_path = dataset_path
        # attribute : index in seq
        self.attribute_index_dict = dict()
        # index : attribute reverse dict
        self.index_attribute_dict = dict()

        # [' ', '--', '##', '--[']
        self.separator_seq = []
        self.

    # utility functions
    def compress_to_