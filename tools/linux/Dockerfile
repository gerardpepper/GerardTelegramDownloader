# Ambiente di build per l'eseguibile Linux (usato da build-linux.ps1).
# Debian 12 (glibc 2.36): l'eseguibile funziona sulle distribuzioni con glibc 2.36 o più recente.
FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
        binutils libgl1 libegl1 libglib2.0-0 libfontconfig1 libdbus-1-3 \
        libxkbcommon0 libxkbcommon-x11-0 libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
        libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-xinerama0 libxcb-xkb1 libxcb-xfixes0 \
        libx11-xcb1 libxrender1 libxi6 libsm6 libice6 \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements-dev.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt -r /tmp/requirements-dev.txt
ENV GTD_PYTHON=python
