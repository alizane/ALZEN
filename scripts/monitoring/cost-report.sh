#!/bin/bash
# ============================================================
# ALZEN Daily Cost Report — DeepSeek API usage only
# Infrastructure cost: ALWAYS $0
# ============================================================
echo "=== ALZEN Cost Report — $(date -I) ==="
echo ""
echo "Infrastructure:  $0.00 (Docker, local)"
echo "Lead Discovery:  $0.00 (web scraping + free APIs)"
echo "Email Sending:   $0.00 (Mailgun free tier)"
echo "Voice Calls:     $0.00 (Asterisk + Google TTS free tier)"
echo "Database:        $0.00 (PostgreSQL local)"
echo "Caching:         $0.00 (Redis local)"
echo "----------------------------------------"
echo "DeepSeek API:    ~\$12.00/month (estimated)"
echo "TOTAL MONTHLY:   ~\$12.00"
echo ""
echo "Next billing check: Never (DeepSeek is pay-as-you-go)"
