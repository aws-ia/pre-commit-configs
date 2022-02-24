#!/usr/bin/env python3
import configparser
import argparse
import json
import base64
import yaml
from pathlib import Path


def _inspect_dir(dir_path):
    r = {}

    c = configparser.ConfigParser()
    c.read(f"{dir_path}/.git/config")
    origin_url = c['remote "origin"']['url']

    with open(f"{dir_path}/.pre-commit-hooks.yaml") as f:
        pch = yaml.safe_load(f)

    for h in pch:
        _u = f"{origin_url.replace('https://github.com/','')}.{h['id']}"
        uuid_prefix = base64.b64encode(_u.encode()).decode().replace('=', '')
        try:
            r[origin_url][h['id']] = uuid_prefix
        except KeyError:
            r[origin_url] = {h['id']: uuid_prefix}

    return r


def fetch_hook_metadata(cache_dir):
    results = {}
    d = Path(cache_dir).expanduser().resolve()
    for x in d.iterdir():
        if x.is_dir():
            _per_dir_results = _inspect_dir(x)
            results.update(**_per_dir_results)
    return results


def modify_existing(config, existing, hmd):
    for k,v in config.get('root_args',{}).items():
        existing[k] = v
    
    for repo_idx, repo_definition in enumerate(existing.get('repos',[])):
        mod_config = config.get('repo_args',{}).get(repo_definition['repo'])
        
        if mod_config:
            for hook_idx, hook in enumerate(repo_definition['hooks']):
                for x,y in mod_config.get(hook['id'], {}).items():
                    if x == 'meta':
                        lf_ext = y.get('extension')
                        if lf_ext:
                            fn_prefix = hmd[repo_definition['repo']][hook['id']]
                            existing['repos'][repo_idx]['hooks'][hook_idx]['log_file'] = f"/tmp/{fn_prefix}.{lf_ext}"
                        continue
                    if mod_config[hook['id']].get(x):
                        existing['repos'][repo_idx]['hooks'][hook_idx][x] += y
                    else:
                        existing['repos'][repo_idx]['hooks'][hook_idx][x] = y
    return existing


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Automatically generates pre-commit config for CI usage"
    )
    parser.add_argument('--config', type=str, required=True)
    parser.add_argument('--input', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--cache-dir', type=str, required=True)
    parser.add_argument('--metadata-file-out', type=str, required=True)
    args = parser.parse_args()

    hook_name_metadata = fetch_hook_metadata(args.cache_dir)

    with open(Path(args.config).expanduser().resolve()) as f:
        config = yaml.safe_load(f)

    with open(Path(args.input).expanduser().resolve()) as f:
        existing = yaml.safe_load(f)

    modified = modify_existing(config, existing, hook_name_metadata)

    with open(Path(args.output).expanduser().resolve(), 'w') as f:
        f.write(yaml.dump(modified))

    _rev_hmd = {}
    for rurl, _x in hook_name_metadata.items():
        for hid, h in _x.items():
            _rev_hmd[h] = {rurl:hid}
    with open(Path(args.metadata_file_out).expanduser().resolve(), 'w') as f:
        f.write(json.dumps(_rev_hmd, indent=2, sort_keys=True))


