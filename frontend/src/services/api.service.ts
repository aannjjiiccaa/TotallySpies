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

export async function getGraph() {
  const res = await axios.get(`${API_URL}/graph`);
  return res.data;
}

export async function getSumarry() {
  const res = await axios.get(`http://localhost:8000/api/summary`);
  return res.data; 
}

export async function getKeyPoints() {
  const res = await axios.post(`http://localhost:8000/api/ask`, {
    question:
      "List 3-5 key points of this system as bullet points, one per line. No intro text."
  });
  return res.data.answer as string; // plain text
}

export async function getWhoUses() {
  const res = await axios.post(`http://localhost:8000/api/ask`, {
    question:
      "Who uses this system? Simple list 3-5 user groups/teams, one per line. No intro text."
  });
  return res.data.answer as string; // plain text
}