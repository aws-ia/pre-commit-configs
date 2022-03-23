# AWS-IA uses pre-commits to run static code analysis on PRs. All projects that leverage this mechanism will have a `.metadata` folder in the root of the repo. 

## Example: of metadata folder
```.metadata
├── cloudformation
└── terraform
```
Precommit will check the metadata folder to determine which configurations to run when a PR is raised in GitHub.

