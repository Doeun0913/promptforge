import { useState } from "react";
import PromptInput from "./components/PromptInput";
import CompressedOutput from "./components/CompressedOutput";
import TokenStats from "./components/TokenStats";
import FilterTogglePanel from "./components/FilterTogglePanel";
import PipelineVisualizer from "./components/PipelineVisualizer";
import { compressPrompt, CompressResult } from "./api/client";

export default function App() {
  const [result, setResult] = useState<CompressResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleCompress = async (prompt: string, systemPrompt: string) => {
    setLoading(true);
    try {
      const res = await compressPrompt(prompt, systemPrompt);
      setResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-forge-700 text-white py-6 shadow-lg">
        <div className="max-w-6xl mx-auto px-4">
          <h1 className="text-3xl font-bold tracking-tight">PromptForge</h1>
          <p className="mt-1 text-forge-100 text-sm">
            한국어 감정·모호어 인식 기반 의도 보존형 프롬프트 재작성 필터
          </p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8 space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <PromptInput onSubmit={handleCompress} loading={loading} />
            {result && <CompressedOutput result={result} />}
          </div>

          <div className="space-y-6">
            {result && <TokenStats stats={result.token_stats} />}
            <FilterTogglePanel />
            {result && <PipelineVisualizer logs={result.stage_logs} />}
          </div>
        </div>
      </main>
    </div>
  );
}
