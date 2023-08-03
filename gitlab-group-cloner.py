#!/usr/bin/python
import os
import requests
import subprocess
import argparse

def get_gitlab_groups(gitlab_url, gitlab_token, parent_group_id=None):
    headers = {
        "PRIVATE-TOKEN": gitlab_token
    }
    if parent_group_id:
        url = f"{gitlab_url}/api/v4/groups/{parent_group_id}/subgroups"
    else:
        url = f"{gitlab_url}/api/v4/groups"

    response = requests.get(url, headers=headers)

    if response.status_code == 401:
        raise Exception("Authentication error. Please check that your GitLab token is correct and has the necessary permissions.")
    elif response.status_code != 200:
        raise Exception(f"An error occurred while retrieving groups: {response.status_code} - {response.text}")

    groups = response.json()
    return groups

def get_gitlab_projects(group_id, gitlab_url, gitlab_token):
    headers = {
        "PRIVATE-TOKEN": gitlab_token
    }
    url = f"{gitlab_url}/api/v4/groups/{group_id}/projects"
    response = requests.get(url, headers=headers)

    if response.status_code == 401:
        raise Exception("Authentication error. Please check that your GitLab token is correct and has the necessary permissions.")
    elif response.status_code != 200:
        raise Exception(f"An error occurred while retrieving projects: {response.status_code} - {response.text}")

    projects = response.json()
    return projects

def branch_exists(repo_path, branch):
    result = subprocess.run(["git", "show-ref", f"refs/heads/{branch}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def clone_projects(group_id, group_name, gitlab_url, gitlab_token, output_folder, branch):
    try:
        projects = get_gitlab_projects(group_id, gitlab_url, gitlab_token)

        group_folder = os.path.join(output_folder, group_name)
        if not os.path.exists(group_folder):
            os.makedirs(group_folder)

        for project in projects:
            project_name = project["name"]
            project_url = project["ssh_url_to_repo"]
            project_folder = os.path.join(group_folder, project_name)

            if not os.path.exists(project_folder):
                subprocess.run(["git", "clone", project_url, project_folder])
            else:
                print(f"The project '{project_name}' already exists in group '{group_name}', it will not be cloned again.")

            # Check if the branch exists and switch to it if it does
            if branch and branch_exists(project_folder, branch):
                os.chdir(project_folder)
                subprocess.run(["git", "checkout", "-B", branch], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f"All projects in group '{group_name}' have been cloned successfully.")

        # Get subgroups and clone their projects recursively.
        subgroups = get_gitlab_groups(gitlab_url, gitlab_token, group_id)
        for subgroup in subgroups:
            subgroup_id = subgroup["id"]
            subgroup_name = subgroup["name"]
            clone_projects(subgroup_id, subgroup_name, gitlab_url, gitlab_token, group_folder, branch)

    except Exception as e:
        print(f"An error occurred: {e}")

def clone_projects_from_groups(group_ids, gitlab_url, gitlab_token, output_folder, branch):
    for group_id in group_ids:
        group_name = get_group_name(group_id, gitlab_url, gitlab_token)
        clone_projects(group_id, group_name, gitlab_url, gitlab_token, output_folder, branch)

def get_group_name(group_id, gitlab_url, gitlab_token):
    headers = {
        "PRIVATE-TOKEN": gitlab_token
    }
    url = f"{gitlab_url}/api/v4/groups/{group_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 401:
        raise Exception("Authentication error. Please check that your GitLab token is correct and has the necessary permissions.")
    elif response.status_code != 200:
        raise Exception(f"An error occurred while retrieving the group: {response.status_code} - {response.text}")

    group_data = response.json()
    return group_data["name"]

def main():
    parser = argparse.ArgumentParser(description="Script to clone projects from GitLab groups.")
    parser.add_argument("--group_ids", nargs="+", help="List of GitLab group IDs to clone.")
    parser.add_argument("--gitlab_url", help="GitLab instance URL.")
    parser.add_argument("--gitlab_token", help="GitLab token with appropriate permissions.")
    parser.add_argument("--output_folder", help="Folder where the projects will be cloned.")
    parser.add_argument("--branch", help="Branch to switch to after cloning (if it exists). (Optionnal)")
    args = parser.parse_args()

    # Check environment variables
    if not args.group_ids:
        args.group_ids = os.getenv("GROUP_IDS")
    if not args.gitlab_url:
        args.gitlab_url = os.getenv("GITLAB_URL")
    if not args.gitlab_token:
        args.gitlab_token = os.getenv("GITLAB_TOKEN")
    if not args.output_folder:
        args.output_folder = os.getenv("OUTPUT_FOLDER")

    if not args.group_ids or not args.gitlab_url or not args.gitlab_token or not args.output_folder:
        parser.error("Please specify the missing parameters: --group_ids, --gitlab_url, --gitlab_token, and --output_folder.")

    clone_projects_from_groups(args.group_ids, args.gitlab_url, args.gitlab_token, args.output_folder, args.branch)

if __name__ == "__main__":
    main()
