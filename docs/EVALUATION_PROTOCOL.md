# Evaluation protocol and honest reporting

## Manual acceptance checklist

- [ ] Open `streamlit run app.py` in `demo` without any downloaded model weights.
- [ ] Confirm first-run disclosure and local-only runtime labels.
- [ ] Verify missing/incorrect permission acknowledgement prevents profile persistence.
- [ ] Preview, validate, and save the user's own or adult-consented WAV.
- [ ] Reject oversized/corrupt/silent reference recordings with actionable errors.
- [ ] Save, preview and delete a secondary labelled recording.
- [ ] Import `.txt` and JSON messages; verify review/edit/clear controls.
- [ ] Check a local delivery suggestion and manual override.
- [ ] Verify demo mode does not return speech or pretend to synthesize.
- [ ] Optional on supported Python 3.11/hardware: install Chatterbox, generate short English speech with an authorized reference, playback, download and inspect metadata.
- [ ] Optional: listen to A/B neutral vs selected variant, using identical text/profile.
- [ ] Check that output displays a synthetic disclosure and allows no automatic sharing.
- [ ] Delete the profile and verify all associated references are removed.
- [ ] Check `.env`, model weights, user recordings, caches, secrets absent from ZIP.

## Small participant test (only with informed consent)

Compare A = neutral reference/default exaggeration, B = manual delivery/ref selection, and C = context suggestion + manual approval. Keep script and speaker constant; counterbalance playback order. Gather voluntary scores (1–5) for intelligibility, naturalness, self-reported resemblance, intended tone match, overall preference. Record actual latency, output duration, and failures; never claim these are diagnostic or validated identity measures. Use `ratings_template.csv` and `scripts/summarize_ratings.py` on **actual collected data only**. The template contains no identifying columns. No participant data or experiment scores are bundled.

## Known threats to validity

Small samples, participant demand effects, microphone variance, uncalibrated heuristic tone, stochastic TTS output, mismatched emotion-labelled reference performances, and lack of blinded order. Results are exploratory and not proof that conversation context improves speech quality.
