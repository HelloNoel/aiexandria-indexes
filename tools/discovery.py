"""Run source-selection regression queries through an installed AIexandria >=0.3."""
from pathlib import Path
import argparse,json,subprocess,threading,queue,time,shutil,tempfile,os
import yaml

class MCP:
    def __init__(self, binary, args):
        self.q=queue.Queue(); self.i=0
        self.p=subprocess.Popen([str(binary),*args],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
        def consume():
            for line in self.p.stdout:
                self.q.put(json.loads(line))
        threading.Thread(target=consume,daemon=True).start()
        self.rpc('initialize',{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'migration-check','version':'1'}})
        self.p.stdin.write(json.dumps({'jsonrpc':'2.0','method':'notifications/initialized'})+'\n');self.p.stdin.flush()
    def rpc(self,method,params):
        self.i+=1
        self.p.stdin.write(json.dumps({'jsonrpc':'2.0','id':self.i,'method':method,'params':params})+'\n');self.p.stdin.flush()
        end=time.monotonic()+65
        while time.monotonic()<end:
            r=self.q.get(timeout=max(0.1,end-time.monotonic()))
            if r.get('id')==self.i:
                if 'error' in r: return {'error':r['error']}
                return r['result']
        raise TimeoutError(method)
    def call(self,name,args):
        r=self.rpc('tools/call',{'name':name,'arguments':args})
        if 'error' in r or r.get('isError'): return r
        body=''.join(x.get('text','') for x in r.get('content',[]))
        try:return json.loads(body)
        except json.JSONDecodeError:return {'text':body}
    def close(self):
        self.p.stdin.close()
        try:self.p.wait(timeout=5)
        except subprocess.TimeoutExpired:self.p.kill()

def git(path,*args):
    return subprocess.check_output(['git','-C',str(path),*args],stderr=subprocess.DEVNULL,text=True).strip()

def snapshot(path):
    git(path,'init','--object-format=sha1','-b','main')
    git(path,'add','.')
    git(path,'-c','user.name=AIexandria test','-c','user.email=test@example.invalid','-c','commit.gpgsign=false','commit','-m','Discovery evaluation fixture')

parser=argparse.ArgumentParser()
parser.add_argument('--aiexandria',default=shutil.which('aiexandria'))
args=parser.parse_args()
assert args.aiexandria, 'Install AIexandria >=0.3 or pass --aiexandria PATH'
root=Path(__file__).resolve().parents[1]
cases=json.loads((root/'tests/discovery-queries.json').read_text())
with tempfile.TemporaryDirectory(prefix='aiexandria-discovery-') as temp:
    base=Path(temp);repo=base/'catalog'
    shutil.copytree(root,repo,ignore=shutil.ignore_patterns('.git','.local','.venv','__pycache__'))
    snapshot(repo)
    registry=base/'registry.yaml'
    registry.write_text(yaml.safe_dump({'indexes':{'public-docs':{'repo':{'url':repo.as_uri(),'branch':'main','submodules':False},'path':'pinakes.yaml'}}}))
    os.environ.pop('AIEXANDRIA_AUTH',None)
    os.environ['XDG_CONFIG_HOME']=str(base/'config')
    cache=base/'cache';client=MCP(args.aiexandria,['--registry',str(registry),'--cache',str(cache)])
    try:
        for attempt in range(30):
            result=client.call('discover_sources',{'query':'Rust ownership'})
            if result.get('catalog',{}).get('complete'):break
            time.sleep(.1)
        assert result.get('catalog',{}).get('complete'),result
        hits=0
        for case in cases:
            result=client.call('discover_sources',{'query':case['query']})
            assert result.get('catalog',{}).get('complete'),result
            sources=result['sources']
            assert len(sources)<=5 and len(json.dumps(result,separators=(',',':'),ensure_ascii=False).encode())<=8192
            paths=[s['search']['path'][-1] for s in sources[:3] if s['search']['path']]
            hit=case['expected'] in paths;hits+=hit
            if not hit:print('Miss:',case['query'],'expected',case['expected'],'got',paths)
        assert len(list(cache.rglob('.git')))==1,'Discovery acquired a doc-only upstream repository'
        print(f'Top-three recall: {hits}/{len(cases)}; discovery acquired only the collection')
        assert hits/len(cases)>=.9
    finally:client.close()
