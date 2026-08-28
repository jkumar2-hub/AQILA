# AQILA — Demo Data Directory
# Shared — committed to repository (controlled dataset)
# ─────────────────────────────────────────────────────────────────────────────
#
# This directory contains the CONTROLLED DEMO DATASET for AQILA SIH 2026.
# All demo files must be created and committed BEFORE the hackathon.
# Do NOT place real sensitive data here.
#
# Required files (per v4.1 §14 + §15 Demo Dataset):
#
#   P0 — Guaranteed Demo (both PDFs required):
#   ┌──────────────────────────────────────────────────────────────────────┐
#   │ field_report.pdf                                                     │
#   │   2-page intel report. Content must include:                        │
#   │   - Operation FALCON                                                 │
#   │   - Location: Sector 7, eastern perimeter                           │
#   │   - Date: March 15 2024, 0300 hrs  ← DELIBERATE CONTRADICTION DATE │
#   │   - Agent Mehra                                                      │
#   │   - Coordinates table                                                │
#   └──────────────────────────────────────────────────────────────────────┘
#   ┌──────────────────────────────────────────────────────────────────────┐
#   │ field_report_b.pdf                                                   │
#   │   Short corroborating report. Content must include:                 │
#   │   - Operation FALCON                                                 │
#   │   - Date: March 25  ← DELIBERATE CONTRADICTION (vs March 15 above) │
#   │   - Agent Mehra                                                      │
#   └──────────────────────────────────────────────────────────────────────┘
#
#   P1 — Extended Demo (optional, hardware permitting):
#   ┌──────────────────────────────────────────────────────────────────────┐
#   │ call_recording.mp3                                                   │
#   │   ~45-second voice recording. Content:                              │
#   │   - Operation Falcon, Date March 25, Agent Mehra                    │
#   │   Used for: audio transcription (Whisper) + timestamp citations     │
#   └──────────────────────────────────────────────────────────────────────┘
#   ┌──────────────────────────────────────────────────────────────────────┐
#   │ screenshot.png                                                       │
#   │   Screenshot of field_report.pdf page 1.                            │
#   │   Used for: image captioning (vision LLM) + CLIP embedding          │
#   └──────────────────────────────────────────────────────────────────────┘
#
# Demo Validation — Expected Facts (per v4.1 §15):
#   Query 1: "What is Operation FALCON?"
#     → Answer mentions "Sector 7" or "eastern perimeter"
#     → At least one [N] citation linking to field_report.pdf
#
#   Query 2: "Who was confirmed at the meeting?"
#     → Answer mentions "Agent Mehra"
#     → Citations from both PDF sources
#     → Evidence graph shows PDF-PDF semantic edge
#
#   Query 3: "When did the crossing occur?"
#     → contradiction_found == true
#     → claim_a contains "March 15", claim_b contains "March 25"
#     → conflict_type == "date"
#
# ─────────────────────────────────────────────────────────────────────────────
# ACTION REQUIRED (before hackathon):
#   All members: create the demo files above and commit them to this directory.
#   See v4.1 §14 Pre-Hackathon Checklist for details.
# ─────────────────────────────────────────────────────────────────────────────
