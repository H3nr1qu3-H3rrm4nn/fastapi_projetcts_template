import re
from urllib.parse import urlparse


def validate_max_length_factory(max_length: int):
    def validate_max_length(input_string: str):
        if input_string is not None and len(input_string) > max_length:
            raise ValueError(
                f"A entrada excedeu o limite máximo de {max_length} caracteres"
            )
        return input_string

    return validate_max_length


def validate_cpf_cnpj(number):
    if not number:
        return number

    def calculate_cpf_digits(cpf):
        for i in range(9, 11):
            value = sum((int(cpf[num]) * ((i + 1) - num) for num in range(0, i)))
            digit = ((value * 10) % 11) % 10
            if digit != int(cpf[i]):
                raise ValueError(f"CPF ou CNPJ inválido")
        return True

    def calculate_cnpj_digits(cnpj):
        weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        for i in range(12, 14):
            value = sum(int(digit) * weight for digit, weight in zip(cnpj, weights[-i:]))
            digit = 11 - (value % 11)
            digit = digit if digit < 10 else 0
            if digit != int(cnpj[i]):
                raise ValueError("CNPJ inválido")

        return True

    formatted_number = number
    number = "".join(filter(str.isdigit, number))

    if len(number) == 11 and number != number[0] * 11:
        if calculate_cpf_digits(number):
            return formatted_number
        else:
            raise ValueError(f"CPF ou CNPJ inválido")

    elif len(number) == 14 and number != number[0] * 14:
        if calculate_cnpj_digits(number):
            return formatted_number
        else:
            raise ValueError(f"CPF ou CNPJ inválido")

    raise ValueError(f"CPF ou CNPJ inválido")


def strip_special_chars(s: str):
    if not s:
        return s
    special_chars = set("<>\"'")
    return "".join(char for char in s if char not in special_chars)


def validate_url(url: str):
    if not url:
        return url
    parsed_url = urlparse(url)
    is_valid_scheme = parsed_url.scheme in ("http", "https")
    pattern = re.compile(
        r"^(?:http|https)://"  # http:// or https://
        r"[\w.-]+(\.[\w.-]+)+"  # Domain name
        r"(?::\d+)?"  # Optional port
        r"(?:/[\w.-]*)*"  # Optional path
        r"(?:\?[\w.=&%-]*)?"  # Optional query
        r"(?:#[\w/-]*)?$",  # Optional fragment, allowing / in the fragment
        re.IGNORECASE,
    )
    is_valid_domain = re.match(pattern, url) is not None

    if is_valid_scheme and is_valid_domain:
        return url
    else:
        raise ValueError("URL inválida")
