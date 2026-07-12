import DataPage from "../components/DataPage";
import { getLatestNotices } from "../services/api";

function LatestNoticesPage() {

    return (

        <DataPage
            title="Latest Notices"
            subtitle="Recent notices published by the college"
            fetchFunction={getLatestNotices}
        />

    );

}

export default LatestNoticesPage;