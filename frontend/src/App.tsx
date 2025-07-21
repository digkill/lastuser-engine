import React, { useState } from "react";
import { Dashboard } from "./pages/Dashboard";
import { JobsPage } from "./pages/JobsPage";
import { Button } from "./components/ui/button";

const App: React.FC = () => {
  const [section, setSection] = useState<"dashboard" | "jobs">("dashboard");

  return (
    <div className="min-h-screen bg-muted text-base">
      <div className="flex gap-2 p-4 border-b">
        <Button variant={section === "dashboard" ? "default" : "outline"} onClick={() => setSection("dashboard")}>
          📊 Кампании
        </Button>
        <Button variant={section === "jobs" ? "default" : "outline"} onClick={() => setSection("jobs")}>
          🛠️ Все задачи
        </Button>
      </div>
      {section === "dashboard" && <Dashboard />}
      {section === "jobs" && <JobsPage />}
    </div>
  );
};

export default App;
