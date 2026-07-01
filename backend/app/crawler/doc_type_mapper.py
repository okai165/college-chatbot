def map_doc_type(url: str, title: str) -> str:
    """Return a meaningful doc_type based on URL or page title."""
    lower_url = url.lower()
    lower_title = title.lower()

    if "module.php?id=53" in lower_url or "examination" in lower_title:
        return "examination"
    if "grievances" in lower_url or "grievance" in lower_title or "complaint" in lower_title:
        return "grievance"
    if "library" in lower_url:
        return "library"
    if "hostel" in lower_url:
        return "hostel"
    if "innovation" in lower_url or "incubation" in lower_title:
        return "innovation"
    if "scholarship" in lower_url:
        return "scholarship"
    if "iqac" in lower_url:
        return "iqac"
    if "nirf" in lower_url:
        return "nirf"
    if "ncc" in lower_url:
        return "ncc"
    if "entrepreneurship" in lower_url:
        return "entrepreneurship"

    # fallback
    return "notice"