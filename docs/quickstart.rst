Quick Start
================

CLI Tool Installation
----------------------------------

.. code:: pycon

    pip install ghscard


Generate Card Data Files
----------------------------------

``ghscard gen`` command will create card data file of GitHub user/organization/repository.

.. code:: pycon

    ghscard gen thombashi/thombashi -o data
    [INFO] ghscard gen: written repository data to 'data/thombashi.json'


Add Widget to a HTML
----------------------------------

.. code:: html

    <!doctype html>
    <html>
    <body>
        <div class='ghscard' src='data/thombashi.json'></div>

        <script src="https://rawgit.com/thombashi/ghscard/master/dist/ghscard.min.js"></script>
    </body>
    </html>

This will displayed as follows:

.. image:: ss/quickstart.png
    :width: 300px
    :alt: Link to an example page
    :target: https://thombashi.github.io/ghscard/quickstart/
