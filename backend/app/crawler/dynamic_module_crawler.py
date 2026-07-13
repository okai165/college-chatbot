import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.gcwmaroad.edu.in"


def extract_dynamic_id(html):
    """
    Detects whether a page loads its content dynamically.

    Looks for:
        <input type="hidden" id="deptId" value="48">

    Returns:
        dept_id (str) or None
    """

    soup = BeautifulSoup(html, "html.parser")

    dept = soup.find("input", id="deptId")

    if not dept:
        return None

    return dept.get("value")


def fetch_department_profile(dept_id):
    """
    Fetches dynamic content from:

        /src/fetchDepartmentProfile.php?did=<dept_id>

    Works for:
        - Scholarship
        - Hostel
        - NCC
        - NSS
        - Library
        - Departments
        - Research pages
        - Future dynamic pages

    Returns:
        {
            "title": "...",
            "content": "..."
        }

    or None
    """

    url = f"{BASE_URL}/src/fetchDepartmentProfile.php"

    response = requests.get(
        url,
        params={"did": dept_id},
        headers={
            "User-Agent": "Mozilla/5.0",
            "X-Requested-With": "XMLHttpRequest",
        },
        timeout=20,
    )

    response.raise_for_status()

    sections = response.json()

    if not sections:
        return None

    content_parts = []

    page_title = "Department"

    for i, section in enumerate(sections):

        title = section.get("sectionTitle", "").strip()

        if i == 0 and title:
            page_title = title

        html = section.get("sectionDescription", "")

        text = BeautifulSoup(
            html,
            "html.parser"
        ).get_text(
            "\n",
            strip=True
        )

        if title:
            content_parts.append(title)

        if text:
            content_parts.append(text)

    content = "\n\n".join(content_parts).strip()

    if not content:
        return None

    return {
        "title": page_title,
        "content": content
    }


def load_dynamic_content(html):
    """
    Automatically loads AJAX content for any page that
    contains a hidden deptId.

    Usage:

        dynamic = load_dynamic_content(html)

        if dynamic:
            title = dynamic["title"]
            content = dynamic["content"]

    Returns:
        {
            "title": "...",
            "content": "..."
        }

    or None
    """

    dept_id = extract_dynamic_id(html)

    if not dept_id:
        return None

    try:

        data = fetch_department_profile(dept_id)

        if data:
            print(
                f"Loaded dynamic content for dept {dept_id} "
                f"({len(data['content'])} chars)"
            )

        return data

    except Exception as e:

        print(
            f"Dynamic fetch failed for dept {dept_id}: {e}"
        )

        return None