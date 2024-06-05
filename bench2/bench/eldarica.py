from katsura_bench import *

class Eldarica(Benchmarker):
    def pre_cmd(self):
        return 'echo Eldarica'
    
    def gen_cmd(self, file: str):
        return f'eld -portfolio {file}'
      
    def parse_stdout(self, stdout):
      result_data = dict()
      result_data['result'] = 'invalid' if 'unsat' in stdout else 'valid' if 'sat' in stdout else 'fail' 
      return result_data
    
    def base_dir(self):
        return '/home/katsura/github.com/moratorium08/hopdr/hopdr/benchmark'


do_bench(Eldarica())
