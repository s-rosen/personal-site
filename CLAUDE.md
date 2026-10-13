# Personal site: simonrosen.me

Simon's resume website. Recruiters and hiring managers read it. Simon iterates on
it across sessions.

## Layout and deploy

- `index.html` is the whole site in one self-contained file. `jobs.html` is a second
  page, and `assets/` holds media and data.
- Content source: `C:\Users\Owner\Documents\Resume\resume_anthropic.tex` (the richer
  of the two resume versions).
- **Hosting: Cloudflare Pages**, project `simonrosen`, custom domains `simonrosen.me` +
  `www.` (proxied CNAMEs → `simonrosen.pages.dev`; the domain is registered at
  Cloudflare). Pushing to `master` on GitHub `s-rosen/personal-site` runs
  `.github/workflows/deploy.yml`, which stages files into `dist/` and runs
  `wrangler pages deploy`. **A new top-level page must be added to the workflow's `cp`
  line** or it won't ship. `/jobs` is served as a clean URL (a 308 from `.html` is
  normal). GitHub Pages is disabled.
- Preview locally with `python -m http.server` (Playwright blocks `file://`). For
  visual tweaks, just commit, push, and let Simon refresh.

## Content rules

- **Copy is straight and professional.** The design can be distinctive; the words
  can't be clever. Removed and not coming back: the journal/academic conceits ("№ 17
  field notes", the dictionary lemma, "fig. 1" captions, § symbols, "N.B." tags, the
  feature-bundle footer joke). Section labels look like "01 About"; tags like "In
  progress".
- Design elements that stay: the IPA gloss over the name, feature-bundle bracket
  notation for skills, and the waveform/spectrogram. Fonts are Fraunces + Newsreader +
  IBM Plex Mono, on a cream/ink/rust palette with a light/dark toggle (localStorage).
  Motion is delta-time based, with reduced-motion fallbacks.
- **Phone number is deliberately omitted.** Email and LinkedIn are included.
- **LinkedIn is `linkedin.com/in/simon-rosen-linguist`.** `/in/simonrosen` is a
  different person; it was wrongly used here and in the resumes until 2026-07-22.

## Hero spectrogram

An interactive Praat-style spectrogram of Simon's ElevenLabs TTS intro clip
("Hi, I'm Simon Rosen…", voice "Luis").

- `scripts/analyze_voice.py`, run with
  `uv run --no-project --with praat-parselmouth --with faster-whisper`, writes
  `assets/speech-data.json` **and** `assets/speech-data.js`. The `.js` is loaded with a
  script tag, not fetched, so `file://` works. It contains the broadband spectrogram
  (uint8 base64), Burg formants F1-F3, the pitch contour, and Whisper word timestamps
  paired with hand-written IPA.
- **Word boundaries were hand-corrected** in `scripts/align-editor.html` +
  `align_server.py` (port 8742). Re-runs keep them; Whisper only runs if the words are
  missing. To change the clip: replace the WAV, update the IPA and TOBI lists in the
  script, delete the words from the JSON, re-run, then re-correct in the editor.
- Tiers: ToBI (draft tones from F0 anchors; Simon is a prosody pro and relabels them),
  IPA, and word. Word segments play on click, with sample-accurate Web Audio playback
  of the lossless WAV (Simon wants exact boundaries); `<audio>` m4a is only the
  `file://` fallback. Space toggles playback when the figure is focused.

## Gotchas

- **Padding shorthand on a higher-specificity selector clobbers `.wrap`'s horizontal
  padding.** This has happened twice. Use `padding-top`/`padding-bottom` longhands on
  sections and the hero. Sections need `scroll-margin-top` for the sticky nav.
- **Cloudflare Pages keeps a per-hostname cache that zone purges can't clear.** A
  removed file kept serving on `simonrosen.me` for days (s-maxage 7 d), while
  `*.pages.dev` and `?cb=` URLs were clean. Purge-everything, single-URL purge, Dev
  Mode, deleting deployments and re-attaching the domain all failed. **What works:**
  deploy a *changed file at the same path*, then purge the zone. Verify with the bare
  URL on the custom domain.

## Paper embargo

`assets/TTS_Eval_Critique.pdf` (the ACL 2026 paper, "Beyond Naturalness: Probing
Automated TTS Evaluators…") is a **554-byte "coming soon" placeholder**. The real PDF
was scrubbed from git history. As of 2026-10-13 the publications entry still reads
"Under review — ACL 2026" with no link. **To publish:** overwrite the PDF with the real
one, restore the "Read the submission" link in the publications section, then commit
and push. The changed asset busts the hostname cache by itself. Ask Simon whether the
archive is live before doing this.
