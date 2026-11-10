#!/usr/bin/env node
/**
 * QVAC Real Neural Model CLI Driver
 * Executes on-device inference using @qvac/sdk and outputs structured JSON or text.
 * Strictly zero fallback: exits non-zero on failure.
 */

import { performance } from 'node:perf_hooks';
import process from 'node:process';
import {
  loadModel,
  unloadModel,
  completion,
  cancel,
  QWEN3_600M_INST_Q4
} from '@qvac/sdk';

async function run() {
  const args = process.argv.slice(2);
  let prompt = "Provide 3 creative names for a local agricultural coding club in Kenya.";
  let jsonOutput = false;
  let maxTokens = 250;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--json') {
      jsonOutput = true;
    } else if (args[i] === '--prompt' && i + 1 < args.length) {
      prompt = args[i + 1];
      i++;
    } else if (args[i] === '--max-tokens' && i + 1 < args.length) {
      maxTokens = parseInt(args[i + 1], 10);
      i++;
    } else if (!args[i].startsWith('--')) {
      prompt = args[i];
    }
  }

  const tStart = performance.now();
  let modelId;
  try {
    modelId = await loadModel({
      modelSrc: QWEN3_600M_INST_Q4,
      modelConfig: { ctx_size: 2048, device: 'cpu' }
    });
  } catch (err) {
    if (jsonOutput) {
      console.log(JSON.stringify({ error: err.message, status: "load_failed" }));
    } else {
      console.error("FATAL: Failed to load model:", err.message);
    }
    process.exit(1);
  }

  const tInfer = performance.now();
  let firstTokenMs = 0;
  let tokenCount = 0;
  let fullText = "";

  const runHandle = completion({
    modelId,
    history: [{ role: 'user', content: prompt }],
    stream: true
  });

  try {
    for await (const token of runHandle.tokenStream) {
      if (tokenCount === 0) {
        firstTokenMs = performance.now() - tInfer;
      }
      fullText += token;
      tokenCount++;

      // When reasoning is complete and sufficient answer is generated, finish early
      if (tokenCount >= maxTokens) {
        try {
          await cancel({ requestId: runHandle.requestId });
        } catch (_) {}
        break;
      }
      if (fullText.includes('</think>') && (fullText.split('</think>')[1].trim().length > 150)) {
        try {
          await cancel({ requestId: runHandle.requestId });
        } catch (_) {}
        break;
      }
    }
  } catch (err) {
    // If cancelled due to budget, ignore cancel error
    if (!err.message?.includes('cancelled')) {
      try { await unloadModel({ modelId }); } catch (_) {}
      if (jsonOutput) {
        console.log(JSON.stringify({ error: err.message, status: "inference_failed" }));
      } else {
        console.error("FATAL: Inference generation failed:", err.message);
      }
      process.exit(1);
    }
  }

  const durationSec = (performance.now() - tInfer) / 1000;
  try {
    await unloadModel({ modelId });
  } catch (_) {}

  const cleanedText = fullText.includes('</think>') 
    ? fullText.split('</think>')[1].trim()
    : fullText.trim();

  const finalResponse = cleanedText.length > 0 ? cleanedText : fullText.trim();

  if (jsonOutput) {
    console.log(JSON.stringify({
      model: "QWEN3_600M_INST_Q4",
      execution_mode: "qvac_local_hardware",
      first_token_ms: Math.round(firstTokenMs),
      duration_seconds: parseFloat(durationSec.toFixed(2)),
      token_count: tokenCount,
      tokens_per_second: parseFloat((tokenCount / Math.max(0.1, durationSec)).toFixed(2)),
      raw_text: fullText,
      response_text: finalResponse
    }));
  } else {
    console.log(finalResponse);
  }
  process.exit(0);
}

run().catch((err) => {
  console.error("FATAL:", err.message);
  process.exit(1);
});
