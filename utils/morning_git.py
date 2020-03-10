import git
import sys, os

def morning_git_version():
    morning_path = ''
    try:
        morning_path = os.environ['MORNING_PATH']
    except KeyError:
        print('NO MORNING_PATH ENV') 
        return morning_path

    repo = git.Repo(morning_path)
    commits = list(repo.iter_commits('master', max_count=5))
    return commits[0].hexsha + '_' + commits[0].message


if __name__ == '__main__':
    print(morning_git_version())
