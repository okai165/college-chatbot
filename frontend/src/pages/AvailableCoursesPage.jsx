import { useEffect, useState } from "react";
import { getAvailableCourses } from "../services/api";


function AvailableCoursesPage(){

    const [courses,setCourses] = useState([]);


    useEffect(()=>{

        getAvailableCourses()
        .then(data=>{
            setCourses(data);
        });

    },[]);



    return (

        <div className="page-container">

            <button onClick={()=>window.history.back()}>
                ← Back
            </button>


            <h1>
                Available Courses
            </h1>


            <table border="1">

                <thead>

                    <tr>
                        <th>S.No</th>
                        <th>Course Name</th>
                        <th>Course Type</th>
                        <th>Eligibility</th>
                    </tr>

                </thead>


                <tbody>

                {
                    courses.map((course,index)=>(

                        <tr key={index}>

                            <td>{course.sno}</td>

                            <td>{course.name}</td>

                            <td>{course.type}</td>

                            <td>{course.eligibility}</td>

                        </tr>

                    ))
                }

                </tbody>

            </table>


        </div>

    )

}


export default AvailableCoursesPage;