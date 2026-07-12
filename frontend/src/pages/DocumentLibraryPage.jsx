import DataPage from "../components/DataPage";

import { getDocuments } from "../services/api";

function DocumentLibraryPage() {

    return (

        <DataPage

            title="Document Library"

            subtitle="College documents and downloads"

            fetchFunction={getDocuments}

        />

    );

}

export default DocumentLibraryPage;