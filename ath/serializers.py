from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
def check_password_validity(password):
  try:
    validate_password(password)
    return "Valid" # Password is valid
  except ValidationError as e:
    return str(e) # Get password validity case...

 
