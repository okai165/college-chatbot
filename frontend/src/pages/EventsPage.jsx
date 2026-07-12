import DataPage from "../components/DataPage";

import { getEvents } from "../services/api";

function EventsPage() {

    return (

        <DataPage

            title="Events & Workshops"

            subtitle="Upcoming events"

            fetchFunction={getEvents}

        />

    );

}

export default EventsPage;