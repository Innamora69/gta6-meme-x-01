// gta6-meme-x-01 entry (Node 22, standard library only).
//
// The entry is the X post itself: the agent made a GTA 6 meme (see
// draw_meme.py, which drew meme.png), the post went out on X from a
// public account with make.fun and a play code in its text, and
// POST.json at this repository's root names the post's address.
//
// All this program has to do is hand that address to the gate: it reads
// POST.json, checks it is a JSON object naming one X post address, and
// copies those exact bytes to /output/POST.json, where the house reads
// the post from X (its first picture, then its text) and hands it to
// the judge. No network, no clock, no files outside the repository;
// the same input always writes the same bytes.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and
// MAKEFUN_OUTPUT_DIR stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

// An X post address, nothing else: https://x.com/<handle>/status/<id>
// (twitter.com is the same post). No query string, no fragment.
const POST_URL = /^https:\/\/(x\.com|twitter\.com)\/[A-Za-z0-9_]+\/status\/[0-9]+$/;

function fail(message: string): never {
  console.error(`gta6-meme-x-01: ${message}`);
  process.exit(1);
}

function main(): void {
  const botDir = process.env.MAKEFUN_BOT_DIR ?? "/bot";
  const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
  const source = join(botDir, "POST.json");

  let raw: Buffer;
  try {
    raw = readFileSync(source);
  } catch (err) {
    fail(`POST.json could not be read from ${botDir}: ${(err as Error).message}`);
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw!.toString("utf8"));
  } catch {
    fail("POST.json is not valid JSON");
  }
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    fail("POST.json must be a JSON object naming one X post");
  }
  const url = (parsed as Record<string, unknown>).url;
  if (typeof url !== "string" || !POST_URL.test(url)) {
    fail("POST.json must name one X post address, https://x.com/<handle>/status/<id>");
  }

  mkdirSync(outDir, { recursive: true });
  const target = join(outDir, "POST.json");
  try {
    copyFileSync(source, target);
  } catch (err) {
    fail(`POST.json could not be copied to ${outDir}: ${(err as Error).message}`);
  }

  // Prove the copy is exact: the gate reads these bytes, so a partial
  // or altered copy must never pass silently.
  if (!readFileSync(target).equals(raw!)) {
    fail("the copied POST.json differs from the repository's POST.json");
  }
}

main();
