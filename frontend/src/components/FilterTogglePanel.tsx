import { useEffect, useState } from "react";
import { getPipelineStatus, toggleStage } from "../api/client";

interface StageInfo {
  name: string;
  enabled: boolean;
}

export default function FilterTogglePanel() {
  const [stages, setStages] = useState<Record<string, StageInfo>>({});

  useEffect(() => {
    getPipelineStatus()
      .then(setStages)
      .catch(console.error);
  }, []);

  const handleToggle = async (id: string, enabled: boolean) => {
    await toggleStage(id, !enabled);
    setStages((prev) => ({
      ...prev,
      [id]: { ...prev[id], enabled: !enabled },
    }));
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">
        필터 토글
      </h2>
      <div className="space-y-2 max-h-80 overflow-y-auto">
        {Object.entries(stages).map(([id, info]) => (
          <label
            key={id}
            className="flex items-center justify-between py-1 cursor-pointer"
          >
            <span className="text-xs text-gray-700 truncate pr-2">
              {info.name}
            </span>
            <input
              type="checkbox"
              checked={info.enabled}
              onChange={() => handleToggle(id, info.enabled)}
              className="h-4 w-4 text-forge-600 rounded"
            />
          </label>
        ))}
      </div>
    </div>
  );
}
