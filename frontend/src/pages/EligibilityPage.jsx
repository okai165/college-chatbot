import DataPage from "../components/DataPage";
import { getEligibility } from "../services/api";

function EligibilityPage() {

    return (

        <DataPage
            title="Eligibility Criteria"
            subtitle="Eligibility requirements for admissions"
            fetchFunction={getEligibility}
        />

    );

}

export default EligibilityPage;