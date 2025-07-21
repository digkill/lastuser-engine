// src/types.ts

export type JobInfo = {
  id: number;
  campaign_id: number;
  status: string;
  started_at?: string | null;
  finished_at?: string | null;
  updated_at?: string | null;
  // другие поля, если есть
};
