# Gitlab mass cloner

A simple yet efficient multiple goup (and subgroup) gitlab cloner in python.

```
usage: cloneall.py [-h] [--group_ids GROUP_IDS [GROUP_IDS ...]] [--gitlab_url GITLAB_URL] [--gitlab_token GITLAB_TOKEN] [--output_folder OUTPUT_FOLDER] [--branch BRANCH]

Script to clone projects from GitLab groups.

options:
  -h, --help            show this help message and exit
  --group_ids GROUP_IDS [GROUP_IDS ...]
                        List of GitLab group IDs to clone.
  --gitlab_url GITLAB_URL
                        GitLab instance URL.
  --gitlab_token GITLAB_TOKEN
                        GitLab token with appropriate permissions.
  --output_folder OUTPUT_FOLDER
                        Folder where the projects will be cloned.
  --branch BRANCH       Branch to switch to after cloning (if it exists).
```

## Known issues

- Only clones in https
