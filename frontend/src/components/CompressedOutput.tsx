import type { CompressResult } from "../api/client";

interface Props {
  result: CompressResult;
}

export default function CompressedOutput({ result }: Props) {
  return (
    <div className="bg-white rounded-xl shadow-sm border p-6 space-y-4">
      <h2 className="text-lg font-semibold text-gray-800">압축 결과</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-1">원본</h3>
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm whitespace-pre-wrap">
            {result.original_prompt}
          </div>
        </div>

        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-1">압축 후</h3>
          <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-sm whitespace-pre-wrap">
            {result.compressed_prompt}
          </div>
        </div>
      </div>

      {result.domain !== "unknown" && (
        <div className="text-sm text-gray-600">
          <span className="font-medium">도메인:</span>{" "}
          <span className="px-2 py-0.5 bg-forge-100 text-forge-700 rounded-full text-xs">
            {result.domain}
          </span>
        </div>
      )}

      {result.injection_detected && (
        <div className="bg-red-100 border border-red-300 text-red-800 rounded-lg p-3 text-sm font-medium">
          프롬프트 인젝션이 감지되었습니다!
        </div>
      )}
    </div>
  );
}
