def base_n_encode(num, base, alphabet=None):
    """Encode a number in an arbitrary base

    `num`: Non-negative number to encode
    `base`: Base to encode to, >= 2
    `alphabet`: The alphabet to use for encoding
    """
    if alphabet is None:
        alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    if num < 0:
        raise ValueError('num must be >= 0')

    if base > len(alphabet):
        raise ValueError('alphabet not big enough for this base')

    if (num == 0):
        return alphabet[0]
    arr = []
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


def base_n_decode(num, base, alphabet=None):
    """Decode a number from an arbitrary base to base 10

    `num`: Non-negative number to decode
    `base`: Base to decode from, >= 2
    `alphabet`: The alphabet to use for encoding
    """
    if alphabet is None:
        alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    if base > len(alphabet):
        raise ValueError('alphabet not big enough for this base')

    val = 0
    for position, digit in enumerate(num):
        base_ten_digit = alphabet.index(digit)
        power = len(num) - position - 1
        val += base_ten_digit * base**power

    return val
