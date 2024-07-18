FROM python:3.11.7

WORKDIR /app
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY Pipfile /app
COPY Pipfile.lock /app
RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile --${PIPENV_ARGS}
RUN cat /etc/ssl/certs/ca-certificates.crt >> `python -m certifi`

WORKDIR /app
COPY .env /app/.env
COPY migrations /app/migrations
COPY backend_services /app/backend_services

COPY api /app/api
COPY alembic.ini /app/alembic.ini
COPY asgi.py /app/asgi.py

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "asgi:api", "--host", "0.0.0.0", "--port", "8000"]