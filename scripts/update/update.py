"""
Deploy this project in dev/stage/production.

Requires commander_ which is installed on the systems that need it.

.. _commander: https://github.com/oremj/commander
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from commander.deploy import task, hostgroups
import commander_settings as settings


# Setup virtualenv path.
venv_bin_path = os.path.join(settings.SRC_DIR, 'virtualenv', 'bin')
os.environ['PATH'] = venv_bin_path + os.pathsep + os.environ['PATH']
os.environ['DJANGO_SETTINGS_MODULE'] = 'badgus.settings'


@task
def update_code(ctx, tag):
    """Update the code to a specific git reference (tag/sha/etc)."""
    with ctx.lcd(settings.SRC_DIR):
        ctx.local('git fetch')
        ctx.local('git checkout -f %s' % tag)
        ctx.local('git submodule sync')
        ctx.local('git submodule update --init --recursive')


@task
def update_info(ctx):
    """Write info about the current state to a publicly visible file."""
    with ctx.lcd(settings.SRC_DIR):
        ctx.local('date')
        ctx.local('git branch -a')
        ctx.local('git log -3')
        ctx.local('git status')
        ctx.local('git submodule status')
        ctx.local('git rev-parse HEAD > media/revision.txt')


# TODO: update_locales


@task
def setup_dependencies(ctx):
    with ctx.lcd(settings.SRC_DIR):
        # TODO: only delete & recreate virtualenv when needed
        # Maybe stash the md5 of requirements files between deploys, only
        # rebuild virtualenv on mismatch?
        ctx.local('rm -rf virtualenv')
        ctx.local('virtualenv --no-site-packages virtualenv')

        # Activate virtualenv to append to path.
        activate_env = os.path.join(settings.SRC_DIR, 'virtualenv', 'bin', 'activate_this.py')
        execfile(activate_env, dict(__file__=activate_env))
        ctx.local('python --version')
        ctx.local('python scripts/peep.py install -r requirements/prod.txt')
        ctx.local('virtualenv --relocatable virtualenv')

        # Fix lib64 symlink to be relative instead of absolute.
        ctx.local('rm -f virtualenv/lib64')
        with ctx.lcd('virtualenv'):
            ctx.local('ln -s lib lib64')


@task
def update_db(ctx):
    with ctx.lcd(settings.SRC_DIR):
        ctx.local("python manage.py syncdb --noinput")
        # HACK: Skip djcelery migrations. Tables already there... somehow?
        # ctx.local('python manage.py migrate djcelery --fake --noinput')
        # ctx.local('python manage.py migrate --noinput')
        # ctx.local('python manage.py migrate --list')


@task
def update_assets(ctx):
    with ctx.lcd(settings.SRC_DIR):
        ctx.local("python manage.py collectstatic --noinput")


@task
def clean(ctx):
    """Clean .gitignore and .pyc files."""
    with ctx.lcd(settings.SRC_DIR):
        ctx.local("find . -type f -name '.gitignore' -or -name '*.pyc' -delete")


@task
def checkin_changes(ctx):
    """Use the local, IT-written deploy script to check in changes."""
    ctx.local(settings.DEPLOY_SCRIPT)


@hostgroups(settings.WEB_HOSTGROUP, remote_kwargs={'ssh_key': settings.SSH_KEY})
def deploy_app(ctx):
    """Call the remote update script to push changes to webheads."""
    ctx.remote('touch %s' % settings.REMOTE_WSGI)


# https://github.com/mozilla/chief/blob/master/chief.py#L48


@task
def pre_update(ctx, ref=settings.UPDATE_REF):
    """1. Update code to pick up changes to this file."""
    update_code(ref)
    setup_dependencies()
    update_info()
    clean()


@task
def update(ctx):
    """2. Nothing to do here yet."""
    update_assets()
    update_db()


@task
def deploy(ctx):
    """3. Deploy stuff."""
    checkin_changes()
    deploy_app()
