ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN apt-get update && apt-get install -y \
    python3-opencv \
    ros-jazzy-cv-bridge \
    && rm -rf /var/lib/apt/lists/*