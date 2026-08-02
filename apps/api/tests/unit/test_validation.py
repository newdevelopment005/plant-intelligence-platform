import pytest

from app.core.exceptions import ValidationException
from app.modules.auth.domain.use_cases import RegisterUserUseCase


class TestPasswordValidation:
    def setup_method(self):
        self.use_case = RegisterUserUseCase(None)

    def test_valid_password(self):
        self.use_case._validate_password("TestPassword123!")

    def test_password_too_short(self):
        with pytest.raises(ValidationException):
            self.use_case._validate_password("Ab1!")

    def test_password_no_uppercase(self):
        with pytest.raises(ValidationException):
            self.use_case._validate_password("testpassword1!")

    def test_password_no_lowercase(self):
        with pytest.raises(ValidationException):
            self.use_case._validate_password("TESTPASSWORD1!")

    def test_password_no_digit(self):
        with pytest.raises(ValidationException):
            self.use_case._validate_password("TestPassword!")

    def test_password_no_special_char(self):
        with pytest.raises(ValidationException):
            self.use_case._validate_password("TestPassword123")

    def test_password_empty(self):
        with pytest.raises(ValidationException):
            self.use_case._validate_password("")


class TestEmailValidation:
    def setup_method(self):
        self.use_case = RegisterUserUseCase(None)

    def test_valid_email(self):
        self.use_case._validate_email("test@example.com")

    def test_email_with_plus(self):
        self.use_case._validate_email("test+tag@example.com")

    def test_email_with_dots(self):
        self.use_case._validate_email("first.last@example.com")

    def test_invalid_email_no_at(self):
        with pytest.raises(ValidationException):
            self.use_case._validate_email("testexample.com")

    def test_invalid_email_no_domain(self):
        with pytest.raises(ValidationException):
            self.use_case._validate_email("test@")

    def test_empty_email(self):
        with pytest.raises(ValidationException):
            self.use_case._validate_email("")

    def test_whitespace_email(self):
        with pytest.raises(ValidationException):
            self.use_case._validate_email("   ")


class TestNameValidation:
    def setup_method(self):
        self.use_case = RegisterUserUseCase(None)

    def test_valid_name(self):
        self.use_case._validate_name("John Doe")

    def test_name_too_short(self):
        with pytest.raises(ValidationException):
            self.use_case._validate_name("J")

    def test_empty_name(self):
        with pytest.raises(ValidationException):
            self.use_case._validate_name("")

    def test_whitespace_name(self):
        with pytest.raises(ValidationException):
            self.use_case._validate_name("   ")
