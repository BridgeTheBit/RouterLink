# ========================================================
# RouterLink Multi-Arch Container Image for MikroTik RouterOS 7
# Optimized for minimal RAM & Flash footprint on Alpine Linux
# ========================================================

FROM python:3.11-alpine3.20 as runtime

LABEL maintainer="RouterLink Core Team"
LABEL description="RouterLink VPN Gateway & Management Server for MikroTik RouterOS 7 Containers"

# Install essential VPN tools, networking utilities, and runtime libraries
RUN apk add --no-cache \
    bash \
    curl \
    ca-certificates \
    openvpn \
    wireguard-tools \
    iptables \
    iproute2 \
    tzdata \
    libffi \
    sqlite-libs

WORKDIR /app

# Install build dependencies temporarily for Python packages with native extensions
COPY server/backend/requirements.txt /app/requirements.txt
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libffi-dev \
    cargo \
    rust \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps \
    && rm -rf /root/.cache /root/.cargo

# Copy Application Source and Embedded WebUI Static Assets
COPY server/backend /app

# Copy Entrypoint Script
COPY deployment/docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Environment Variables
ENV PYTHONUNBUFFERED=1 \
    ROUTERLINK_DATA_DIR=/data \
    ROUTERLINK_HOST=0.0.0.0 \
    ROUTERLINK_PORT=8080

# Volumes & Ports
VOLUME ["/data"]

# Expose WebUI (8080), OpenVPN TCP (8443), OpenVPN UDP (1194), WireGuard UDP (51820)
EXPOSE 8080/tcp 8443/tcp 1194/udp 51820/udp

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://127.0.0.1:8080/api/v1/auth/setup/status || exit 1

ENTRYPOINT ["/entrypoint.sh"]

