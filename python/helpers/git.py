# Git functionality removed - using hardcoded version instead
# from git import Repo
# from datetime import datetime
# import os
# from python.helpers import files

def get_git_info():
    # try:
    #     # Get the current working directory (assuming the repo is in the same folder as the script)
    #     repo_path = files.get_base_dir()

    #     # Configure git safe directory to avoid ownership issues
    #     import subprocess
    #     try:
    #         subprocess.run(['git', 'config', '--global', '--add', 'safe.directory', repo_path],
    #                      check=True, capture_output=True)
    #     except subprocess.CalledProcessError:
    #         # If git config fails, continue anyway
    #         pass

    #     # Open the Git repository
    #     repo = Repo(repo_path)

    #     # Ensure the repository is not bare
    #     if repo.bare:
    #         raise ValueError(f"Repository at {repo_path} is bare and cannot be used.")

    #     # Get the current branch name
    #     branch = repo.active_branch.name if repo.head.is_detached is False else "detached"

    #     # Get the latest commit hash
    #     commit_hash = repo.head.commit.hexsha

    #     # Get the commit date (ISO 8601 format)
    #     commit_time = datetime.fromtimestamp(repo.head.commit.committed_date).strftime('%y-%m-%d %H:%M')

    #     # Get the latest tag description (if available)
    #     short_tag = ""
    #     try:
    #         tag = repo.git.describe(tags=True)
    #         tag_split = tag.split('-')
    #         if len(tag_split) >= 3:
    #             short_tag = "-".join(tag_split[:-1])
    #         else:
    #             short_tag = tag
    #     except:
    #         tag = ""

    #     version = branch[0].upper() + " " + ( short_tag or commit_hash[:7] )

    #     # Create the dictionary with collected information
    #     git_info = {
    #         "branch": branch,
    #         "commit_hash": commit_hash,
    #         "commit_time": commit_time,
    #         "tag": tag,
    #         "short_tag": short_tag,
    #         "version": version
    #     }

    #     return git_info
    # except Exception as e:
    #     print(f"Warning: Could not get Git info from {files.get_base_dir()}: {e}")
    #     # Fallback: try to get basic info from environment variables set during Docker build
    #     import os
    #     commit_hash = os.environ.get('GIT_COMMIT', 'unknown')[:7]  # Short hash
    #     branch = os.environ.get('GIT_BRANCH', 'unknown')
    #     tag = os.environ.get('GIT_TAG', '')
    #     build_date = os.environ.get('BUILD_DATE', 'unknown')

    #     # Format version similar to Git describe
    #     if tag and tag != 'unknown':
    #         version = tag
    #     elif branch and branch != 'unknown':
    #         version = f"{branch[0].upper()} {commit_hash}"
    #     else:
    #         version = f"dev {commit_hash}"

    #     return {
    #         "branch": branch,
    #         "commit_hash": commit_hash,
    #         "commit_time": build_date,
    #         "tag": tag,
    #         "short_tag": tag,
    #         "version": version
    #     }
            # Hardcoded version information (Git repo removed from container)
        return {
            "branch": "main",
            "commit_hash": "7b98b7a42916c9ea83f19a3d0d7a72bd4d170fbb",
            "commit_time": "Nov 19, 2025",
            "tag": "v0.9.7",
            "short_tag": "v0.9.7",
            "version": "v0.9.7"
        }

def get_version():
    try:
        git_info = get_git_info()
        return str(git_info.get("short_tag", "")).strip() or "unknown"
    except Exception:
        return "unknown"