from kfp.components import InputPath, OutputPath


def evaluation(model_path: InputPath('DecisionTreeRegressor'),
               preprocessor_path: InputPath('StandardScaler'),
               dataset_path: InputPath('Dataset'),
               mlpipeline_metrics_path: OutputPath('Metrics'),
               mlpipeline_ui_metadata_path: OutputPath()):
    import json
    import pandas as pd
    import numpy as np
    from joblib import load
    from sklearn.metrics import mean_squared_error, r2_score

    TARGET_COLUMN = 'MedHouseVal'

    df = pd.read_csv(dataset_path)
    X, y = df.drop(columns=[TARGET_COLUMN]), df[TARGET_COLUMN]

    regressor = load(model_path)
    scaler = load(preprocessor_path)
    X_transformed = scaler.fit_transform(X)
    y_log = np.log(y)

    y_pred = regressor.predict(X_transformed)
    val_neg_mse = -mean_squared_error(y_pred, y_log)
    val_r2 = r2_score(y_pred, y_log)

    with open(mlpipeline_metrics_path, 'w') as f:
        json.dump({
            'metrics': [{
                'name': 'val-neg-mean-sq-error',
                'numberValue': val_neg_mse,
                'format': "RAW",
            }, {
                'name': 'val-r-squared',
                'numberValue': val_r2,
                'format': "RAW",
            }]
        }, f)

    with open(mlpipeline_ui_metadata_path, 'w') as f:
        json.dump({
            'outputs': [{
                'type': 'table',
                'storage': 'inline',
                'format': 'csv',
                'header': ['feature', 'importance'],
                'source': pd.DataFrame({
                    'feature': X.columns,
                    'importance': regressor.feature_importances_
                }).sort_values('importance', ascending=False) \
                  .to_csv(header=False, index=False)
            }]
        }, f)
