# nohup python3 ringen.py 24comp_ADT-LIA --n-threads 16 --timeout 300 &
from katsura_bench import *

class RInGen(Benchmarker):
    def pre_cmd(self):
        return 'echo evaluating ringen...'

    def gen_cmd(self, file: str):
        print('file', file)
        return f'ringen {file}'

    def parse_stdout(self, stdout):
      result_data = dict()
      results = stdout.split("\n")
      stdouts = []
      warnings = ""
      for line in results:
          if line.startswith("; "):
              warnings += line + "\n"
          else:
              stdouts.append(line)
      stdout = stdouts[0]
      result_data['result'] = 'invalid' if 'unsat' in stdout else 'valid' if 'sat' in stdout else 'fail'
      result_data['warnings'] = warnings
      return result_data

    def base_dir(self):
        return '/home/katsura/github.com/moratorium08/hopdr/hopdr/benchmark'


do_bench(RInGen())
