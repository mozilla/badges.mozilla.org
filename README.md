badg.us
=======

badg.us is a badge service based on [django-badger][] and [playdoh][].

[playdoh]: https://github.com/mozilla/playdoh
[django-badger]: https://github.com/lmorchard/django-badger

Bugs and Ideas
--------------
Feel free to file them [as issues on the django-badger project][issues]!

[issues]: https://github.com/lmorchard/django-badger/issues

Development
-----------

Here's how I get it running on my MacBook:

    git clone 
    git submodule update --init --recursive
    virtualenv --no-site-packages venv
    . ./venv/bin/activate
    pip install -r requirements/compiled.txt
    pip install -r requirements/dev.txt
    # Set up a mysql database
    # Edit badgermini/settings/local.py
    ./manage.py syncdb
    ./manage.py migrate
    ./manage.py compress_assets
    ./manage.py runserver 0.0.0.0:8000

License
-------
This software is licensed under the [New BSD License][BSD]. For more
information, read the file ``LICENSE``.

[BSD]: http://creativecommons.org/licenses/BSD/
