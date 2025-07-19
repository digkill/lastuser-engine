import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export const getCampaigns = async () => {
  const res = await axios.get(`${API_URL}/campaigns/`);
  return res.data;
};

export const createCampaign = async (data: any) => {
  const res = await axios.post(`${API_URL}/campaigns/`, data);
  return res.data;
};

export const getJobs = async (campaignId: number) => {
  const res = await axios.get(`${API_URL}/jobs/`, { params: { campaign_id: campaignId } });
  return res.data;
};
