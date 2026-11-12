#!/usr/bin/env node
/**
 * QVAC Real Local Model Runner & Benchmark
 * 
 * Executes QWEN3_600M_INST_Q4 (Qwen3-0.6B-Q4_0.gguf) locally using @qvac/sdk.
 * Operates 100% offline with zero cloud dependencies and zero mock fallbacks.
 * 
 * Rules:
 * - NO fallback canned responses
 * - NO simulated or hardcoded latencies
 * - Any failure (import, weights, loading, generation) immediately stops with exit code 1.
 */

import { performance } from 'node:perf_hooks';
import process from 'node:process';
import {
  getSystemResources,
  loadModel,
  unloadModel,
  completion,
  QWEN3_600M_INST_Q4
} from '@qvac/sdk';

async function main() {
  const args = process.argv.slice(2);
  let prompt = "Provide 3 creative names for a local agricultural coding club in Kenya.";

  if (args.includes('--changed')) {
    prompt = "Give 3 bullet-point tips for saving water in tomato drip irrigation. Each tip must be 8 words or fewer.";
  } else if (args.length > 0 && !args[0].startsWith('--')) {
    prompt = args[0];
  }

  console.log("======================================================================");
  console.log("TERRANEXUS: QVAC LOCAL NEURAL MODEL INFERENCE BENCHMARK");
  console.log("Runtime Environment:");
  console.log(`• OS Platform: ${process.platform} (${process.arch})`);
  console.log(`• Node Version: ${process.version}`);
  console.log("• Model Descriptor: QWEN3_600M_INST_Q4");
  console.log(`• Model GGUF Target: ${QWEN3_600M_INST_Q4.modelId}`);
  console.log(`• Expected File Size: ${QWEN3_600M_INST_Q4.expectedSize} bytes (~364.5 MB)`);
  console.log(`• Engine Addon: ${QWEN3_600M_INST_Q4.addon} (${QWEN3_600M_INST_Q4.engine})`);
  console.log("======================================================================\n");

  // Step 1: System resource discovery
  let resources;
  try {
    resources = await getSystemResources({ sample: false });
    const ramBytes = resources?.capabilities?.memory?.totalBytes?.value;
    const ramGb = ramBytes ? (ramBytes / (1024 ** 3)).toFixed(2) + " GB" : "N/A";
    const cpuModel = resources?.capabilities?.cpu?.model?.value || "x86_64 CPU";
    console.log(`[Host Hardware] CPU: ${cpuModel} | RAM: ${ramGb}`);
  } catch (err) {
    console.error(`❌ FATAL: getSystemResources diagnostics failed: ${err.message}`);
    process.exit(1);
  }

  // Step 2: Load Model via @qvac/sdk
  console.log(`\n[1/3] Loading local neural model weights into memory...`);
  const tLoadStart = performance.now();
  let modelId;
  try {
    modelId = await loadModel({
      modelSrc: QWEN3_600M_INST_Q4,
      modelConfig: {
        ctx_size: 2048,
        device: 'cpu'
      },
      onProgress: (p) => {
        if (p && p.percentage != null) {
          process.stdout.write(`\rLoading progress: ${p.percentage}%`);
        }
      }
    });
  } catch (err) {
    console.error(`\n❌ FATAL: Failed to load QVAC model into memory: ${err.message}`);
    console.error(err.stack);
    process.exit(1);
  }

  const loadDurationMs = performance.now() - tLoadStart;
  console.log(`\n[2/3] Model loaded successfully in ${loadDurationMs.toFixed(0)} ms. Local Model ID: ${modelId}`);

  // Step 3: Run Completion Stream within robust finally-cleanup lifecycle
  console.log(`\n[3/3] Executing on-device neural completion...`);
  console.log(`Prompt: "${prompt}"\n`);
  console.log("--- MODEL RESPONSE STREAM START ---");

  const tInferStart = performance.now();
  let firstTokenMs = 0;
  let tokenCount = 0;
  let generatedText = "";
  let inferDurationSec = 0;

  try {
    const run = completion({
      modelId,
      history: [
        {
          role: 'user',
          content: prompt
        }
      ],
      stream: true
    });

    for await (const token of run.tokenStream) {
      if (tokenCount === 0) {
        firstTokenMs = performance.now() - tInferStart;
      }
      process.stdout.write(token);
      generatedText += token;
      tokenCount++;
    }
    inferDurationSec = (performance.now() - tInferStart) / 1000;
  } catch (err) {
    console.error(`\n❌ FATAL: Completion generation failed: ${err.message}`);
    console.error(err.stack);
    try {
      await unloadModel({ modelId });
    } catch (_) {}
    process.exit(1);
  } finally {
    // Step 4: Strict Unload Model to free memory (Fatal if unload fails)
    try {
      if (modelId) {
        await unloadModel({ modelId });
        console.log(`\n[Unload] Model ${modelId} successfully unloaded from memory.`);
      }
    } catch (err) {
      console.error(`\n❌ FATAL: Model unload failed: ${err.message}`);
      process.exit(1);
    }
  }

  console.log("\n--- MODEL RESPONSE STREAM END ---\n");

  // Step 5: Strictly reject empty generations (zero tokens)
  if (tokenCount === 0 || !generatedText.trim()) {
    console.error("❌ FATAL: QVAC model produced 0 tokens. Offline inference failed.");
    process.exit(1);
  }

  const tokensPerSec = inferDurationSec > 0
    ? (tokenCount / inferDurationSec).toFixed(2)
    : "0.00";

  // Step 5: Report Truthful Measured Benchmark Metrics
  console.log("\n======================================================================");
  console.log("VERIFIED LOCAL MODEL BENCHMARK METRICS (NO SIMULATION / NO FALLBACK):");
  console.log(`• Model: QWEN3_600M_INST_Q4 (Qwen3-0.6B-Q4_0.gguf)`);
  console.log(`• Execution Mode: qvac_local_hardware`);
  console.log(`• Device: cpu`);
  console.log(`• Model Load Duration: ${loadDurationMs.toFixed(0)} ms`);
  console.log(`• First Text Token Latency: ${firstTokenMs.toFixed(1)} ms`);
  console.log(`• Generation Duration: ${inferDurationSec.toFixed(2)} s`);
  console.log(`• Total Tokens Generated: ${tokenCount}`);
  console.log(`• Throughput Speed: ${tokensPerSec} tokens/s`);
  console.log("======================================================================\n");
}

main().catch((err) => {
  console.error("FATAL: Unhandled benchmark exception:", err);
  process.exit(1);
});
