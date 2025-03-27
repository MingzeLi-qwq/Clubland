import axios from "axios";

export const api = axios.create({
    baseURL: "http://51.21.191.188:8000/api/",
    withCredentials: true,
});
