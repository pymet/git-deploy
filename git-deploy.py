#!/usr/bin/python3

import os, sys, subprocess, getpass, argparse, tempfile, urllib.request


parser = argparse.ArgumentParser(description = 'Generate repository and branch for git-hooks')
parser.add_argument('path', help = 'Path for the git repository')
parser.add_argument('-o', '--origin', default = 'dev', help = 'Origin to use for the hint')
parser.add_argument('-b', '--branch', default = 'hooks', help = 'Branch for the hooks')
parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = 'Set verbosity')
parser.add_argument('--git-user', default = 'GitBot', help = 'Username for the commit')
parser.add_argument('--git-email', default = 'gitbot@localhost', help = 'Email for the commit')
parser.add_argument('--git-msg', default = 'Initial config', help = 'Message for the commit')
parser.add_argument('--offline', action = 'store_true', default = False, help = 'Skip using online tools for detecting the host IP')
args = parser.parse_args()

args.path = os.path.normpath(os.path.abspath(args.path))


# default config file

config = r'''
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
'''

# default pre-receive & post-receive handler

receive = r'''
#!/usr/bin/python3

import os, sys, json, shlex, subprocess


# loading the config file from the branch

try:
	config = json.loads(open('hooks/custom/config.json').read())

# invalid config file

except json.JSONDecodeError as ex:
	print('Config file is broken: ' + str(ex))
	config = {}

# missing config file

except IOError as ex:
	print('No config file found')
	config = {}


def get_config(branch):
	"""
		Get the configuration for a branch.
	"""

	# default values

	values = {
		'allow': True,
		'work-tree': None,
		'pre-message': None,
		'post-message': None,
		'timeout-message': None,
		'timeout': None,
		'exec': None,
	}

	# load branch specific settings

	if branch in config:
		values.update(config[branch])

	# load global settings

	elif '*' in config:
		values.update(config['*'])

	return values


def git_checkout(path, branch):
	"""
		Checkout the branch to path.
	"""

	# cache is not allowed
	
	os.system('unset GIT_INDEX_FILE')
	os.makedirs(path, exist_ok = True)

	# simulate a standard git checkout
	# git will think we are checking out the same branch as before

	open('HEAD', 'w').write('ref: refs/heads/%s\n' % branch)
	cmd = ['git', '--work-tree=' + path, 'checkout', branch, '-f', '--quiet']
	proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
	proc.wait()

	# keep the master as the main branch

	open('HEAD', 'w').write('ref: refs/heads/master\n')
	return proc.stdout.read().decode()

"""
git-hooks:

	pre-receive:

		This is called on the remote repo just before updating the pushed
		refs. A non-zero status will abort the process. Although it receives
		no parameters, it is passed a string through stdin in the form of
		"<old-value> <new-value> <ref-name>" for each ref.

	post-receive:

		This is run on the remote when pushing after the all refs have been
		updated. It does not take parameters, but receives info through stdin
		in the form of "<old-value> <new-value> <ref-name>". Because it is
		called after the updates, it cannot abort the process.
"""

lines = sys.stdin.read().splitlines()
script = sys.argv[0].split('/')[-1]

for line in lines:
	old, new, ref = line.split()
	branch = ref.split('/')[-1]

	# check for the HOOKS_BRANCH branch

	if branch == 'HOOKS_BRANCH':
		git_checkout('hooks/custom', 'HOOKS_BRANCH')
		continue

	# load the config for the branch

	cfg = get_config(branch)

	# check if the the push is allowed

	if script == 'pre-receive':

		if cfg['pre-message']:
			print(cfg['pre-message'])

		if not cfg['allow']:
			exit(1)

	# check if we have post-receive task

	if script == 'post-receive':

		# message

		if cfg['post-message']:
			print(cfg['post-message'])

		# checkout

		if cfg['work-tree']:
			message = git_checkout(cfg['work-tree'], branch)

			if message:
				print(message, end = '' if message.endswith('\n') else '\n')

		# post-receive task

		if cfg['exec']:
			try:
				if type(cfg['exec']) is str:
					cfg['exec'] = shlex.split(cfg['exec'])
				
				proc = subprocess.Popen(cfg['exec'], cwd = 'hooks/custom', stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
				proc.wait(cfg['timeout'])

			# process timed out

			except subprocess.TimeoutExpired:
				if cfg['timeout-message']:
					print(cfg['timeout-message'])

				proc.kill()

			# process failed

			except Exception as ex:
				print(ex)

			# print stdout

			finally:
				try:
					stdout = proc.stdout.read().decode()

					if stdout:
						print(stdout, end = '' if stdout.endswith('\n') else '\n')

				except:
					pass
'''


