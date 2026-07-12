import { useEffect, useState } from "react";

import PageHeader from "./PageHeader";
import InfoCard from "./InfoCard";

function DataPage({

    title,

    subtitle,

    fetchFunction

}) {

    const [items, setItems] = useState([]);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");

    useEffect(() => {

        async function load() {

            try {

                const data = await fetchFunction();

                setItems(data);

            }

            catch (err) {

                setError("Unable to load data.");

            }

            finally {

                setLoading(false);

            }

        }

        load();

    }, [fetchFunction]);

    if (loading)
        return <h2 style={{ padding: 30 }}>Loading...</h2>;

    if (error)
        return <h2 style={{ padding: 30 }}>{error}</h2>;

    return (

        <div style={{ padding: 30 }}>

            <PageHeader

                title={title}

                subtitle={subtitle}

            />

            {

                items.length === 0 ?

                    <p>No data found.</p>

                    :

                    items.map(item => (

                        <InfoCard

                            key={item.id}

                            title={item.title}

                            summary={item.summary}

                            type={item.type}

                            date={
                                item.created_at
                                    ? new Date(item.created_at).toLocaleDateString()
                                    : item.published_date
                                        ? new Date(item.published_date).toLocaleDateString()
                                        : ""
                            }

                            url={
                                item.pdf_url ||
                                item.url
                            }

                        />

                    ))

            }

        </div>

    );

}

export default DataPage;