# Python 3.12, a C compiler and make, for machines without them: the interpreter of the stored results.
#   docker build -t mutation-barriers .
#   docker run --rm --network none --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$PWD":/work -w /work mutation-barriers make test
# numpy is installed for the tasks that run the programs of experiments/ (experiments/requirements.txt);
# cypari2, which only `n4_opposite.py fn` and three checking scripts need, is not.
FROM python:3.12-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends make gcc libc6-dev git \
 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir numpy==2.5.4
