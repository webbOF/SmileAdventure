"""
Error message constants for the Users service.
Centralizes all error messages to eliminate duplicate string literals.
"""

# User-related errors
USER_NOT_FOUND = "User not found"
EMAIL_ALREADY_REGISTERED = "Email already registered"
PARENT_USER_NOT_FOUND = "Parent user not found"

# Child-related errors
CHILD_NOT_FOUND = "Child not found"
CHILD_ALREADY_HAS_SENSORY_PROFILE = "Child already has a sensory profile"

# Sensory profile errors
SENSORY_PROFILE_NOT_FOUND = "Sensory profile not found"
SENSORY_PROFILE_NOT_FOUND_FOR_CHILD = "Sensory profile not found for this child"

# Specialty errors
SPECIALTY_NOT_FOUND = "Specialty not found"

# Success messages
USER_DELETED_SUCCESS = "User deleted successfully"
CHILD_DELETED_SUCCESS = "Child deleted successfully"
SENSORY_PROFILE_DELETED_SUCCESS = "Sensory profile deleted successfully"
