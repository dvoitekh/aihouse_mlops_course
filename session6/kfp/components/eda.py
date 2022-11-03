import json
import pandas as pd

from kfp.components import InputPath, OutputPath


def eda(dataset_path: InputPath('Dataset'), mlpipeline_ui_metadata_path: OutputPath()):
    import pandas as pd
    import json
    from pandas_profiling import ProfileReport

    df = pd.read_csv(dataset_path)
    profile = ProfileReport(df, title="Dataset Profiling Report")

    with open(mlpipeline_ui_metadata_path, 'w') as f:
        json.dump({
            'outputs': [{
                'storage': 'inline',
                'source': profile.to_html(),
                'type': 'web-app',
            }]
        }, f)


if __name__ == "__main__":
    test_dataset_path = '/tmp/test.csv'
    output_report_path = '/tmp/report.json'
    pd.DataFrame({'a': [1,2,3,4,5], 'b': [1,2,3,4,5]}).to_csv(test_dataset_path, index=False)

    eda(test_dataset_path, output_report_path)

    with open(output_report_path) as f:
        report = json.load(f)

    assert list(report.keys()) == ['outputs']
    assert len(report['outputs']) == 1
    assert sorted(report['outputs'][0].keys()) == ['source', 'storage', 'type']

