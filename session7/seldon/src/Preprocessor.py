import feast
import logging
import os

from joblib import load


class Preprocessor(object):
    def __init__(self):
        self.feature_store = feast.FeatureStore(
            repo_path=os.environ['FEATURE_STORE_PATH']
        )
        self.scaler = load(os.environ['PREPROCESSSING_PATH'])

    def class_names(self):
        return [
            "house_main_view:HouseId",
            "house_main_view:MedInc",
            "house_main_view:HouseAge",
            "house_main_view:AveRooms",
            "house_main_view:AveBedrms",
            "house_main_view:Population",
            "house_main_view:AveOccup",
            "house_lat_lon_view:Latitude",
            "house_lat_lon_view:Longitude"
        ]

    def health_status(self):
        return []

    def predict(self, X, features_names):
        online_features = self.feature_store.get_online_features(
            features=self.class_names()[1:],
            entity_rows=[
                {"HouseId": x[0]} for x in X
            ]
        ).to_df()[[x.split(':')[-1] for x in self.class_names()]]
        features = self.scaler.transform(online_features)
        logging.info(features)
        return features
