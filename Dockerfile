FROM python:3.12-slim

RUN groupadd -r agenthive && useradd -r -g agenthive -d /app -s /sbin/nologin agenthive

WORKDIR /app

COPY --chown=agenthive:agenthive . .

RUN pip install --no-cache-dir -e ".[dev,lab]" && rm -rf /root/.cache

USER agenthive

EXPOSE 8000

ENTRYPOINT ["agenthive"]
CMD ["lab", "--http", "--port", "8000"]
