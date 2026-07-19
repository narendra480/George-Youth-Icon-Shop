import axios from "axios";

const authClient = axios.create({
  baseURL: "/api/v1/auth",
  headers: {
    "Content-Type": "application/json",
  },
});

export default authClient;
