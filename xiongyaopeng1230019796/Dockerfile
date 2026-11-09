# Pinned reproduction environment for the CS340 OS-defect replication.
#
# The analysis uses only the Python standard library, so there is nothing to
# install and no dependency drift. The interpreter is pinned here and in
# .github/workflows/ci.yml (python 3.12.7 / Debian slim base image).

FROM python:3.12.7-slim

LABEL org.opencontainers.image.title="cs340-os-defects-replication"
LABEL org.opencontainers.image.description="Reproduction of arXiv:2608.20643v1 for CS340 Operating Systems"

ENV PYTHONHASHSEED=0 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# `make` is only needed for the convenience targets; the pipeline itself is
# plain Python and runs with the interpreter alone.
RUN apt-get update \
 && apt-get install -y --no-install-recommends make \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /work

COPY requirements.txt ./
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

COPY . .

# Reproduce the paper and validate the result against the committed expectation.
# Generated output is written under /work/results.
CMD ["make", "all"]
