import secrets
import string
from django.contrib.auth.models import AbstractUser
from django.db import IntegrityError, models, transaction

TAG_LENGTH = 8
TAG_ALPHABET = string.ascii_uppercase + string.digits
TAG_SAVE_ATTEMPTS = 5


def generate_tag():
    """Return a tag like '#A7K2M9QX': '#' + 8 uppercase letters/digits, containing at least one of each."""
    while True:
        body = ''.join(secrets.choice(TAG_ALPHABET) for _ in range(TAG_LENGTH))
        if any(c.isalpha() for c in body) and any(c.isdigit() for c in body):
            return '#' + body


def normalize_tag(value):
    """Accept 'a7k2m9qx', '#a7k2m9qx' or ' #A7K2M9QX ' and return '#A7K2M9QX'."""
    return '#' + str(value).strip().lstrip('#').upper()


class User(AbstractUser):
    tag = models.CharField(max_length=TAG_LENGTH + 1, unique=True, editable=False, default=generate_tag)
    display_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    bio = models.CharField(max_length=120, blank=True)
    gender = models.CharField(max_length=30, blank=True)
    # Google account id ("sub" claim) for users who sign in with Google.
    google_sub = models.CharField(max_length=255, unique=True, null=True, blank=True, editable=False)
    # Own profile picture in S3 (users/avatars.py); empty = the default character art.
    avatar_key = models.CharField(max_length=200, blank=True, editable=False)
    # Own look of the app: '' = default, or a theme the couple bought in the shop (e.g. 'pink').
    theme = models.CharField(max_length=30, blank=True)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            return super().save(*args, **kwargs)
        # Pick a tag nobody has. The unique constraint is the real guarantee: if a concurrent
        # signup takes the same tag between the check and the insert, retry with a new tag.
        for attempt in range(TAG_SAVE_ATTEMPTS):
            if User.objects.filter(tag=self.tag).exists():
                self.tag = generate_tag()
                continue
            try:
                with transaction.atomic():
                    return super().save(*args, **kwargs)
            except IntegrityError:
                if attempt == TAG_SAVE_ATTEMPTS - 1 or not User.objects.filter(tag=self.tag).exists():
                    raise  # some other constraint (e.g. username) failed
                self.tag = generate_tag()
        raise IntegrityError('Could not generate a unique user tag.')
