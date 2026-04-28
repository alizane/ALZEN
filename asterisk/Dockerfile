# ALZEN Phase 31 — Asterisk SIP Server (Self-Hosted)
FROM asterisk:18-alpine
RUN apk add --no-cache sox curl
COPY etc/asterisk.conf /etc/asterisk/asterisk.conf
COPY etc/extensions.conf /etc/asterisk/extensions.conf
COPY etc/sip.conf /etc/asterisk/sip.conf
EXPOSE 5060/udp 8088/tcp 5038/tcp
HEALTHCHECK --interval=30s CMD asterisk -rx "core show version" || exit 1
