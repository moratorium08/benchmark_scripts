from katsura_bench import *

class Hoice(Benchmarker):
    def pre_cmd(self):
        return 'cargo build --release'
    
    def gen_cmd(self, file: str):
        return f'./target/release/hoice {file}'
      
    def parse_stdout(self, stdout):
      result_data = dict()
      result_data['result'] = 'invalid' if 'unsat' in stdout else 'valid' if 'sat' in stdout else 'fail' 
      return result_data
    
    def base_dir(self):
        return '/home/katsura/github.com/moratorium08/hopdr/hopdr/benchmark'


do_bench(Hoice())
