
# Install Python3 on osx
if [ "$TRAVIS_OS_NAME" = "osx" ] && ! python3; then
    brew upgrade python
    pip3 install tox

    exit 0
else
    pip install tox
fi
