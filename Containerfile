FROM registry.access.redhat.com/ubi9/ubi-minimal:latest

RUN microdnf update -y && microdnf install -y \
    python3.11 \
    python3.11-pip \
    chkconfig \
    && microdnf clean all \
    && alternatives --install /usr/bin/python python /usr/bin/python3.11 1 \
    && alternatives --install /usr/bin/pip pip /usr/bin/pip3.11 1 \
    && alternatives --set python /usr/bin/python3.11 \
    && alternatives --set pip /usr/bin/pip3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8501
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]