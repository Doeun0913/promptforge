import type { StageLog } from "../api/client";

interface Props {
  logs: StageLog[];
}

export default function PipelineVisualizer({ logs }: Props) {
  if (logs.length === 0) return null;

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">
        파이프라인 실행
      </h2>
      <div className="space-y-2">
        {logs.map((log, i) => (
          <div
            key={i}
            className={`flex items-center justify-between text-xs py-1.5 px-2 rounded ${
              log.skipped
                ? "bg-gray-50 text-gray-400"
                : "bg-forge-50 text-gray-700"
            }`}
          >
            <span className="font-mono truncate">{log.stage_id}</span>
            <div className="flex items-center gap-2">
              {!log.skipped && (
                <span className="text-gray-400">
                  {log.elapsed_ms.toFixed(0)}ms
                </span>
              )}
              <span
                className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${
                  log.skipped
                    ? "bg-gray-200 text-gray-500"
                    : log.gate_decision === "rejected"
                      ? "bg-red-100 text-red-600"
                      : "bg-green-100 text-green-600"
                }`}
              >
                {log.skipped
                  ? "SKIP"
                  : log.gate_decision ?? `${(log.confidence * 100).toFixed(0)}%`}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
