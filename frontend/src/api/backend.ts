import axios from "axios";
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001/api";

export const getCampaigns = async () => {
  const res = await axios.get(`${API_URL}/campaigns/`);
  return res.data;
};

export const createCampaign = async (data: never) => {
  const res = await axios.post(`${API_URL}/campaigns/`, data);
  return res.data;
};

export const getJobs = async (campaignId: number) => {
  const res = await axios.get(`${API_URL}/jobs/`, { params: { campaign_id: campaignId } });
  return res.data;
};

export interface RunJobResponse {
  status: string;
  message?: string;
  job?: never; // заменить на Job если надо
}

export async function runJob(jobId: number): Promise<RunJobResponse> {
  const res = await fetch(`${API_URL}/jobs/${jobId}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Ошибка запуска job: ${text}`);
  }
  return res.json();
}
