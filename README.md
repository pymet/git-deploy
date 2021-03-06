# git-deploy

Deploy a git repo using git-hooks, because `git push production` is just awesome. To get more details about automated tasks using git hooks please follow: [how-to-use-git-hooks-to-automate-development-and-deployment-tasks](https://www.digitalocean.com/community/tutorials/how-to-use-git-hooks-to-automate-development-and-deployment-tasks) or [setting-up-push-to-deploy-with-git](http://krisjordan.com/essays/setting-up-push-to-deploy-with-git) or [using-git-to-deploy-code](http://mikeeverhart.net/2013/01/using-git-to-deploy-code).

**To get the server setup, please follow the [Prerequisites](https://github.com/pymet/git-deploy/blob/master/PREREQUISITES.md) section.**

### Usage

```sh
wget https://pymet.github.io/git-deploy/git-deploy.py
python3 git-deploy.py myproject
```

### Download

You can download the script [here](https://pymet.github.io/git-deploy/git-deploy.py) or [here](https://raw.githubusercontent.com/pymet/git-deploy/master/git-deploy.py).

### Configuration

The default `config.json` is the following:

```json
{
	"*": {
		"allow": true,
		"work-tree": null,
		"pre-message": null,
		"post-message": null,
		"timeout-message": null,
		"timeout": null,
		"exec": null
	}
}
```

The `"*"` rule will match **any** of the branches except for those that have a custom rule set.
The following snippet will allow push for the master branch **only**.

```json
{
	"master": {
		"allow": true
	},
	"*": {
		"allow": false
	}
}
```

- The `allow` parameter will be used in the `pre-receive` step. If `allow` is set to `false`, the branch will be **rejected**.
- If `work-tree` parameter is not `null`, the content of the branch will be checked out there. The folder will be created if does not exists.

#### Deploy to /var/www/html

```json
{
	"master": {
		"work-tree": "/var/www/html"
	}
}
```

- `pre-message`, `post-message` and `timeout-message` will be printed in the git push result.

```json
{
	"master": {
		"pre-message": "This is the pre-message",
		"post-message": "This is the post-message",
		"timeout-message": "This is the timeout-message",
		"timeout": 1.0,
		"exec": "sleep 3"
	}
}
```

Running **git push dev**

```
Counting objects: 3, done.
Writing objects: 100% (3/3), 246 bytes | 0 bytes/s, done.
Total 3 (delta 0), reused 0 (delta 0)
remote: This is the pre-message
remote: This is the post-message
remote: This is the timeout-message
To 123.123.123.123:testrepo
   b1556f2..9a3b525  master -> master
```

- If `exec` is not `null`, it will be executed after the repo is checked out.

```json
{
	"master": {
		"work-tree": "/path/to/your/project",
		"exec": "make -C /path/to/your/project"
	}
}
```

#### Exec can be given as a list

```
"exec": "make -C /path/to/your/project"
```
is the same as:
```
"exec": ["make", "-C", "/path/to/your/project"]
```

#### Disallow a branch

```json
{
	"master": {
		"allow": false,
		"pre-message": "One does not simpli push the master here. (try dev)"
	},
	"dev": {
		"allow": true,
		"work-tree": "/var/www/html"
	}
}
```

Running **git push dev**
```
Counting objects: 3, done.
Writing objects: 100% (3/3), 247 bytes | 0 bytes/s, done.
Total 3 (delta 0), reused 0 (delta 0)
remote: One does not simpli push the master here. (try dev)
To 123.123.123.123:testrepo
 ! [remote rejected] master -> master (pre-receive hook declined)
error: failed to push some refs to 'root@123.123.123.123:testrepo'
```

#### Complex task

Place **complex-task.sh** next to the **config.json**. Once the master branch is pushed, the **complex-task.sh** will be called.

```
+ myproject-hooks/
|      config.json
|      complex-task.sh
```

```json
{
	"master": {
		"exec": "sh complex-task.sh"
	}
}
```

- If `timeout` is not `null`, the task will be killed after `timeout` seconds and the `timeout-message` will be shown.

```json
{
	"master": {
		"timeout-message": "No one can sleep 5 seconds under 2.5 seconds",
		"timeout": 2.5,
		"exec": "sleep 5"
	}
}
```

#### Broken config file

```
Counting objects: 2, done.
Writing objects: 100% (2/2), 197 bytes | 0 bytes/s, done.
Total 2 (delta 0), reused 0 (delta 0)
remote: Config file is broken: Expecting property name enclosed in double quotes: line 5 column 2 (char 106)
remote: Config file is broken: Expecting property name enclosed in double quotes: line 5 column 2 (char 106)
To 123.123.123.123:testrepo
   9a3b525..47cd617  master -> master
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

```sh
$ python3 git-deploy.py myproject
```

```
Add or set the remote url:
        git remote add dev git@123.123.123.123:myproject
        git remote set-url dev git@123.123.123.123:myproject

Clone the hooks branch:
        git clone -b hooks git@123.123.123.123:myproject myproject-hooks
```

#### Offline

```sh
$ python3 git-deploy.py myproject --offline
```

#### Verbose

```sh
$ python3 git-deploy.py myproject --verbose --offline
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

#### Customize branch

```sh
$ python3 git-deploy.py myproject -b custom-hooks
```
```
...
Clone the custom-hooks branch:
        git clone -b custom-hooks git@123.123.123.123:myproject myproject-hooks
...
```

#### Customize the commit

```sh
$ python3 git-deploy.py myproject            \
          --git-user "John Doe"              \
          --git-email "john.doe@localhost"   \
          --git-message "Hello World!"
```

### Acknowledgement

Thank you for the [ipify-api](https://github.com/rdegges/ipify-api)
