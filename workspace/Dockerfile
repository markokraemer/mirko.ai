FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies for building Python
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install pyenv
# Pyenv rather than a single Python version so we can adapt to the target repo
RUN curl https://pyenv.run | bash

# Set environment variables for pyenv
ENV HOME  /root
ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

# Initialize pyenv automatically by adding it to the profile script
RUN echo 'eval "$(pyenv init --path)"' >> ~/.profile && \
    echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.profile

# Install multiple versions of Python using pyenv
RUN pyenv install 3.12 && pyenv install 3.8 && pyenv global 3.12

# Verify Python installation
RUN python --version && python3 --version

RUN ssh-keyscan -H github.com >> ~/.ssh/known_hosts

# Using HTTP/1.1 resolved this error on M1 w/ OSX 14.4:
# "RPC failed; curl 92 HTTP/2 stream 0 was not closed cleanly"
RUN git config --global http.version HTTP/1.1

WORKDIR /app