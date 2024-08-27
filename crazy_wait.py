from multiprocessing import Queue

def crazyWait(queue: Queue):
    while(True):
        # queue is common_event_queue
        # queue_data is the data (status) we get from common_event_queue, which is the dictionary with 2 keys or more
        # first key is feature which is what part of process or feature does it relate (flight, camera, or anything else)
        # second key is state which is what is the state of the feature now that is given
        # there may be other keys to add more details, descriptions, or contexts
        queue_data = queue.get()
        if (queue_data['feature'] == 'crazy_flight') {
            if (queue_data['state'] == 'returned')
        }