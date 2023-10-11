import sys
import hmac
import time
import struct
import base64

ALGORITHM = "SHA512"
DIGITS = 10
STEP = 30


def totp(K):
    steps = int(time.time()) // STEP
    C = struct.pack(">Q", steps)
    assert len(C) == 8
    assert isinstance(C, bytes)
    data = hmac.HMAC(K, C, ALGORITHM).digest()
    # import binascii
    # data = binascii.a2b_hex("|1f|86|98|69|0e|02|ca|16|61|85|50|ef|7f|19|da|8e|94|5b|55|5a".replace("|", ""))
    offset = data[-1] & 0xf
    four = data[offset:offset + 4]
    value = struct.unpack(">I", four)[0] & (2 ** 31 - 1)
    print(data, offset, four, C, value)
    return value % (10 ** DIGITS)


def test_totp_vectors():
    from unittest.mock import patch
    K = b"1234567890123456789012345678901234567890123456789012345678901234"
    with patch("time.time", return_value=59), \
            patch("totp.DIGITS", 8):
        assert totp(K) == 90693936

    with patch("time.time", return_value=2000000000), \
            patch("totp.DIGITS", 8):
        assert totp(K) == 38618901


def test_hde_example():
    theirs = b"bmluamFAZXhhbXBsZS5jb206MTc3MzEzMzI1MA=="
    tdec = base64.decodebytes(theirs)
    assert tdec == b"ninja@example.com:1773133250"
    mine = custom("ninja@example.com")
    assert len(mine) == len(theirs)
    dec = base64.decodebytes(mine.encode("utf-8"))
    tl, tr = tdec.split(b":")
    ml, mr = dec.split(b":")
    assert tr.isdigit()
    assert mr.isdigit()
    assert tl == ml


def custom(email):
    secret = ("%s%s" % (sys.argv[1], "HENNGECHALLENGE003")).encode("utf-8")
    tmp = "%s:%s" % (email, str(totp(secret)).rjust(DIGITS, "0"))
    return base64.encodebytes(tmp.encode("utf-8")).decode("utf-8").strip()


def token():
    email = "dimaqq@gmail.com"
    secret = ("%s%s" % (email, "HENNGECHALLENGE003")).encode("utf-8")
    tmp = "%s:%s" % (email, str(totp(secret)).rjust(DIGITS, "0"))
    return base64.encodebytes(tmp.encode("utf-8")).decode("utf-8").strip()


def test_token():
    assert token()


if __name__ == "__main__":
    assert len(sys.argv) > 1, "Usage: %s <email>" % sys.argv[0]
    print(custom(sys.argv[1]))
