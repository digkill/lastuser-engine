import React, { useEffect, useState } from "react";
import { getCampaigns } from "../api/backend";
import { Card, CardContent } from "./ui/card";

type Campaign = {
  id: number;
  name: string;
  query: string;
  url: string;
  sessions: number;
  created_at: string;
};

export const CampaignList: React.FC<{ onSelect: (c: Campaign) => void }> = ({ onSelect }) => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);

  useEffect(() => {
    getCampaigns().then(setCampaigns);
  }, []);

  return (
    <div className="grid grid-cols-1 gap-4">
      {campaigns.map((c) => (
        <Card key={c.id} className="hover:bg-gray-100 cursor-pointer" onClick={() => onSelect(c)}>
          <CardContent>
            <div className="flex justify-between items-center">
              <div>
                <div className="font-semibold text-xl">{c.name}</div>
                <div className="text-sm text-gray-500">{c.query}</div>
                <div className="text-xs text-gray-400">{c.url}</div>
              </div>
              <div className="text-xs text-gray-500">Sessions: {c.sessions}</div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};
