import base64
import farmhash

NUMBER_SIZE_BYTES = 8
BYTE_ORDER = 'big'

def fast_hash(input_str):
    number = farmhash.hash128(input_str)
    result_str = number[0].to_bytes(NUMBER_SIZE_BYTES, BYTE_ORDER)
    return base64.urlsafe_b64encode(result_str).decode('utf-8')