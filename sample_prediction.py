import csv
import datetime
import logging

from pkg_resources import resource_filename

from nupic.frameworks.opf.model_factory import ModelFactory

DEFAULT_INPUT_PATH = 'input_data/default_input.csv'
DEFAULT_OUTPUT_PATH = 'output_data/default_output.csv'


class BaseModel(object):


    def __init__(self,
                 model_params,
                 load_batch_size = 0,
                 input_path = None,
                 output_path = None,):
        self._model = None
        self._model_params = model_params
        self._file_type = 'csv'
        self._input_path = input_path 
        self._output_path = output_path
        self._load_batch_size = load_batch_size
        self._cur_batch_remaining = load_batch_size
        self._batch = []

        self.anomaly_threshold = 0.9
        self._input_min = input_min
        self._input_max = input_max
        self._encoder_type = "RandomDistributedScalarEncoder"
        self._min_resolution = 0.001 

        self._input_path = input_path 
        self._output_path = output_path

    def get_input_method

    def _setRandomEncoderResolution(self, minResolution=0.001):
        """
        Given model params, figure out the correct resolution for the
        RandomDistributed encoder. Modifies params in place.
        """
        encoder = (
          self._model_params["modelParams"]["sensorParams"]["encoders"]["value"]
        )

        if encoder["type"] == "RandomDistributedScalarEncoder":
            rangePadding = abs(self._input_max - self._input_min) * 0.2
            minValue = self._input_min - rangePadding
            maxValue = self._input_max + rangePadding
            resolution = max(minResolution,
                             (maxValue - minValue) / encoder.pop("numBuckets")
                            )
            encoder["resolution"] = resolution

    def createModel(self):
        self._setRandomEncoderResolution()
        self._model = ModelFactory.create(self._model_params)

        print("BaseModel successfully created")


    def output_data(self, data_dict):
        if self._load_batch_size == 0:
            return [data_dict]
        else:
            self._batch.append(data_dict)
            self._cur_batch_remaining -= 1
            if self._cur_batch_remaining == 0:
                self._cur_batch_remaining = self._load_batch_size
                temp = self._batch
                self._batch = []
                return temp




    def load_historic_with_model(self):

        if self._input_path != None:
            if self._file_type == csv:
                with open (self._input_path) as fin:
                    reader = csv.reader(fin)
                    headers = reader.next()
                    for (i, record) in enumerate(reader, start = 1):
                        modelInput = dict(zip(headers, record))
                        modelInput['value'] = float(modelInput['value'])
                        modelInput['timestamp'] = datetime.datetime.strptime(
          modelInput["timestamp"], "%Y-%m-%d %H:%M:%S")

                    result = model.run(modelInput)
                    anomalyScore = result.inferences['anomalyScore']
                    modelInput['anomaly_score'] = anomalyScore
                    if 



    # return data_dict: {attr1:, attr2:, anomaly = [] / [attr1, attr2.....], anomaly_score = }
    def run_base_model(self):
        self.createModel()
        assert(self._model != None)
        self._model.enableInference({'predictedField': 'value'})









