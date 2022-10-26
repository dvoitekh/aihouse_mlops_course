from pyspark.sql import SparkSession
from pyspark.sql.types import *
import pyspark.sql.functions as f


def apply_config(spark):
    spark._jsc.hadoopConfiguration().set("fs.s3a.access.key", "minioadmin")
    spark._jsc.hadoopConfiguration().set("fs.s3a.secret.key", "minioadmin")
    spark._jsc.hadoopConfiguration().set("fs.s3a.endpoint", 'http://helm-minio.default.svc:9000')
    spark._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
    spark._jsc.hadoopConfiguration().set("fs.s3a.connection.ssl.enabled", "false")
    spark._jsc.hadoopConfiguration().set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")


spark = SparkSession.builder.getOrCreate()
apply_config(spark)

# read files. '*' can be used for broadcasting
main_df = spark.read.parquet('s3a://data/house_dataset_main.parquet')
lat_lon_df = spark.read.parquet('s3a://data/house_dataset_lat_lon.parquet')
print(main_df.count())

# print dataframes
main_df.show()
lat_lon_df.show()

# select specific columns
lat_lon_df = lat_lon_df.select(f.col('HouseId'), f.col('Latitude'), f.col('Longitude'))
lat_lon_df.show()

# add new columns
main_df.withColumn('is_old_house', f.col('HouseAge') > 10.0).show()

# count records
print(main_df.count())

# join dataframes
joined_df = main_df.join(lat_lon_df, on="HouseId", how="left")
joined_df.show()

# show df summary: https://spark.apache.org/docs/3.1.2/api/python/reference/api/pyspark.sql.DataFrame.summary.html
joined_df.summary().show()

# filtering and sorting
joined_df.where((f.col('MedHouseVal') > 2.0) & (f.col('HouseAge') < 10.0)).orderBy(f.col('HouseAge').desc()).show()

# grouping
joined_df.groupby(f.col('HouseAge')).agg(f.count('HouseId').alias('count'), f.sum('Population').alias('total_population')).orderBy(f.col('count').desc()).show()

# persist (note that with multiple workers there will be multiple partitions)
joined_df.write.format('parquet').mode('overwrite').save('s3a://data/output/')


