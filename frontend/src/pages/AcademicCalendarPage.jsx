import { useEffect, useState } from "react";
import { getAcademicCalendar } from "../services/api";


function AcademicCalendarPage() {

    const [calendar, setCalendar] = useState([]);
    const [loading, setLoading] = useState(true);


    useEffect(() => {

        const fetchCalendar = async () => {

            try {

                const data = await getAcademicCalendar();
                setCalendar(data);

            } catch (error) {

                console.error(
                    "Calendar loading error:",
                    error
                );

            } finally {

                setLoading(false);

            }

        };


        fetchCalendar();

    }, []);



    if (loading) {
        return (
            <div className="page-container">
                <h2>Loading...</h2>
            </div>
        );
    }


    return (

        <div className="page-container">


            <button onClick={() => window.history.back()}>
                ← Back
            </button>


            <h1>
                Academic Calendar
            </h1>


            <p>
                Latest academic schedule and important dates
            </p>



            {
                calendar.map((item,index)=>(


                    <div 
                        className="data-card"
                        key={index}
                    >

                        <h2>
                            {item.content.match(/Session\s+\d{4}[-–]\d{2}/)?.[0] 
                                || "Academic Calendar"}
                        </h2>


                        <p style={{ whiteSpace: "pre-line" }}>
                        {
                            item.content
                                .replace(/TITLE:.*?\n/g, "")
                                .replace(/SOURCE:.*?\n/g, "")
                                .replace(/CHUNK:.*?\n/g, "")
                                .replace(/CONTENT:/g, "")
                                .replace(/https?:\/\/\S+/g, "")
                                .replace(/\d+\/\d+/g, "")
                                .replace(/ACADEMIC CALENDAR \(chunk 1\)/gi, "")
                                .trim()
                        }
                        </p>

                        {
                            item.url && (

                                <a
                                    href={item.url}
                                    target="_blank"
                                    rel="noreferrer"
                                >
                                    View PDF
                                </a>

                            )
                        }


                    </div>


                ))
            }


        </div>

    );

}


export default AcademicCalendarPage;