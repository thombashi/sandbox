Create table
------------

.. include:: table_from_data_matrix.rst


Create table from a csv file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. object:: Input: sample\_data.csv

    .. parsed-literal::
    
        "attr_a","attr_b","attr_c"
        1,4,"a"
        2,2.1,"bb"
        3,120.9,"ccc"

.. object:: Sample code

    .. code:: python

        from simplesqlite import SimpleSQLite
        import six

        table_name = "sample_data"
        con = SimpleSQLite("sample.sqlite", "w")
        con.create_table_from_csv(csv_path="sample_data.csv")

        six.print_(con.get_attribute_name_list(table_name))
        result = con.select(select="*", table_name=table_name)
        for record in result.fetchall():
            six.print_(record)
    
.. object:: Output

    .. code:: console

        ['attr_a', 'attr_b', 'attr_c']
        (1, 4.0, u'a')
        (2, 2.1, u'bb')
        (3, 120.9, u'ccc')
