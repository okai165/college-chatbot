import DataPage from "../components/DataPage";

import { getAcademicCalendar } from "../services/api";

function AcademicCalendarPage() {

    return (

        <DataPage

            title="Academic Calendar"

            subtitle="Important academic dates"

            fetchFunction={getAcademicCalendar}

        />

    );

}

export default AcademicCalendarPage;