import React, { useState } from "react";
import { CampaignList } from "../components/CampaignList";
import { CampaignForm } from "../components/CampaignForm";
import { JobTable } from "../components/JobTable";

export const Dashboard: React.FC = () => {
  const [selected, setSelected] = useState<any>(null);
  const [refresh, setRefresh] = useState(0);

  return (
    <div className="max-w-3xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-2">🎯 LastUser Engine — Dashboard</h1>
      <CampaignForm onCreated={() => setRefresh(r => r + 1)} />
      <hr className="my-4" />
      <CampaignList key={refresh} onSelect={setSelected} />
      {selected && (
        <div className="mt-8">
          <h2 className="text-xl mb-2">{selected.name} — Jobs</h2>
          <JobTable campaignId={selected.id} />
        </div>
      )}
    </div>
  );
};
