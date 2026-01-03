# Use the pre-built base image for A0
# Build base first: docker build -f docker/base/Dockerfile -t adversys-delta-base:latest .
# Or use published base: FROM adversys-delta-base:latest
FROM adversys-delta-base:latest

# Branch argument (defaults to "local" for local development)
# Can be overridden: docker build --build-arg BRANCH=main -f docker/run/Dockerfile .
ARG BRANCH=local
ENV BRANCH=$BRANCH

# Environment argument (defaults to "development" for local development)
# Set to "production" for production builds
# Can be overridden: docker build --build-arg ENVIRONMENT=production -f docker/run/Dockerfile .
ARG ENVIRONMENT=development
ENV ENVIRONMENT=$ENVIRONMENT

# GitHub repository URL argument (used when cloning from GitHub)
# Can be overridden: docker build --build-arg GITHUB_REPO_URL=https://github.com/user/repo -f docker/run/Dockerfile .
ARG GITHUB_REPO_URL=https://github.com/adversysai/adversys-delta
ENV GITHUB_REPO_URL=$GITHUB_REPO_URL

# Copy filesystem files to root
# Note: Build context should be the root of the project (docker build -f docker/run/Dockerfile .)
COPY docker/run/fs/ /

# Copy application code to /git/agent-zero (where install scripts expect it for "local" branch)
# This matches the original Agent Zero pattern where code is built into the image at /git/agent-zero
COPY . /git/agent-zero

# pre installation steps
RUN bash /ins/pre_install.sh $BRANCH

# install A0
RUN bash /ins/install_A0.sh $BRANCH

# install additional software
RUN bash /ins/install_additional.sh $BRANCH

# cleanup repo and install A0 without caching, this speeds up builds
ARG CACHE_DATE=none
RUN echo "cache buster $CACHE_DATE" && bash /ins/install_A02.sh $BRANCH

# post installation steps
RUN bash /ins/post_install.sh $BRANCH

# Expose ports
EXPOSE 22 80 9000-9009

RUN chmod +x /exe/initialize.sh /exe/run_A0.sh /exe/run_searxng.sh /exe/run_tunnel_api.sh

# initialize runtime and switch to supervisord
CMD ["/exe/initialize.sh", "$BRANCH"]
