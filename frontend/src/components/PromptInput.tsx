import { useState } from "react";

interface Props {
  onSubmit: (prompt: string, systemPrompt: string) => void;
  loading: boolean;
}

export default function PromptInput({ onSubmit, loading }: Props) {
  const [prompt, setPrompt] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [showSystem, setShowSystem] = useState(false);

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6 space-y-4">
      <h2 className="text-lg font-semibold text-gray-800">
        프롬프트 입력
      </h2>

      {showSystem && (
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">
            System Prompt
          </label>
          <textarea
            className="w-full border rounded-lg p-3 text-sm resize-y min-h-[60px] focus:ring-2 focus:ring-forge-500 focus:border-transparent"
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            placeholder="시스템 프롬프트 (선택)"
          />
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">
          User Prompt
        </label>
        <textarea
          className="w-full border rounded-lg p-3 text-sm resize-y min-h-[120px] focus:ring-2 focus:ring-forge-500 focus:border-transparent"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder='예: "하 진짜 이거 왜 이렇게 어렵냐 ㅠ 좀 쉽게 설명해줘"'
        />
      </div>

      <div className="flex items-center justify-between">
        <button
          className="text-sm text-forge-600 hover:underline"
          onClick={() => setShowSystem(!showSystem)}
        >
          {showSystem ? "System Prompt 숨기기" : "System Prompt 추가"}
        </button>

        <button
          className="px-6 py-2 bg-forge-600 text-white rounded-lg font-medium hover:bg-forge-700 disabled:opacity-50 transition-colors"
          onClick={() => onSubmit(prompt, systemPrompt)}
          disabled={loading || !prompt.trim()}
        >
          {loading ? "압축 중..." : "압축하기"}
        </button>
      </div>
    </div>
  );
}
