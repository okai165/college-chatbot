def classify_notice(title, text):
    combined = (title + " " + text[:3000]).lower()

    def match(keywords):
        return any(k in combined for k in keywords)

    # =====================================================
    # STRICT HIGH PRIORITY (must override everything)
    # =====================================================
    if match(["nirf", "national institutional ranking"]):
        return "nirf"

    if match(["iqac", "internal quality assurance"]):
        return "iqac"

    if match(["anti ragging", "grievance cell", "complaint"]):
        return "grievance"

    if match(["hostel accommodation", "hostel admission"]):
        return "hostel"

    if match(["fee structure", "course-wise fee", "fee schedule"]):
        return "fee"

    # =====================================================
    # EXAMINATION (high confidence)
    # =====================================================
    if match([
        "datesheet",
        "date sheet",
        "revaluation",
        "result notification",
        "examination schedule"
    ]):
        return "examination"

    # =====================================================
    # SCHOLARSHIP
    # =====================================================
    if match([
        "scholarship",
        "financial assistance",
        "post matric",
        "pm scholarship"
    ]):
        return "scholarship"

    # =====================================================
    # ADMISSION (ONLY IF STRONG SIGNAL)
    # =====================================================
    if match([
        "spot round",
        "merit list",
        "counselling",
        "fyugp",
        "admission notification",
        "selection list",
        "commencement of classwork"
    ]):
        return "admission"

    # =====================================================
    # LIBRARY
    # =====================================================
    if match(["e-library", "digital library", "library rules"]):
        return "library"

    # =====================================================
    # RESEARCH / INNOVATION / ENTREPRENEURSHIP
    # =====================================================
    if match(["central research laboratory", "publication", "laboratory"]):
        return "research"

    if match(["innovation centre", "incubation", "startup"]):
        return "innovation"

    if match(["entrepreneurship cell", "startup cell"]):
        return "entrepreneurship"

    if match(["ncc", "national cadet corps"]):
        return "ncc"

    # =====================================================
    # FINAL FALLBACK
    # =====================================================
    return "notice"