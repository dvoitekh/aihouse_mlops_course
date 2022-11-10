import numpy as np

from fixtures import model, features


def test_model(model, features):
    predictions = model.predict(features)
    real_prices = np.exp(predictions)
    assert type(predictions) is np.ndarray
    assert np.all(real_prices > 0)
    assert real_prices[0] > real_prices[1]
