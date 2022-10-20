import os
import click
import pandas as pd
import hashlib

from tqdm import tqdm
from pandas_profiling import ProfileReport


@click.command()
@click.option("--input", required=True)
@click.option("--output", required=True)
def main(input: str, output: str):
    print('start eda job')
    if os.path.isfile(input):
        input_files = [input]
    else:
        for dirpath, dirs, files in os.walk(input):
            input_files = [os.path.join(dirpath, filename) for filename in files if filename.endswith('.parquet')]
    input_files = sorted(input_files)

    print('input files:', input_files)
    if len(input_files) == 0:
        return

    data = pd.concat([pd.read_parquet(x) for x in input_files])
    profile = ProfileReport(data, title="Dataset Profiling Report")

    files_hash = hashlib.md5(','.join(input_files).encode('utf-8')).hexdigest()
    profile.to_file(os.path.join(output, f'eda_profile_{files_hash}.html'))


if __name__ == "__main__":
    main()
