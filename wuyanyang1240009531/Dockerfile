FROM python:3.12.7-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
WORKDIR /app
COPY liuxin1240013249/data/ /app/liuxin1240013249/data/
COPY wuyanyang1240009531/scripts/ /app/wuyanyang1240009531/scripts/
COPY wuyanyang1240009531/tests/ /app/wuyanyang1240009531/tests/
CMD ["python", "-B", "wuyanyang1240009531/scripts/run_all.py"]
