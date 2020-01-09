import time
import threading
from concurrent.futures import ThreadPoolExecutor as tpe

def some_func(n):
    time.sleep(0.5)
    # print(f'\tprinting: {n}')

def measureExecutionTimeByThreadCount(func):
    def wrapper(threadCount = 1):
        print(f'executing task with {threadCount} workers...')
        t1 = time.time()
        func(threadCount)
        t2 = time.time()
        return f'execution time with {threadCount} workers: {t2 - t1} seconds'
    return wrapper

def create_testData():
    return list( range(12) )

@measureExecutionTimeByThreadCount
def execute(threadCount):
    with tpe(max_workers=threadCount) as executor:
        executor.map( some_func, create_testData() )

@measureExecutionTimeByThreadCount
def execute2(threadCount):
    args = create_testData()
    lock = threading.Lock()

    def task():
        while(True):
            with lock:
                if len(args) <= 0:
                    return
                arg = args.pop()
            some_func(arg)

    threads = [ threading.Thread(target=task) for n in range(threadCount) ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

results1 = [
    execute(threadCount)
    for threadCount in range(1, 5)
]
results2 = [
    execute2(threadCount)
    for threadCount in range(1, 5)
]
print('=======================result1=======================')
print(*results1, sep='\n')
print('=======================result2=======================')
print(*results2, sep='\n')