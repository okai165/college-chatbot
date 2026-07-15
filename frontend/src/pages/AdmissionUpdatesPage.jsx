import { useNavigate } from "react-router-dom";
import DataPage from "../components/DataPage";
import { getAdmissionUpdates } from "../services/api";

function AdmissionUpdatesPage() {
    const navigate = useNavigate();

    return (
        <>
            <button
                className="back-btn"
                onClick={() => navigate(-1)}
            >
                ← Back
            </button>

            <DataPage
                // title="Notices"
                fetchFunction={getAdmissionUpdates}
            />
        </>
    );
}

export default AdmissionUpdatesPage;