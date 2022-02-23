#!/usr/bin/env python3
import argparse
import yaml
from pathlib import Path

def modify_existing(config, existing):
    for k,v in config.get('root_args',{}).items():
        existing[k] = v
    for repo_idx, repo_definition in enumerate(existing.get('repos',[])):
        mod_config = config.get('repo_args',{}).get(repo_definition['repo'])
        if mod_config:
            for hook_idx, hook in enumerate(repo_definition['hooks']):
                for x,y in mod_config.get(hook['id'], {}).items():
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
    args = parser.parse_args()
    
    with open(Path(args.config).expanduser().resolve()) as f:
        config = yaml.safe_load(f)

    with open(Path(args.input).expanduser().resolve()) as f:
        existing = yaml.safe_load(f)

    modified = modify_existing(config, existing)

    with open(Path(args.output).expanduser().resolve(), 'w') as f:
        f.write(yaml.dump(modified))
