import argparse
import os
import signal
import subprocess
import json
import time
import datetime
import threading
from abc import ABC, abstractmethod

TIMEOUT = 10
RETRY_COOLDOWN = 10

class Config:
    def __init__(self):
        pass

class Benchmarker(ABC):
    """
    `gen_cmd` and `parse_stdout` are the two methods that need to be implemented.
    - `gen_cmd`: generates a command to run the program
    - `parse_stdout`: parses the output to save the result

    Optionally, you can implement the following methods:
    - `pre_cmd`: a command to run before the benchmark
    - `cli_arg`: add command line arguments
    - `fix_cfg`: fix the configuration
    - `print_result`: print the result
    """
    @abstractmethod
    def gen_cmd(self, file: str):
        """Given a file, generate the command to run the benchmark"""
        pass

    @abstractmethod
    def parse_stdout(self, stdout: str):
        """
        Parse the output of the benchmark

        Input: stdout: str
        Output: dict
        """
        pass

    def pre_cmd(self):
        pass

    def cli_arg(self, parser):
        """Add command line arguments to the parser"""
        return parser

    def fix_cfg(self, cfg: Config, _args) -> Config:
        return cfg

    def base_dir(self) -> str:
        """
        Default base directory
        """
        return "./"

    def print_result(self, file, result):
        if result['ok']:
            print(f'{file}\t{result["result"]}')
        else:
            print(f'{file}\t{result["error"]}')
    
    def callback(self, file, result):
        self.print_result(file, result)
    
    def stat(self, results):
        pass

    def allow_parallel(self):
        return True

    def dump_meta(self, cfg):
        data = dict()
        data['timeout'] = cfg.timeout
        data['list'] = cfg.list
        data['basedir'] = cfg.basedir
        return data


class Executor:
    def __init__(self, bench: Benchmarker, cfg: Config, tasks: list):
        self.bench = bench
        self.cfg = cfg
        self.tasks = tasks
        self.results = []

    def gen_preexec_fn(self):
        def preexec_fn():
            os.chdir(self.cfg.root)
            os.setsid()
        return preexec_fn

    def run(self, cmd: str, timeout: int=None):
        if timeout is None:
            timeout=self.cfg.timeout
        st = time.perf_counter()
        with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, preexec_fn=self.gen_preexec_fn()) as p:
            try:
                output, _ = p.communicate(timeout=timeout)
                ed = time.perf_counter()
                elapsed = ed - st
                return output, elapsed
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(p.pid, signal.SIGKILL)
                except:
                    pass
                raise

    def handle(self, file: str, retry: int = 0):
        cmd = self.bench.gen_cmd(file)
        try:
            stdout, t = self.run(cmd)
            stdout = stdout.decode('utf-8')
            result = self.bench.parse_stdout(stdout)
            result['time'] = t
            result['ok'] = True
        except subprocess.TimeoutExpired:
            result = {'ok': False, 'error': 'timeout'}
            result['time'] = self.cfg.timeout
        if 'result' not in result:
            result['result'] = 'fail'
        if result['result'] == 'fail' and self.cfg.retry > 0:
            time.sleep(RETRY_COOLDOWN)
            self.handle(file, retry - 1)
        else:
            result['file'] = file
            result['size'] = os.path.getsize(file)
            self.bench.callback(file, result)
            self.results.append(result)

    def stat(self):
        pass
    
    def start(self):
        for file in self.tasks:
            self.handle(os.path.join(self.cfg.basedir, self.cfg.base, file))
        self.stat()

def run_par(executor: Executor):
    executor.start()

def save_json(filename: str, meta: dict, results: list):
    data = meta
    data["result"] = results
    with open(filename, "w") as f:
        json.dump(data, f)

def do_bench(bench: Benchmarker):
    """
    The main function to run the benchmark

    Input: bench: Benchmarker

    Example:
    ```
    class YourBenchmarker(Benchmarker):
        ...

    if __name__ == '__main__':
        bench = YourBenchmarker()
        do_bench(bench)
    ```
    """
    now = datetime.datetime.now()
    default_json_file = "results/" + now.strftime("%Y-%m-%d-%H%M") + ".json"


    parser = argparse.ArgumentParser()
    parser.add_argument("list", help="benchmark target name")
    parser.add_argument("--timeout", help="timeout", default=TIMEOUT, type=int)
    parser.add_argument('--json', help="set filename in which results will be saved", default=default_json_file)
    parser.add_argument("--basedir", help="base directory", default=bench.base_dir())
    parser.add_argument("--test-config", help="run a single instance to verify the configuration setup", action="store_true")

    if bench.allow_parallel():
        parser.add_argument("--n-threads", help="Number of parallel execution", default=1, type=int)

    parser = bench.cli_arg(parser)
    args = parser.parse_args()

    cfg = Config()
    cfg.root = './'
    cfg.retry = 0
    cfg.base = 'inputs'
    cfg.timeout = args.timeout
    cfg.json = args.json
    cfg.basedir = args.basedir
    cfg.list = args.list
    cfg = bench.fix_cfg(cfg, args)

    d = os.path.dirname(cfg.json)
    if not os.path.exists(d):
        os.makedirs(d)

    if bench.allow_parallel() and not args.test_config:
        assert(args.n_threads > 0 and args.n_threads < 1024)
        n_par = args.n_threads
    else:
        n_par = 1

    with open(os.path.join(cfg.basedir, 'lists', cfg.list)) as f:
        files = f.read().strip('\n').split('\n')

    if args.test_config:
        files = files[:1]

    tasks = [[] for i in range(n_par)]
    for i, f in enumerate(files):
        tasks[i % n_par].append(f)

    executors = []
    for i in range(n_par):
        executors.append(Executor(bench, cfg, tasks[i]))
    
    out, _ = executors[0].run(bench.pre_cmd(), timeout=1000)
    print(out.decode('utf-8'))

    threads = [threading.Thread(target=run_par, args=(e,)) for e in executors]
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()

    results = []
    for e in executors:
        results.extend(e.results)
    save_json(cfg.json, bench.dump_meta(cfg), results)
    print('saved: ', cfg.json)
