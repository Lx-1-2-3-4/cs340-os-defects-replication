FROM python:3.12.7-slim

WORKDIR /work
COPY data ./data
COPY scripts ./scripts
COPY docs ./docs
COPY README.md LICENSE ./

CMD ["sh", "-c", "python scripts/reproduce.py && python scripts/compare.py && python scripts/validate.py"]
