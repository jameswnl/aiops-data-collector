FROM centos:7

EXPOSE 8080

RUN INSTALL_PKGS="rh-python36 rh-python36-python-devel rh-python36-python-setuptools rh-python36-python-pip nss_wrapper \
        httpd24 httpd24-httpd-devel httpd24-mod_ssl httpd24-mod_auth_kerb httpd24-mod_ldap \
        httpd24-mod_session atlas-devel gcc-gfortran libffi-devel libtool-ltdl enchant snappy-devel gcc-c++" && \
    yum install -y centos-release-scl && \
    yum -y --setopt=tsflags=nodocs install --enablerepo=centosplus $INSTALL_PKGS && \
    rpm -V $INSTALL_PKGS && \
    # Remove centos-logos (httpd dependency) to keep image size smaller.
    rpm -e --nodeps centos-logos && \
    yum -y clean all --enablerepo='*'

COPY requirements.txt /opt/app-root/requirements.txt

WORKDIR /opt/app-root

RUN source scl_source enable rh-python36 && \
    pip --no-cache-dir install -r requirements.txt

COPY . /opt/app-root

USER 1001

ENTRYPOINT [ "./run.sh" ]
