# Cleans extracted text for nlp processing
import re

def cleaner(text):
    replacements = ("n, r, t, 0, b, f, a, u200b, u200c, u200d, u2028, u2029, ufeff, u00a0, u3000, u2009, u2003, u2002, u2018, u2019, u201c, u201d, u2013, u2014").split(", ")
    for replacement in replacements:
        pattern = "\\" + replacement
        if pattern not in ["\\n", "\\r", "\\f", "\\u2028", "\\u2029"]: # replace line break characters with " "
            text = re.sub(pattern, "", text)
        else: # all non-line break characters are replaced with ""
            text = re.sub(pattern, " ", text)
    return text