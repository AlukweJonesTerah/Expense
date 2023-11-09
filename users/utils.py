from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type # compactbility

class AppTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        # return (str(user.is_active)+str(user.pk)+str(timestamp))
        return (text_type(user.is_active)+text_type(user.pk)+text_type(timestamp))

account_activation_token=AppTokenGenerator()