from settings import *  # noqa

SOUTH_TESTS_MIGRATE = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
