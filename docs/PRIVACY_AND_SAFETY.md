# Privacy, consent and safety

EchoPersona is an experimental demonstration of personalized expressive speech synthesis. Generated audio is synthetic and may not accurately preserve a speaker’s identity, intended emotion, or communication style. Use only voices you own or have explicit permission from an adult speaker to use. Do not use outputs to impersonate someone, mislead listeners, or bypass identity checks. This prototype is not a medical device and is not a substitute for professional accessibility or clinical advice.

**Before creating a profile:** choose your own voice or a recording from an explicitly consenting adult; type the required acknowledgement. This is self-declared consent, not identity verification. No minors' voices are supported as a product policy.

**On disk:** normalized reference WAV, per-profile metadata, optional reference transcript and optional compact approved preferences. Raw imported chat history and generated speech are not persisted by app services. Session widgets and output buffers may hold input until cleared or closed. No automatic remote telemetry is added. Model downloads may reach third-party model-hosting servers, but there is no remote inference pathway in this release.

**Delete operations:** selective reference removal, full profile deletion, all-profile deletion, current-session generation/ratings clear, current-session context summary clear. File deletion cannot guarantee erasure from disk backups/OS caches or copies exported by the user. `.gitignore` and packaging exclude personal data and recorded speech. Local directory paths are constructed from random IDs rather than file names.

**Restrictions:** no fake identity verification, no spoofing, no recording of phone calls, no auto-send, no non-consensual cloning, no watermark removal, no misleading provenance, no claims of guaranteed affective fidelity. Users should review each result. This product must not be exposed to the internet without an additional design review for authentication, HTTPS, upload isolation and rate limits.
