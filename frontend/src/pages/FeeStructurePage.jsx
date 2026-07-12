import { useEffect, useState } from "react";
import { getFeeStructure } from "../services/api";

function FeeStructurePage() {

    const [fees, setFees] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {

        const fetchFees = async () => {

            try {

                const data = await getFeeStructure();
                setFees(data);

            } catch (error) {

                console.error("Fee loading error:", error);

            } finally {

                setLoading(false);

            }

        };

        fetchFees();

    }, []);


    if (loading) {
        return (
            <div className="page-container">
                <h2>Loading...</h2>
            </div>
        );
    }


    const extractRows = (content) => {

        const cleaned = content
            .replace(/TITLE:.*?\n/g, "")
            .replace(/SOURCE:.*?\n/g, "")
            .replace(/CHUNK:.*?\n/g, "")
            .replace(/CONTENT:/g, "")
            .replace(/\n/g, " ")
            .trim();


        const rows = [];


        const regex =
            /(\d+)\s+([A-Za-z&\s().-]+?)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)/g;


        let match;


        while ((match = regex.exec(cleaned)) !== null) {

            rows.push({

                sno: match[1],
                course: match[2].trim(),
                collegeFee: match[3],
                secFee: match[4],
                universityFee: match[5],
                totalFee: match[6]

            });

        }


        return rows;

    };


    const rows = extractRows(
        fees[0]?.content || ""
    );


    console.log("Extracted fee rows:", rows);


    return (

        <div className="page-container">

            <button onClick={() => window.history.back()}>
                ← Back
            </button>


            <h1>
                Fee Structure
            </h1>


            <p>
                Details of college fees, charges, and related fee information
            </p>


            {
                rows.length === 0 ? (

                    <p>
                        No fee data available.
                    </p>

                ) : (

                    <table border="1">

                        <thead>

                            <tr>
                                <th>S.No</th>
                                <th>Course Name</th>
                                <th>College Fee</th>
                                <th>SEC Fee</th>
                                <th>University Fee</th>
                                <th>Total Fee</th>
                            </tr>

                        </thead>


                        <tbody>

                            {
                                rows.map((row, index) => (

                                    <tr key={index}>

                                        <td>{row.sno}</td>

                                        <td>{row.course}</td>

                                        <td>{row.collegeFee}</td>

                                        <td>{row.secFee}</td>

                                        <td>{row.universityFee}</td>

                                        <td>{row.totalFee}</td>

                                    </tr>

                                ))
                            }

                        </tbody>

                    </table>

                )
            }


        </div>

    );

}


export default FeeStructurePage;