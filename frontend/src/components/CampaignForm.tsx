import React, { useState } from "react";
import { createCampaign } from "../api/backend";
import { Button } from "./ui/button";

export const CampaignForm: React.FC<{ onCreated: () => void }> = ({ onCreated }) => {
  const [name, setName] = useState("");
  const [query, setQuery] = useState("");
  const [url, setUrl] = useState("");
  const [sessions, setSessions] = useState(10);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await createCampaign({ name, query, url, sessions });
    setName(""); setQuery(""); setUrl(""); setSessions(10);
    onCreated();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <input className="input" required value={name} onChange={e => setName(e.target.value)} placeholder="Campaign name" />
      <input className="input" required value={query} onChange={e => setQuery(e.target.value)} placeholder="Search query" />
      <input className="input" required value={url} onChange={e => setUrl(e.target.value)} placeholder="Target URL" />
      <input className="input" type="number" min={1} value={sessions} onChange={e => setSessions(Number(e.target.value))} placeholder="Sessions" />
      <Button type="submit">Create Campaign</Button>
    </form>
  );
};
