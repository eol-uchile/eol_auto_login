from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings
from eol_auto_login.views import create_auto_login

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'This command will create url to user auto login.'

    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            help='Username to generate auto-login link (default: None).',
            default=None
        )

    def handle(self, *args, **options):
        logger.info('EolAutoLoginCommand - Running create_auto_login()')
        if not options['username']:
            raise CommandError("EolAutoLoginCommand - Username must be specified")
        username = options['username']
        link = create_auto_login(username)
        if link is None:
            raise CommandError("EolAutoLoginCommand - Username {} doesnt exists".format(username))
        self.stdout.write(
            f"Auto login Url {link}"
        )
        return link

