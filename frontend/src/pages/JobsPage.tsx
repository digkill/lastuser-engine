import React, { useEffect, useState } from "react";
import type { JobInfo } from "../types";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001/api";

// Универсальный фетчер — забирает все джобы
const fetchJobs = async (): Promise<JobInfo[]> => {
  const res = await fetch(`${API_URL}/jobs/`);
  if (!res.ok) throw new Error("Ошибка загрузки списка задач");
  return await res.json();
};

export const JobsPage: React.FC = () => {
  const [jobs, setJobs] = useState<JobInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadJobs = async () => {
    setLoading(true);
    setError(null);
    try {
      setJobs(await fetchJobs());
    } catch (e) {
      setError("Ошибка загрузки задач");
    }
    setLoading(false);
  };

  useEffect(() => {
    loadJobs();
  }, []);

  return (
    <div className="max-w-3xl mx-auto p-4">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">🛠️ Все задачи (Jobs)</h1>
        <Button onClick={loadJobs} disabled={loading}>
          {loading ? "Обновление..." : "Обновить"}
        </Button>
      </div>
      {error && <div className="text-red-500">{error}</div>}
      <JobTable jobs={jobs} onJobRun={loadJobs} />
    </div>
  );
};

// Отдельный компонент для таблицы
type JobTableProps = {
  jobs: JobInfo[];
  onJobRun?: () => void;
};

const statusColors: Record<string, string> = {
  new: "bg-blue-100 text-blue-700",
  running: "bg-yellow-100 text-yellow-800",
  done: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
};

export const JobTable: React.FC<JobTableProps> = ({ jobs, onJobRun }) => {
  if (!jobs.length) return <div className="text-gray-500">Нет задач.</div>;
  return (
    <Card>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="p-2 text-left">ID</th>
                <th className="p-2 text-left">Статус</th>
                <th className="p-2 text-left">Started</th>
                <th className="p-2 text-left">Finished</th>
                <th className="p-2 text-left">Кампания</th>
                <th className="p-2"></th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((job) => (
                <tr key={job.id} className="border-b hover:bg-muted/30 transition">
                  <td className="p-2">{job.id}</td>
                  <td className="p-2">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${statusColors[job.status] || ""}`}>
                      {job.status}
                    </span>
                  </td>
                  <td className="p-2">{job.started_at ? new Date(job.started_at).toLocaleString() : "-"}</td>
                  <td className="p-2">{job.finished_at ? new Date(job.finished_at).toLocaleString() : "-"}</td>
                  <td className="p-2">{job.campaign_id}</td>
                  <td className="p-2">
                    {job.status === "new" && (
                      <RunJobButton jobId={job.id} onDone={onJobRun} />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};

const RunJobButton: React.FC<{ jobId: number; onDone?: () => void }> = ({ jobId, onDone }) => {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const runJob = async () => {
    setLoading(true);
    setSuccess(false);
    try {
      const res = await fetch(`${API_URL}/jobs/${jobId}/run`, { method: "POST" });
      if (res.ok) {
        setSuccess(true);
        if (onDone) onDone();
      }
    } catch {}
    setLoading(false);
  };

  return (
    <Button
      size="sm"
      onClick={runJob}
      disabled={loading || success}
      className={success ? "bg-green-500 hover:bg-green-600" : ""}
    >
      {success ? "✅ Запущено" : loading ? "..." : "▶️ Запустить"}
    </Button>
  );
};
