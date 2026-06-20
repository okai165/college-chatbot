def classify_notice(title, text):

    combined = (
        title + " " + text[:1000]
    ).lower()

    scholarship_keywords = [
        "scholarship",
        "financial assistance"
    ]

    fee_keywords = [
        "fee structure",
        "college fee",
        "course-wise fee",
        "university fee"
    ]

    admission_keywords = [
        "admission",
        "selection list",
        "merit list",
        "counselling",
        "fyugp"
    ]

    if any(
        keyword in combined
        for keyword in scholarship_keywords
    ):
        return "scholarship"

    if any(
        keyword in combined
        for keyword in fee_keywords
    ):
        return "fee"

    if any(
        keyword in combined
        for keyword in admission_keywords
    ):
        return "admission"

    return "notice"