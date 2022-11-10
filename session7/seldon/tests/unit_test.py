import os
import numpy as np

from fixtures import regressor, features


def test_regressor_batch(regressor, features):
    predictions = regressor.predict(features, None)
    assert type(predictions) is np.ndarray
    assert len(predictions) == len(features)
    assert isinstance(predictions[0], float)


def test_regressor_single(regressor, features):
    predictions = regressor.predict(features[:1], None)
    assert type(predictions) is np.ndarray
    assert len(predictions) == 1
    assert isinstance(predictions[0], float)
