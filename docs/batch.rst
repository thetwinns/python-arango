Batch API Execution
-------------------
.. warning::

    The batch request API is deprecated since ArangoDB 3.8.0.
    We discourage its use, as it will be removed in a future release.
    It is already slow and seems to regularly create weird errors when
    used with recent versions of ArangoDB.

    The driver functionality has been refactored to no longer use the batch API,
    but a `ThreadPoolExecutor` instead. For backwards compatibility,
    `max_workers` is set to 1 by default, but can be increased to speed up
    batch operations. Essentially, the batch API can now be used to send
    multiple requests in parallel, but not to send multiple requests in a
    single HTTP call. Note that sending multiple requests in parallel may
    cause conflicts on the servers side (for example, requests that modify the same document).

    To send multiple documents at once to an ArangoDB instance,
    please use any of :class:`arango.collection.Collection` methods
    that accept a list of documents as input, such as:

    * :func:`~arango.collection.Collection.insert_many`
    * :func:`~arango.collection.Collection.update_many`
    * :func:`~arango.collection.Collection.replace_many`
    * :func:`~arango.collection.Collection.delete_many`

After the commit, results can be retrieved later from :ref:`BatchJob` objects.

**Example:**

.. code-block:: python

    from arango import ArangoClient, AQLQueryExecuteError

    # Initialize the ArangoDB client.
    client = ArangoClient()

    # Connect to "test" database as root user.
    db = client.db('test', username='root', password='passwd')

    # Get the API wrapper for "students" collection.
    students = db.collection('students')

    # Begin batch execution via context manager. This returns an instance of
    # BatchDatabase, a database-level API wrapper tailored specifically for
    # batch execution. The batch is automatically committed when exiting the
    # context. The BatchDatabase wrapper cannot be reused after commit.
    with db.begin_batch_execution(return_result=True) as batch_db:

        # Child wrappers are also tailored for batch execution.
        batch_aql = batch_db.aql
        batch_col = batch_db.collection('students')

        # API execution context is always set to "batch".
        assert batch_db.context == 'batch'
        assert batch_aql.context == 'batch'
        assert batch_col.context == 'batch'

        # BatchJob objects are returned instead of results.
        job1 = batch_col.insert({'_key': 'Kris'})
        job2 = batch_col.insert({'_key': 'Rita'})
        job3 = batch_aql.execute('RETURN 100000')
        job4 = batch_aql.execute('INVALID QUERY')  # Fails due to syntax error.

    # Upon exiting context, batch is automatically committed.
    assert 'Kris' in students
    assert 'Rita' in students

    # Retrieve the status of each batch job.
    for job in batch_db.queued_jobs():
        # Status is set to either "pending" (transaction is not committed yet
        # and result is not available) or "done" (transaction is committed and
        # result is available).
        assert job.status() in {'pending', 'done'}

    # Retrieve the results of successful jobs.
    metadata = job1.result()
    assert metadata['_id'] == 'students/Kris'

    metadata = job2.result()
    assert metadata['_id'] == 'students/Rita'

    cursor = job3.result()
    assert cursor.next() == 100000

    # If a job fails, the exception is propagated up during result retrieval.
    try:
        result = job4.result()
    except AQLQueryExecuteError as err:
        assert err.http_code == 400
        assert err.error_code == 1501
        assert 'syntax error' in err.message

    # Batch execution can be initiated without using a context manager.
    # If return_result parameter is set to False, no jobs are returned.
    batch_db = db.begin_batch_execution(return_result=False)
    batch_db.collection('students').insert({'_key': 'Jake'})
    batch_db.collection('students').insert({'_key': 'Jill'})

    # The commit must be called explicitly.
    batch_db.commit()
    assert 'Jake' in students
    assert 'Jill' in students

.. note::
    * Be mindful of client-side memory capacity when issuing a large number of
      requests in single batch execution.
    * :ref:`BatchDatabase` and :ref:`BatchJob` instances are stateful objects,
      and should not be shared across multiple threads.
    * :ref:`BatchDatabase` instance cannot be reused after commit.

See :ref:`BatchDatabase` and :ref:`BatchJob` for API specification.
