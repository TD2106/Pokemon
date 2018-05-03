import queue

test = queue.Queue()
test.put((1,))
print(test.get()[0])
