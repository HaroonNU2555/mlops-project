FROM apache/airflow:2.7.1

USER root
# Install git, wget, gnupg and DVC as system binary
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    git \
    wget \
    gnupg \
    && wget -qO - https://dvc.org/deb/iterative.asc | gpg --dearmor > packages.iterative.gpg \
    && install -o root -g root -m 644 packages.iterative.gpg /etc/apt/trusted.gpg.d/ \
    && rm packages.iterative.gpg \
    && wget https://dvc.org/deb/dvc.list -O /etc/apt/sources.list.d/dvc.list \
    && apt-get update \
    && apt-get install -y dvc \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow
