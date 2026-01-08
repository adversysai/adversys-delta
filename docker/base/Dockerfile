# Use the latest slim version of Kali Linux
FROM kalilinux/kali-rolling


# Set locale to en_US.UTF-8 and timezone to UTC
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y locales tzdata
RUN sed -i -e 's/# \(en_US\.UTF-8 .*\)/\1/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8
RUN ln -sf /usr/share/zoneinfo/UTC /etc/localtime
RUN echo "UTC" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
ENV TZ=UTC

# Copy contents of the base filesystem to /
# Note: Build context should be the root of the project (docker build -f docker/base/Dockerfile .)
COPY docker/base/fs/ /

# install packages software (split for better cache management)
RUN bash /ins/install_base_packages1.sh
RUN bash /ins/install_base_packages2.sh
RUN bash /ins/install_base_packages3.sh
RUN bash /ins/install_base_packages4.sh

# install python after packages to ensure version overriding
RUN bash /ins/install_python.sh

# install searxng
RUN bash /ins/install_searxng.sh

# configure ssh
RUN bash /ins/configure_ssh.sh

# after install
RUN bash /ins/after_install.sh

# Set capabilities on nmap if it exists (for raw socket access)
# This allows nmap to work without requiring the container to run in privileged mode
# Note: nmap may not be installed in base image, so this is conditional
# Install libcap2-bin if not already installed (required for setcap)
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends libcap2-bin || true && \
    if command -v nmap >/dev/null 2>&1; then \
        setcap cap_net_raw,cap_net_admin+eip /usr/bin/nmap || \
        (echo "WARNING: Failed to set capabilities on nmap. Raw socket access may not work." && \
         echo "Container may need to run with --privileged or --cap-add=NET_RAW,NET_ADMIN" && \
         true); \
    else \
        echo "INFO: nmap not found in base image. Capabilities not set."; \
    fi && \
    rm -rf /var/lib/apt/lists/*

# Keep container running infinitely
CMD ["tail", "-f", "/dev/null"]
