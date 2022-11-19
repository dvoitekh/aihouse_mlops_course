FROM python:3.8.12
WORKDIR /app

# Install python packages
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy source code
COPY . .

# Define environment variables
ENV HOME /app
ENV MODEL_NAME src.Preprocessor
ENV SERVICE_TYPE MODEL
ENV FEATURE_STORE_PATH /app/feature_store/
ENV PREPROCESSSING_PATH /app/checkpoints/preprocessing.joblib
ENV MODEL_PATH /app/checkpoints/model.joblib
ENV OUTLIER_DETECTOR_MODEL_PATH /app/checkpoints/od.joblib

ENV AWS_ACCESS_KEY_ID minioadmin
ENV AWS_SECRET_ACCESS_KEY minioadmin
ENV FEAST_S3_ENDPOINT_URL http://helm-minio.default.svc:9000

# Changing folder to default user
RUN chown -R 8888 /app

CMD exec seldon-core-microservice $MODEL_NAME --service-type $SERVICE_TYPE
