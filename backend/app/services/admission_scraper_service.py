from scrapers.eligibility import get_eligibility
from scrapers.available_courses import get_available_courses
from scrapers.fee_structure import get_fee_structure
from scrapers.document_checklist import get_document_checklist
from scrapers.activity_schedule import get_activity_schedule

from app.db.admission_table_service import save_admission_table


def run_admission_scraper():

    try:
        print("\n========== ADMISSION SCRAPER STARTED ==========")

        admission_data = {

            "eligibility": get_eligibility(),

            "available_courses": get_available_courses(),

            "fee_structure": get_fee_structure(),

            "document_checklist": get_document_checklist(),

            "activity_schedule": get_activity_schedule()

        }


        save_admission_table(
            title="Admissions Information",
            table_data=admission_data
        )


        print("Admission data:")
        print(admission_data)

        print("========== ADMISSION SCRAPER COMPLETED ==========\n")


    except Exception as e:

        print(
            "ADMISSION SCRAPER ERROR:",
            e
        )