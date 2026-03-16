const API_BASE = "/v1";

export interface StageLog {
  stage_id: string;
  confidence: number;
  elapsed_ms: number;
  skipped: boolean;
  gate_decision: string | null;
}

export interface TokenStatsData {
  original_tokens: number;
  compressed_tokens: number;
  savings_ratio: number;
  savings_pct: string;
}

export interface CompressResult {
  original_prompt: string;
  compressed_prompt: string;
  system_prompt: string;
  compressed_system_prompt: string;
  token_stats: TokenStatsData;
  domain: string;
  emotion_layer: { emotions: string[]; confidence: number } | null;
  stage_logs: StageLog[];
  injection_detected: boolean;
  quality_score: number | null;
}

export async function compressPrompt(
  userPrompt: string,
  systemPrompt: string = "",
  options?: {
    preset?: string;
    compressionLevel?: string;
    targetModel?: string;
  }
): Promise<CompressResult> {
  const res = await fetch(`${API_BASE}/compress`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_prompt: userPrompt,
      system_prompt: systemPrompt,
      preset: options?.preset,
      compression_level: options?.compressionLevel ?? "balanced",
      target_model: options?.targetModel ?? "gpt-4o-mini",
    }),
  });

  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getPipelineStatus(): Promise<
  Record<string, { name: string; enabled: boolean }>
> {
  const res = await fetch(`${API_BASE}/pipeline/status`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const data = await res.json();
  return data.stages;
}

export async function toggleStage(
  stageId: string,
  enabled: boolean
): Promise<void> {
  await fetch(`${API_BASE}/pipeline/toggle/${stageId}?enabled=${enabled}`, {
    method: "POST",
  });
}
