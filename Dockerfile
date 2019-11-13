FROM ubuntu:16.04
LABEL authors=OpenStaxCONENG

#========================
# Add PrinceXML
# Source: https://github.com/openstax/docker-princexml/blob/master/Dockerfile
#========================
ENV PRINCE_VERSION=12.5-1
ENV PRINCE_DEB_BUILD=16.04

ADD https://www.princexml.com/download/prince_${PRINCE_VERSION}_ubuntu${PRINCE_DEB_BUILD}_amd64.deb /tmp/

#========================
# Sytem level packages
# software-properties-common allows us to add the open-jdk afterwards
#========================
RUN apt-get -y update \
  && apt-get -y --no-install-recommends install \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    python-virtualenv \
    libxslt1-dev \
    libxml2-dev \
    zlib1g-dev \
    librsvg2-bin \
    otf-stix \
    imagemagick \
    inkscape \
    ruby \
    libxml2-utils \
    zip \
    unzip \
    docbook-xsl-ns \
    xsltproc \
    libopencv-dev \
    python-opencv \
    python-dev \
    memcached \
    nodejs \
    npm \
    curl \
    git \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

#========================
# Install node from nodesource
# - https://github.com/yarnpkg/yarn/issues/6914
#========================
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - \
  && apt-get -qqy install nodejs

#========================
# Add yarn repository to sources list
# - https://yarnpkg.com/lang/en/docs/install/#debian-stable
#========================
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
  && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list

#========================
# Install openjdk-7-jdk, PrinceXML, and yarn
#========================
RUN add-apt-repository ppa:openjdk-r/ppa \
  && apt-get -qqy update --no-install-recommends \
  && apt-get -qqy install  openjdk-7-jdk \
  gdebi yarn\
  && gdebi --non-interactive /tmp/prince_${PRINCE_VERSION}_ubuntu${PRINCE_DEB_BUILD}_amd64.deb \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

#=======================
# Install pip
# - https://pip.pypa.io/en/stable/installing/
#=======================
RUN curl https://bootstrap.pypa.io/get-pip.py | python

#=======================
# Install bundler
#=======================
RUN gem install bundler

#========================
# Copy over the application code
#========================
COPY . /code

WORKDIR /code

#========================
# Install application level dependencies
#========================
RUN python setup.py install
RUN yarn --prefer-offline

