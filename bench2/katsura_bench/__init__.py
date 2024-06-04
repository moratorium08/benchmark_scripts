import argparse
import os
import signal
import subprocess
import json
import time
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
    def gen_cmd(file: str):
        """Given a file, generate the command to run the benchmark"""
        pass

    @abstractmethod
    def parse_stdout(stdout: str):
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

    def print_result(file, result):
        if result['ok']:
            print(f'{file}\t{result["result"]}')
        else:
            print(f'{file}\t{result["error"]}')


class Executor:
    def __init__(self, bench: Benchmarker, cfg: Config):
        self.bench = bench
        self.cfg = cfg
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

    def handle(self, file: str, parser, retry: int = 0):
        cmd = self.bench.gen_cmd(file)
        try:
            stdout, t = self.run(cmd)
            stdout = stdout.decode('utf-8')
            result = parser(stdout)
            result['time'] = t
        except subprocess.TimeoutExpired:
            result = {'ok': False, 'error': 'timeout'}
            result['time'] = self.cfg.timeout
        if 'result' not in result:
            result['result'] = 'fail'
        if result['result'] == 'fail' and self.cfg.retry > 0:
            time.sleep(RETRY_COOLDOWN)
            self.handle(file, parser, retry - 1)
        else:
            result['file'] = file
            result['size'] = os.path.getsize(file)
            self.bench.callback(file, result)
            self.results.append(result)

    def save_json(self, filename: str):
        with open(filename, "w") as f:
            json.dump(self.results, f)

    def stat(self):
        pass


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
    parser = argparse.ArgumentParser()
    parser.add_argument("list", help="benchmark target name")
    parser.add_argument("--timeout", help="timeout", default=TIMEOUT, type=int)
    parser.add_argument('--json', help="set filename in which results will be saved", default=None)
    parser.add_argument("--basedir", help="base directory", default=bench.base_dir())
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

    executor = Executor(bench, cfg)

    out, _ = executor.run(bench.pre_cmd(), timeout=1000)
    print(out.decode('utf-8'))
    with open(os.path.join(cfg.basedir, 'lists', cfg.list)) as f:
        files = f.read().strip('\n').split('\n')
    for file in files:
        executor.handle(bench, cfg,  os.path.join(cfg.basedir, cfg.base, file))
    bench.stat(executor.results)
    if cfg.json is not None:
        executor.save_json(cfg.json)
