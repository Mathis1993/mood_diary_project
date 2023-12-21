from core.utils import hash_email


def test_hash_email():
    email = "myemailaddress@mydomain.de"
    hashed_email_1 = hash_email(email)
    hashed_email_2 = hash_email(email)
    # Ensure the function is well-defined
    assert hashed_email_1 == hashed_email_2
    assert hashed_email_1 != email
    assert len(hashed_email_1) == 64
