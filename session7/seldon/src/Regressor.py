

import os
import logging
import numpy as np

from joblib import load


class Regressor(object):
    def __init__(self):
        self.model = load(os.environ['MODEL_PATH'])

    def predict(self, X, features_names):
        logging.info(X, features_names)
        y_log = self.model.predict(X)
        return np.exp(y_log)

    def metrics(self):
        print("metrics called")
        return [
            # a counter which will increase by the given value
            {"type": "COUNTER", "key": "mycounter", "value": 1},

            # a gauge which will be set to given value
            {"type": "GAUGE", "key": "mygauge", "value": 100},

            # a timer (in msecs) which  will be aggregated into HISTOGRAM
            {"type": "TIMER", "key": "mytimer", "value": 20.2},
        ]
