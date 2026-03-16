import type { TokenStatsData } from "../api/client";

interface Props {
  stats: TokenStatsData;
}

export default function TokenStats({ stats }: Props) {
  const savingsPct = (stats.savings_ratio * 100).toFixed(1);

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">토큰 통계</h2>

      <div className="space-y-3">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">원본 토큰</span>
          <span className="font-mono font-medium">{stats.original_tokens}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">압축 후 토큰</span>
          <span className="font-mono font-medium text-green-600">
            {stats.compressed_tokens}
          </span>
        </div>
        <hr />
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">절감률</span>
          <span className="font-mono font-bold text-forge-600">
            {savingsPct}%
          </span>
        </div>

        <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
          <div
            className="bg-forge-600 h-2.5 rounded-full transition-all"
            style={{ width: `${Math.min(Number(savingsPct), 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
}
