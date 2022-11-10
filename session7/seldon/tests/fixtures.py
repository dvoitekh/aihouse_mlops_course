import os
import pytest

from joblib import load

from src.Regressor import Regressor


@pytest.fixture(scope='session')
def regressor():
    os.environ['MODEL_PATH'] = 'checkpoints/model.joblib'
    return Regressor()


@pytest.fixture(scope='session')
def model():
    return load('checkpoints/model.joblib')


@pytest.fixture(scope='session')
def features():
    return [[-1.7319668924113674,-0.7324396877792114,-0.3686446776412593,-0.7979812453599388,0.07906991444149086,0.7289808981819601,0.08193376858427932,-0.6797418814172994,0.5938194097272528],
            [-1.7312955548882658,-1.3334053246300217,-0.8453931491070594,-0.34815492500568834,-0.019726266386578314,1.1316531272558914,-0.018082498363888314,1.6377819950507821,-0.9834354838678211]]
