FROM python:3.11-slim
WORKDIR /app
COPY deploy/ deploy/
COPY sim/ sim/
COPY paper/artifacts/experiment_protocol.yaml paper/artifacts/experiment_protocol.yaml
RUN pip install --no-cache-dir numpy
EXPOSE 8088
HEALTHCHECK --interval=30s --timeout=5s CMD python deploy/client.py http://127.0.0.1:8088 || exit 1
CMD ["python", "deploy/server.py", "8088"]
