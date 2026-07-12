import DataPage from "../components/DataPage";
import { getAdmissionUpdates } from "../services/api";

function AdmissionUpdatesPage() {

    return (

        <DataPage
            title="Admission Updates"
            subtitle="Latest admission notifications published by the college"
            fetchFunction={getAdmissionUpdates}
        />

    );

}

export default AdmissionUpdatesPage;