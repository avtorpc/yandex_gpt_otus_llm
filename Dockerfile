FROM quay.io/jupyter/base-notebook:2026-07-28

COPY --chown=jovyan:users requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /home/jovyan/work
