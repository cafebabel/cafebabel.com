from flask_security.forms import LoginForm
from flask_security.utils import (_datastore, _pwd_context, get_message,
                                  use_double_hash, hash_password, get_hmac)
from flask_security.confirmable import requires_confirmation


def verify_and_update_password(password, user):
    """
    Copy-pasted function from flask_security and disable double_hash for
    Django passwords.
    """
    if (use_double_hash(user.password)
            and not user.password.startswith('pbkdf2_sha256')):
        verified = _pwd_context.verify(get_hmac(password), user.password)
    else:
        # Try with original password.
        verified = _pwd_context.verify(password, user.password)
    if verified and _pwd_context.needs_update(user.password):
        user.password = hash_password(password)
        _datastore.put(user)
    return verified


class MultipleHashLoginForm(LoginForm):
    def validate(self):
        """
        Copy-pasted from flask_security and use the altered version of
        `verify_and_update_password`.
        """
        if not super(LoginForm, self).validate():
            return False

        self.user = _datastore.get_user(self.email.data)

        if self.user is None:
            self.email.errors.append(get_message('USER_DOES_NOT_EXIST')[0])
            return False
        if not self.user.password:
            self.password.errors.append(get_message('PASSWORD_NOT_SET')[0])
            return False
        if not verify_and_update_password(self.password.data, self.user):
            self.password.errors.append(get_message('INVALID_PASSWORD')[0])
            return False
        if requires_confirmation(self.user):
            self.email.errors.append(get_message('CONFIRMATION_REQUIRED')[0])
            return False
        if not self.user.is_active:
            self.email.errors.append(get_message('DISABLED_ACCOUNT')[0])
            return False
        return True
