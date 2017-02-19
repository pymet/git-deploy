# git-deploy

Deploy a git repo using git-hooks

### Usage

```sh
wget https://pymet.github.io/git-deploy/git-deploy.py
python3 git-deploy.py myproject
```

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

> #### Deploy to /var/www/html
> 
> ```json
> {
> 	"master": {
> 		"work-tree": "/var/www/html"
> 	}
> }
> ```

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

```sh
$ git push dev
```

```
Counting objects: 3, done.
Writing objects: 100% (3/3), 246 bytes | 0 bytes/s, done.
Total 3 (delta 0), reused 0 (delta 0)
remote: This is the pre-message
remote: This is the post-message
remote: This is the timeout-message
To 138.68.79.224:testrepo
   b1556f2..9a3b525  master -> master
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