# commands

branch_commands = [
	['git', 'init', '--quiet'],
	['git', 'add', 'config.json'],
	['git', 'checkout', '-b', args.branch, '--quiet'],
	['git', '-c', 'user.name=' + args.git_user, '-c', 'user.email=' + args.git_email, 'commit', '-m', args.git_msg, '--quiet'],
	['git', 'remote', 'add', 'origin', args.path],
	['git', 'push', 'origin', args.branch, '--quiet'],
]

hooks_commands = [
	['ln', '-s', 'receive.py', 'pre-receive'],
	['ln', '-s', 'receive.py', 'post-receive'],
	['chmod', '755', 'pre-receive', 'post-receive'],
]


# using non documented function

try:
	cmd_join = subprocess.list2cmdline

except:
	cmd_join = lambda x: str(x)


def execute(cmd, cwd):
	'''
		Execute a command in a directory
	'''

	settings = {
		'stderr': subprocess.STDOUT,
		'stdout': subprocess.PIPE,
		'cwd': cwd,
	}

	if args.verbose:
		print('\033[97m%s\033[m' % cmd_join(cmd))

	proc = subprocess.Popen(cmd, **settings)
	proc.wait()

	if args.verbose:
		msg = proc.stdout.read().decode().strip('\n')
		if msg:
			print('\n' + msg)

	if proc.returncode != 0:
		print('\033[31mTask `%s` failed with %d errorcode\033[m' % (cmd_join(cmd), proc.returncode))
		exit(1)


# initialize the repo

if os.path.exists(args.path):
	if not os.path.exists(os.path.join(args.path, 'HEAD')):
		print('\033[31m%s is probably not a git repository\033[m' % args.path)
		exit(1)

	if os.path.exists(os.path.join(args.path, 'refs', 'heads', args.branch)):
		print('\033[31mBranch %s already exists\033[m' % args.branch)
		exit(1)

else:
	os.mkdir(args.path)

	if args.verbose:
		print('\nWorking in %s\n' % args.path)

	execute(['git', 'init', '--bare', '--quiet'], args.path)


# initialize the branch

with tempfile.TemporaryDirectory() as temp:
	if args.verbose:
		print('\nWorking in %s\n' % temp)

	open(os.path.join(temp, 'config.json'), 'w').write(config.strip('\n') + '\n')
	
	for cmd in branch_commands:
		execute(cmd, temp)


# initialize hooks

hooks = os.path.join(args.path, 'hooks')

open(os.path.join(hooks, 'receive.py'), 'w').write(receive.replace('HOOKS_BRANCH', args.branch).strip('\n') + '\n')

if args.verbose:
	print('\nWorking in %s\n' % hooks)

for cmd in hooks_commands:
	execute(cmd, hooks)


# checkout hooks

custom = os.path.join(hooks, 'custom')

if args.verbose:
	print('\nWorking in %s\n' % args.path)

os.mkdir(custom)

open(os.path.join(args.path, 'HEAD'), 'w').write('ref: refs/heads/%s\n' % args.branch)
execute(['git', '--work-tree=' + custom, 'checkout', args.branch, '-f', '--quiet'], args.path)
open(os.path.join(args.path, 'HEAD'), 'w').write('ref: refs/heads/master\n')


# show the hints

if not args.offline:
	host = urllib.request.urlopen('https://api.ipify.org').read().decode()
	user = getpass.getuser()

	short_path = os.path.relpath(args.path, os.path.expanduser('~'))
	base_name = os.path.basename(short_path)

	print('\n\n')
	print('Add or set the remote url:')
	print('\t\033[92mgit remote add %s %s@%s:%s\033[0m' % (args.origin, user, host, short_path))
	print('\t\033[92mgit remote set-url %s %s@%s:%s\033[0m' % (args.origin, user, host, short_path))
	print('\n')
	print('Clone the %s branch:' % args.branch)
	print('\t\033[92mgit clone -b %s %s@%s:%s %s-hooks\033[0m' % (args.branch, user, host, short_path, base_name))
	print('\n\n')
