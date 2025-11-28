# Cleans extracted text for nlp processing
def cleaner(text):
    replacements = [
            "\r", "\t", "\0", "\b", "\f", "\a",
            "\u200b", "\u200c", "\u200d", "\u2028", "\u2029",
            "\ufeff", "\u00a0", "\u3000", "\u2009", "\u2003", "\u2002",
            "\u2018", "\u2019", "\u201c", "\u201d", "\u2013", "\u2014"
    ]
    for replacement in replacements:
        if replacement in ["\r", "\f", "\u2028", "\u2029"]:
            text = text.replace(replacement, " ")
        else:
            text = text.replace(replacement, "")

    return text