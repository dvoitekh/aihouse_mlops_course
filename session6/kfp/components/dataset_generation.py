from kfp.components import OutputPath


def dataset_generation(validation_dataset_fraction: float, random_seed: int,
                       train_dataset_path: OutputPath('Dataset'),
                       val_dataset_path: OutputPath('Dataset')):
    import pandas as pd
    import feast

    store = feast.FeatureStore("feature_store")

    entity_df = pd.DataFrame.from_dict({"HouseId": [i for i in range(1, 20641)]})
    entity_df["event_timestamp"] = pd.to_datetime("now", utc=True)

    retrieval_job = store.get_historical_features(
        entity_df=entity_df,
        features=[
            "house_main_view:MedInc",
            "house_main_view:HouseAge",
            "house_main_view:AveRooms",
            "house_main_view:AveBedrms",
            "house_main_view:Population",
            "house_main_view:AveOccup",
            "house_main_view:MedHouseVal",
            "house_lat_lon_view:Latitude",
            "house_lat_lon_view:Longitude",
        ],
    )
    df = retrieval_job.to_df().drop(columns=["event_timestamp"])

    val_df = df.sample(frac=validation_dataset_fraction, random_state=random_seed)
    train_df = df[~df.index.isin(val_df.index)]

    train_df.to_csv(train_dataset_path, index=False)
    val_df.to_csv(val_dataset_path, index=False)
    print(f"Train size: {len(train_df)}, Validation size: {len(val_df)}")
