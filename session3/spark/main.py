from pyspark.sql import SparkSession
from pyspark.sql.types import *
import pyspark.sql.functions as f


def apply_config(spark):
    spark._jsc.hadoopConfiguration().set("fs.s3a.access.key", "minioadmin")
    spark._jsc.hadoopConfiguration().set("fs.s3a.secret.key", "minioadmin")
    spark._jsc.hadoopConfiguration().set("fs.s3a.endpoint", 'http://minio.default.svc:9000')
    spark._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
    spark._jsc.hadoopConfiguration().set("fs.s3a.connection.ssl.enabled", "false")
    spark._jsc.hadoopConfiguration().set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")


spark = SparkSession.builder.getOrCreate()
apply_config(spark)

main_df = spark.read.parquet('s3a://data/house_dataset_main.parquet')
lat_lon_df = spark.read.parquet('s3a://data/house_dataset_lat_lon.parquet')
main_df.head()
lat_lon_df.head()
