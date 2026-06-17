FROM ghcr.io/gitroomhq/postiz-app:latest

COPY logo-icon.png /tmp/genius-logo-icon.png
COPY logo-wordmark.png /tmp/genius-logo-wordmark.png
COPY custom.css /app/custom.css
COPY patch_branding.py /app/patch_branding.py

RUN python3 /app/patch_branding.py
