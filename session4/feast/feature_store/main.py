import os
from feast import Entity, FeatureService, FeatureView, Field, FileSource, PushSource, ValueType
from feast.types import Float32, Int64


main_source = FileSource(
    path="s3://data/house_dataset_main.parquet",
    s3_endpoint_override=os.environ["INTERNAL_FEAST_S3_ENDPOINT_URL"],
    timestamp_field="EventTimestamp",
    created_timestamp_column="Created",
)

lat_lon_source = FileSource(
    path="s3://data/house_dataset_lat_lon.parquet",
    s3_endpoint_override=os.environ["INTERNAL_FEAST_S3_ENDPOINT_URL"],
    timestamp_field="EventTimestamp",
    created_timestamp_column="Created",
)

main_push_source = PushSource(
    name="main_push_source", batch_source=main_source,
)

house_id = Entity(name="HouseId", join_keys=["HouseId"], value_type=ValueType.INT64,)

house_main_view = FeatureView(
    name="house_main_view",
    entities=[house_id],
    schema=[
        Field(name="MedInc", dtype=Float32),
        Field(name="HouseAge", dtype=Float32),
        Field(name="AveRooms", dtype=Float32),
        Field(name="AveBedrms", dtype=Float32),
        Field(name="Population", dtype=Int64),
        Field(name="AveOccup", dtype=Float32),
        Field(name="MedHouseVal", dtype=Float32)
    ],
    online=True,
    source=main_push_source
)

house_lat_lon_view = FeatureView(
    name="house_lat_lon_view",
    entities=[house_id],
    schema=[
        Field(name="Latitude", dtype=Float32),
        Field(name="Longitude", dtype=Float32)
    ],
    online=True,
    source=lat_lon_source
)

service = FeatureService(
    name="house_service", features=[house_main_view, house_lat_lon_view]
)
