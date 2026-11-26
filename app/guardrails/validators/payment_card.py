
import re


def luhn_valid(value: str) -> bool:

    digits = re.sub(r"\D", "", value)

    if not 13 <= len(digits) <= 19:
        return False

    total = 0

    for index, digit in enumerate(
        reversed(digits)
    ):

        number = int(digit)

        if index % 2 == 1:
            number *= 2

            if number > 9:
                number -= 9

        total += number

    return total % 10 == 0


def validate_payment_card(value: str) -> bool:

    return luhn_valid(value)
