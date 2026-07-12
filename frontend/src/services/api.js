import axios from "axios";

const api = axios.create({

    baseURL: "http://127.0.0.1:8000",

});
// --------------------
// Admission Updates
// --------------------

export async function getAdmissionUpdates() {

    const { data } =
        await api.get("/admission-updates");

    return data;

}
// fee
export async function getFeeStructure() {

    const { data } = await api.get("/fee-structure");

    return data;

}
//   available courses
export async function getAvailableCourses(){

    const {data} = await api.get("/available-courses");

    return data;

}
// --------------------
// Notices
// --------------------

export async function getLatestNotices() {

    const { data } =
        await api.get("/notices/latest");

    return data;

}

// --------------------
// Academic Calendar
// --------------------

export async function getAcademicCalendar() {

    const { data } =
        await api.get("/academic-calendar");

    return data;

}

// --------------------
// Document Library
// --------------------

export async function getDocuments() {

    const { data } =
        await api.get("/documents");

    return data;

}

// --------------------
// Events
// --------------------

export async function getEvents() {

    const { data } =
        await api.get("/events");

    return data;

}

export default api;