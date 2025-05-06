# Usa Python 3.10 come base
FROM python:3.10

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file nel container
COPY tornio.py /app/
COPY requirements.txt /app/

# Installa i pacchetti necessari
RUN pip install -r requirements.txt

# Espone la porta OPC-UA
EXPOSE 4840

# Avvia lo script del tornio
CMD ["python", "tornio.py"]
