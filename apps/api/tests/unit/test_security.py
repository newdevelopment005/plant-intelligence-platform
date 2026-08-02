from datetime import UTC, datetime, timedelta

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_password(self):
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed)

    def test_verify_wrong_password(self):
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert not verify_password("WrongPassword", hashed)

    def test_different_hashes_for_same_password(self):
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestJWT:
    def test_create_access_token(self):
        data = {"sub": "user-123", "email": "test@example.com", "role": "researcher"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token(self):
        data = {"sub": "user-123", "email": "test@example.com", "role": "researcher"}
        token = create_access_token(data)
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "researcher"
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        data = {"sub": "user-123", "email": "test@example.com", "role": "researcher"}
        token = create_refresh_token(data)
        payload = decode_token(token)
        assert payload is not None
        assert payload["type"] == "refresh"

    def test_decode_invalid_token(self):
        payload = decode_token("invalid.token.here")
        assert payload is None

    def test_decode_expired_token(self):
        data = {"sub": "user-123"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        payload = decode_token(token)
        assert payload is None

    def test_custom_expiry(self):
        data = {"sub": "user-123"}
        token = create_access_token(data, expires_delta=timedelta(hours=1))
        payload = decode_token(token)
        assert payload is not None
        exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
        assert exp > datetime.now(UTC)
