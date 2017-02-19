# git-deploy
Deploy a git repo using git-hooks

### Usage

```sh
wget https://pymet.github.io/git-deploy/git-deploy.py
python3 git-deploy.py myproject
```

### Help

```
usage: git-deploy.py [-h] [-o ORIGIN] [-b BRANCH] [-v] [--git-user GIT_USER]
                     [--git-email GIT_EMAIL] [--git-msg GIT_MSG] [--offline]
                     path

Generate repository and branch for git-hooks

positional arguments:
  path                         Path for the git repository

optional arguments:
  -h, --help                   show this help message and exit
  -o ORIGIN, --origin ORIGIN   Origin to use for the hint
  -b BRANCH, --branch BRANCH   Branch for the hooks
  -v, --verbose                Set verbosity
  --git-user GIT_USER          Username for the commit
  --git-email GIT_EMAIL        Email for the commit
  --git-msg GIT_MSG            Message for the commit
  --offline                    Skip using online tools for detecting the host IP
```

### Examples

#### Simple

```sh
$ python3 git-deploy.py myprojec
```

```
Add or set the remote url:
        git remote add dev git@123.123.123.123:myprojec
        git remote set-url dev git@123.123.123.123:myprojec


Clone the script branch:
        git clone -b hooks git@123.123.123.123:myprojec myprojec-hooks
```

#### Offline

```sh
$ python3 git-deploy.py myprojec --offline
```

#### Verbose

```sh
$ python3 git-deploy.py myprojec --verbose --offline
```

```
Working in /home/git/myproject

git init --bare --quiet

Working in /tmp/tmp4bpkoxok

git init --quiet
git add config.json
git checkout -b hooks --quiet
git -c user.name=GitBot -c user.email=gitbot@localhost commit -m "Initial config" --quiet
git remote add origin /home/git/myproject
git push origin hooks --quiet

Working in /home/git/myproject/hooks

ln -s receive.py pre-receive
ln -s receive.py post-receive
chmod 755 pre-receive post-receive

Working in /home/git/myproject

git --work-tree=/home/git/myproject/hooks/custom checkout hooks -f --quiet
```

### Acknowledgement

Thank you for the [ipify-api](https://github.com/rdegges/ipify-api)
