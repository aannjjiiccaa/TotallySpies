import axios from "axios";

const API_URL = "http://localhost:8000/api";

export async function loginUser(data: { email: string; password: string }) {
  const res = await axios.post(`${API_URL}/login`, data);
  return res.data;
}

export async function registerUser(data: { email: string; password: string; username: string }) {
  const res = await axios.post(`${API_URL}/register`, data);
  return res.data;
}
