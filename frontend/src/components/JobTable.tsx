import React, { useEffect, useState } from "react";
import { getJobs } from "../api/backend";

type Job = {
  id: number;
  status: string;
  started_at: string | null;
  finished_at: string | null;
  log: any;
};

export const JobTable: React.FC<{ campaignId: number }> = ({ campaignId }) => {
  const [jobs, setJobs] = useState<Job[]>([]);

  useEffect(() => {
    getJobs(campaignId).then(setJobs);
  }, [campaignId]);

  return (
    <table className="w-full border mt-2">
      <thead>
        <tr className="bg-gray-200">
          <th>ID</th>
          <th>Status</th>
          <th>Started</th>
          <th>Finished</th>
        </tr>
      </thead>
      <tbody>
        {jobs.map((j) => (
          <tr key={j.id} className="border-b">
            <td className="text-center">{j.id}</td>
            <td className="text-center">{j.status}</td>
            <td className="text-center">{j.started_at ? new Date(j.started_at).toLocaleString() : ""}</td>
            <td className="text-center">{j.finished_at ? new Date(j.finished_at).toLocaleString() : ""}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};
