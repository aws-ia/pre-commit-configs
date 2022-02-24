import sys
import argparse
import json
from pathlib import Path
from .base import get_transform_modules
from . import _transformers as tform


def files_from_dir(directory):
    files = []
    d = Path(directory).expanduser().resolve()
    for x in d.iterdir():
        if x.is_file():
            files.append(x)
    return files


def execute_transform(commit_id, files):
    results = []
    tfm = get_transform_modules(tform)
    for file in files:
        tmod = tfm.get(file.suffix)
        if not tmod:
            continue
        with open(file) as f:
            d = json.load(f)
        tresults = tmod.RawData(
            transformer_cls=tmod.Transformer,
            commit_id=commit_id,
            success=False,
            raw_data=d
        ).generate_output()
        if tresults:
            results += tresults
    return results


def main():
    args = sys.argv[1:]
    if not args:
        args.append("-h")
    parser = argparse.ArgumentParser(description='output format customizer')
    parser.add_argument('-d', '--directory', type=str, required=True)
    parser.add_argument('-o', '--output-file', type=str, required=True)
    parser.add_argument('-c', '--commit-id', type=str, required=True)
    args = parser.parse_args()

    files = files_from_dir(args.directory)
    results = execute_transform(args.commit_id, files)

    with open(args.output_file, 'w') as f:
        f.write(json.dumps(results))
    return
