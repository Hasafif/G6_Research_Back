from django.contrib.auth.models import AbstractUser
from django.db import models
""""
class customuser(AbstractUser):
    # Django's built-in User model already includes fields for username and email.
    # The password field is managed by Django's authentication system.
    # The date_joined field is also automatically managed by Django's User model.
    
    # Additional fields
    confirmed = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, null=True, blank=True)
    
    # Override the __str__ method to return the username
    def __str__(self):
        return self.username
"""