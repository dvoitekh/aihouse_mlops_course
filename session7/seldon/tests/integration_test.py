import grpc
from os import getenv

import requests
from jsonschema import validate
from seldon_core.proto import prediction_pb2, prediction_pb2_grpc
from google.protobuf import struct_pb2

TEST_API_HOST = getenv('TEST_API_HOST', 'localhost')
PAYLOAD = [1,1,1,1,1,1,1,1,1]


def test_api_grpc():
    channel = grpc.insecure_channel(f"{TEST_API_HOST}:5005")
    stub = prediction_pb2_grpc.ModelStub(channel)

    batch = struct_pb2.ListValue()
    batch.append(PAYLOAD)
    data = prediction_pb2.DefaultData(ndarray=batch)
    seldon_request = prediction_pb2.SeldonMessage(data=data)
    response = stub.Predict(seldon_request)
    assert len(response.data.ndarray.values) == 1
    assert isinstance(response.data.ndarray.values[0], struct_pb2.Value)


def test_api_rest():
    schema = {
        'type': 'object',
        'properties': {
            'data': {
                'type': 'object',
                'properties': {
                    'names': {
                        'type': 'array'
                    },
                    'ndarray': {
                        'type': 'array',
                    }
                }
            }
        }
    }

    response = requests.post(
        f'http://{TEST_API_HOST}:9005/api/v1.0/predictions',
        headers={'Content-type': 'application/json'},
        json={
            'data': {
                'ndarray': [
                    PAYLOAD
                ]
            }
        }
    )

    response_dict = response.json()

    assert validate(instance=response_dict, schema=schema) is None
