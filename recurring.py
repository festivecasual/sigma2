import random


class Task(object):
    jobs = []

    def __init__(self, period, start='warm', priority=0):
        self.period = period
        self.start = start
        self.priority = priority

    def __call__(self, f):
        def wrapped_f(server):
            f(server)
            server.events.enter(self.period, self.priority, wrapped_f, (server, ))
        self.wrapped_f = wrapped_f

        Task.jobs.append(self)

        return f


def kickstart_tasks(server):
    for job in Task.jobs:
        if job.start == 'hot':
            server.events.enter(0, job.priority, job.wrapped_f, (server, ))
        elif job.start == 'cold':
            server.events.enter(job.period, job.priority, job.wrapped_f, (server, ))
        else:
            server.events.enter(job.period * random.random(), job.priority, job.wrapped_f, (server, ))
