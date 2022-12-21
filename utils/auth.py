import hashlib
import os
import binascii
import jwt
import dataclasses
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

_PBKDF2_HASH_NAME = "SHA256"
_PBKDF2_ITERATIONS = 100_000
user_auth_scheme = HTTPBearer()


@dataclasses.dataclass
class AuthUtilError(Exception):
    code: str
    message: str


def generate_hashed_password(password: str) -> str:
    pbkdf2_salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac(
        _PBKDF2_HASH_NAME,  #hash_name
        password.encode("utf-8"),  #password
        pbkdf2_salt,  #salt
        _PBKDF2_ITERATIONS,  # iterations
    )
    return "%s:%s" % (
        binascii.hexlify(pbkdf2_salt).decode("utf-8"),  # sep: str | bytes
        binascii.hexlify(pw_hash).decode("utf-8"),
    )


def validate_hashed_password(password: str, hashed_password: str) -> bool:
    pbkdf2_salt_hex, pw_hash_hex = hashed_password.split(":")

    pw_challenge = hashlib.pbkdf2_hmac(
        _PBKDF2_HASH_NAME,  #hash_name
        password.encode("utf-8"),  #password
        binascii.unhexlify(pbkdf2_salt_hex),  #salt
        _PBKDF2_ITERATIONS,  # iterations
    )

    return pw_challenge == binascii.unhexlify(pw_hash_hex)


def validate_access_token(access_token: str) -> int:
    try:
        payload = jwt.decode(
            access_token, 
            "secret", 
            algorithms=["HS256"],
            issuer="fastapi-practice"
        )  # jwt 검증
    except jwt.ExpiredSignatureError:
        # 만료된 경우
        raise AuthUtilError(
            code="jwt_expired", 
            message="jwt expired please try reauthenticate"
        )
    except jwt.InvalidIssuerError:
        # 여기 토큰이 아닌 경우
        raise AuthUtilError(
            code="jwt_invalid_issuer",
            message="jwt token is not issued from this service"
        )
    except Exception:
        raise AuthUtilError(
            code="invalid_jwt",
            message="jwt is invalid"
        )

    user_id = payload.get("_id")
    if user_id is None:
        raise AuthUtilError(
            code="invalid_payload",
            message="payload is invalid",
        )
    
    return user_id

# TODO: def 만들기! parameter (user_id, role: int)
# user_id로 찾은 유저의 role과 함수 파라미터로 받은 role의 값을 비교 -> user_id의 role < 파라미터로 받은 role : 에러 발생 (에러만 내기!)

def resolve_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(user_auth_scheme)
) -> int:
    return validate_access_token(credentials.credentials)