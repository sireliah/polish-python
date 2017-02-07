zaimportuj time
zaimportuj random

z multiprocessing zaimportuj Process, Queue, current_process, freeze_support

#
# Function run by worker processes
#

def worker(input, output):
    dla func, args w iter(input.get, 'STOP'):
        result = calculate(func, args)
        output.put(result)

#
# Function used to calculate result
#

def calculate(func, args):
    result = func(*args)
    zwróć '%s says that %s%s = %s' % \
        (current_process().name, func.__name__, args, result)

#
# Functions referenced by tasks
#

def mul(a, b):
    time.sleep(0.5*random.random())
    zwróć a * b

def plus(a, b):
    time.sleep(0.5*random.random())
    zwróć a + b

#
#
#

def test():
    NUMBER_OF_PROCESSES = 4
    TASKS1 = [(mul, (i, 7)) dla i w range(20)]
    TASKS2 = [(plus, (i, 8)) dla i w range(10)]

    # Create queues
    task_queue = Queue()
    done_queue = Queue()

    # Submit tasks
    dla task w TASKS1:
        task_queue.put(task)

    # Start worker processes
    dla i w range(NUMBER_OF_PROCESSES):
        Process(target=worker, args=(task_queue, done_queue)).start()

    # Get oraz print results
    print('Unordered results:')
    dla i w range(len(TASKS1)):
        print('\t', done_queue.get())

    # Add more tasks using `put()`
    dla task w TASKS2:
        task_queue.put(task)

    # Get oraz print some more results
    dla i w range(len(TASKS2)):
        print('\t', done_queue.get())

    # Tell child processes to stop
    dla i w range(NUMBER_OF_PROCESSES):
        task_queue.put('STOP')


jeżeli __name__ == '__main__':
    freeze_support()
    test()
