from django.core.exceptions import ValidationError
from unicodedata import digit


def validate_pesel(value):
    if len(value) != 11 or not value.isdigit():
        raise ValidationError("PESEL musi składać się z 11 cyfr.")

    weights = [1,3,7,9,1,3,7,9,1,3]

    pesel_digits = [int(digit) for digit in value]
    checksum = sum(digit * weight for digit, weight in zip(pesel_digits[:10], weights))
    last_digit = checksum % 10
    control_digit = 10 - last_digit if last_digit != 0 else 0
    if control_digit != pesel_digits[10]:
        raise ValidationError("Niepoprawny numer PESEL (bład sumy kontrolnej)")