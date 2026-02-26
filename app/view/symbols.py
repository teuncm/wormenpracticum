# Uppercase delta symbol
U_DELTA = "\u0394"


# Symbol translation function
def translate_symbols(text):
    return text.replace("DELTA_", U_DELTA)
