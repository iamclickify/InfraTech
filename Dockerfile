FROM python:3.11

WORKDIR /app

# Install curl and Azure CLI (required by Python's AzureCliCredential)
RUN apt-get update && apt-get install -y curl && \
    curl -sL https://aka.ms/InstallAzureCLIDeb | bash && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD python wait_for_db.py && python manage.py migrate && python manage.py runserver 0.0.0.0:8000