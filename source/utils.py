def check_if_term_is_valid(term):
    return f"{'[' + term.law.is_valid + ']' if term.law.is_valid != 'чинний' else ''}"
