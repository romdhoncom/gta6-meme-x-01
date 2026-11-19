// Entry program for make.fun's gta6-meme-x-01 (Node 22, standard library only).
//
// The entry is a post on X: the meme (meme.png, drawn by meme_gen.py) is
// posted from a public account with the post text in POST_TEXT.md, and this
// program hands in the post's address. All it does is copy POST.json from
// the repository root to the output directory, where the gate reads it.
// The house reads the post itself from X; nothing written here is judged.
//
// POST.json still holds a placeholder address until the post is up: replace
// it with the post's address, {"url": "https://x.com/<handle>/status/<id>"},
// before submitting. A placeholder is refused by the gate on purpose.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR
// stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

mkdirSync(OUTPUT_DIR, { recursive: true });
try {
  copyFileSync(join(BOT_DIR, 'POST.json'), join(OUTPUT_DIR, 'POST.json'));
} catch (err) {
  console.error(`POST.json could not be copied from ${BOT_DIR}: ${(err as Error).message}`);
  process.exit(1);
}
