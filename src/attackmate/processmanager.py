import multiprocessing as mp


class ProcessManager:
    def __init__(self):
        self.ctx = mp.get_context('spawn')
        self.proc_list: list[(mp.Process, bool)] = []

    def kill_or_wait_processes(self):
        for proc, kill in self.proc_list:
            if kill and proc.is_alive():
                proc.kill()
            elif not kill and proc.is_alive():
                proc.join()

    def add_process(self, proc: mp.Process, kill=True):
        self.proc_list.append((proc, kill))
