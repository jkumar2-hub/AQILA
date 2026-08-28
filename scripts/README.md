# AQILA — Scripts Directory
# Shared — Setup and utility scripts
# ─────────────────────────────────────────────────────────────────────────────
#
# Owner: Shared (M4 coordinates)
#
# Planned scripts (to be created during pre-hackathon setup or Hour 0):
#
#   verify_models.sh / verify_models.ps1
#     Checks that all required P0 models are pre-downloaded and available:
#     - Ollama llama3.2:3b
#     - sentence-transformers all-MiniLM-L6-v2
#     - ChromaDB smoke test
#     Prints PASS or FAIL for each. M4 adds startup warning if required models missing.
#
#   verify_offline.sh / verify_offline.ps1
#     Disconnects network simulation; runs a full end-to-end smoke test.
#     Used during Hours 17–19 offline verification.
#
#   setup_env.sh / setup_env.ps1
#     Creates backend/.env from backend/.env.example if not already present.
#
# References:
#   - v4.1 §14 Pre-Hackathon Checklist
#   - v4.1 §23 Offline Audit
# ─────────────────────────────────────────────────────────────────────────────
# DO NOT add application scripts here during repository initialization.
