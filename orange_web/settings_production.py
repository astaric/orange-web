from orange_web.settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['orange.biolab.si', 'new.orange.biolab.si']
DOWNLOAD_SET_PATTERN = os.path.join('/srv/download', 'filenames_%s.set')

# Django, reCaptcha secret keys
with open('/etc/orange_web.conf', 'r') as f:
    lines = f.readlines()
    SECRET_KEY = lines[0].split('=', 1)[1]
    RECAPTCHA_SECRET = lines[1].split('=', 1)[1]

# SMTP settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.fri.uni-lj.si'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False