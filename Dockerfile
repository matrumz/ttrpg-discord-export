FROM ubuntu:22.04
SHELL [ "sh", "-e", "-c" ]

RUN <<DOCKERFILE_EOF
export DEBIAN_FRONTEND=noninteractive
export ACCEPT_EULA=Y

# Install packages
apt-get update
apt-get install -y --no-install-recommends \
	python3-pip \
	python3.11

DOCKERFILE_EOF

RUN --mount=type=bind,target=/tmp/requirements.txt,source=/src/requirements.txt <<DOCKERFILE_EOF
pip install -r /tmp/requirements.txt
DOCKERFILE_EOF

COPY src/rootfs /

ENTRYPOINT [ "/app/main.py" ]
