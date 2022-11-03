from kfp.components import InputPath, OutputPath


def training(dataset_path: InputPath('Dataset'),
             model_path: OutputPath('DecisionTreeRegressor'),
             preprocessor_path: OutputPath('StandardScaler'),
             mlpipeline_metrics_path: OutputPath('Metrics')):
    import pandas as pd
    import numpy as np
    import json
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import cross_validate
    from joblib import dump
    from sklearn.metrics import mean_squared_error, r2_score

    TARGET_COLUMN = 'MedHouseVal'

    df = pd.read_csv(dataset_path)
    X, y = df.drop(columns=[TARGET_COLUMN]), df[TARGET_COLUMN]

    print(f"Train features: {X.columns}")

    scaler = StandardScaler()
    X_transformed = scaler.fit_transform(X)
    y_log = np.log(y)

    regressor = DecisionTreeRegressor()
    cv_scores = cross_validate(estimator=regressor, X=X_transformed, y=y_log, cv=10,
                               scoring=('r2', 'neg_mean_squared_error'))
    print(f"CV scores: {cv_scores['test_r2']}")

    regressor.fit(X_transformed, y_log)
    y_pred = regressor.predict(X_transformed)
    train_neg_mse = -mean_squared_error(y_pred, y_log)
    train_r2 = r2_score(y_pred, y_log)

    print(f"Train metrics: Neg MSE {train_neg_mse}, R2 {train_r2}")

    dump(regressor, model_path)
    dump(scaler, preprocessor_path)

    with open(mlpipeline_metrics_path, 'w') as f:
        json.dump({
            'metrics': [{
                'name': 'cv-mean-r-squared',
                'numberValue': cv_scores['test_r2'].mean(),
                'format': "RAW",
            }, {
                'name': 'cv-mean-neg-mean-sq-error',
                'numberValue': cv_scores['test_neg_mean_squared_error'].mean(),
                'format': "RAW",
            }, {
                'name': 'train-neg-mean-sq-error',
                'numberValue': train_neg_mse,
                'format': "RAW",
            }, {
                'name': 'train-r-squared',
                'numberValue': train_r2,
                'format': "RAW",
            }]
        }, f)
