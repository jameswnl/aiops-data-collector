from collector import WORKER

def run():
    acc = {'b64_identity': b'eyJpZGVudGl0eSI6eyJhY2NvdW50X251bWJlciI6IjE0NjAyOTAifX0=', 'account_id': 1460290}
    WORKER(None, 'jobid=122', None, acc)

run()
