from invenio_accounts.testutils import create_test_user

def create_test_users(emails=None):
    """Create test users with specified emails.

    Args:
        emails (list): List of email addresses to use for test users.
            Defaults to ["test1@example.com", "test2@example.com", "test3@example.com"].

    Returns:
        list: List of created user objects.
    """
    if emails is None:
        emails = ["test1@example.com", "test2@example.com", "test3@example.com"]
    
    users = []
    for email in emails:
        users.append(create_test_user(email=email))
    
    return users
