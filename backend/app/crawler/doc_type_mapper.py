def map_doc_type(url: str, title: str, content: str = "") -> str:

    text = f"{url} {title} {content[:2000]}".lower()

    # Admission
    if any(x in text for x in [
        "admission",
        "selection list",
        "merit list",
        "spot round",
        "fyugp",
        "eligibility"
    ]):
        return "admission"

    # Fee
    if any(x in text for x in [
        "fee structure",
        "college fee",
        "course-wise fee",
        "university fee",
        "fee schedule"
    ]):
        return "fee"

    # Scholarship
    if any(x in text for x in [
        "scholarship",
        "financial assistance"
    ]):
        return "scholarship"

    # Examination
    if any(x in text for x in [
        "module.php?id=53",
        "examination",
        "exam",
        "datesheet",
        "date sheet",
        "revaluation",
        "result"
    ]):
        return "examination"

    # Library
    if "library" in text:
        return "library"

    # Research
    if any(x in text for x in [
        "research",
        "laboratory"
    ]):
        return "research"

    # Innovation
    if any(x in text for x in [
        "innovation",
        "incubation"
    ]):
        return "innovation"

    # Entrepreneurship
    if "entrepreneurship" in text:
        return "entrepreneurship"

    # Hostel
    if "hostel" in text:
        return "hostel"

    # Grievance
    if any(x in text for x in [
        "grievance",
        "complaint"
    ]):
        return "grievance"

    # NCC
    if "ncc" in text:
        return "ncc"

    # IQAC
    if "iqac" in text:
        return "iqac"

    # NIRF
    if "nirf" in text:
        return "nirf"

    # Student Corner
    if "student corner" in text:
        return "student_corner"

    # Syllabus
    if "syllabus" in text:
        return "syllabus"

    # About
    if "about us" in text:
        return "about"

    # Public Disclosure
    if "public disclosure" in text:
        return "disclosure"

    return "notice"