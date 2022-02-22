import json
import re
import argparse
from pathlib import Path

def convert_output(input_file):
    results = {}
    regex = '^(\w).+\.+(\w|\W)+\\n'
    escapes = {char:None for char in range(1,32)}
    with open(Path(input_file).expanduser().resolve()) as f:
        d = f.readlines()
    for i in d:
        if re.search(pattern=regex, string=i):
            strl = i.split('..')
            results[strl[0]] = re.sub('\[.*?m|\.','', strl[-1].translate(escapes))
    return results

def write_output_file(output_file, results):
    with open(Path(output_file).expanduser().resolve(),'w') as f:
        f.write(json.dumps(results))
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse pre-commit command output to json format"
    )
    parser.add_argument("-i","--input-file", type=str, help="Input file")
    parser.add_argument("-o","--output-file",type=str, help="Output file")
    args = parser.parse_args()
    if not args.input_file or not args.output_file:
        raise
    results = convert_output(args.input_file)
    if results:
        write_output_file(args.output_file, results)
