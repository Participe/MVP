# Override settings here

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
    ('Artem Suvorov', 'artem.suvorov@gmail.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'participe',                      # Or path to database file if using sqlite3.
        'USER': 'copycat',                      # Not used with sqlite3.
        'PASSWORD': '123',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = 'participe.mvp'
EMAIL_HOST_PASSWORD= 'PaRtIcIpE123'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
