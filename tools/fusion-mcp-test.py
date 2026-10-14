"""Inspect local Fusion by default; --run creates and tests a new CAD document."""
import argparse
from datetime import datetime
import http.client
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]


def call(connection, method, params):
    headers={'Content-Type':'application/json','Accept':'application/json'}
    def rpc(payload):
        connection.request('POST','/mcp',json.dumps(payload),dict(headers))
        response=connection.getresponse()
        body=response.read()
        if response.status not in (200,202):
            raise RuntimeError('Fusion MCP HTTP '+str(response.status)+': '+body.decode())
        session=response.getheader('MCP-Session-Id')
        if session:
            headers['MCP-Session-Id']=session
        data=json.loads(body) if body else {}
        if 'error' in data:
            raise RuntimeError(json.dumps(data['error']))
        if 'id' in payload:
            if response.status!=200 or not body:
                raise RuntimeError('Expected a completed JSON-RPC response')
            if data.get('id')!=payload['id'] or 'result' not in data:
                raise RuntimeError('Expected matching JSON-RPC result')
        return data.get('result',{})
    rpc({'jsonrpc':'2.0','id':1,'method':'initialize','params':{
        'protocolVersion':'2024-11-05','capabilities':{},
        'clientInfo':{'name':'Snaplock native validation','version':'1'}}})
    rpc({'jsonrpc':'2.0','method':'notifications/initialized'})
    result=rpc({'jsonrpc':'2.0','id':2,'method':method,'params':params})
    if result.get('isError'):
        raise RuntimeError(json.dumps(result))
    for block in result.get('content',[]):
        if block.get('type')=='text' and block['text'].lstrip().startswith('{'):
            data=json.loads(block['text'])
            if data.get('success') is False:
                raise RuntimeError(json.dumps(data))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--run',action='store_true',help='Create a new document and run native validation')
    mode.add_argument('--list-tools',action='store_true',help='Discover the current Fusion MCP tool schemas')
    parser.add_argument('--port',type=int,default=27182,help='Port shown in Fusion Preferences > API')
    args=parser.parse_args()
    output=ROOT/'work/fusion-mcp'/datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    output.mkdir(parents=True)
    if args.list_tools:
        method,params='tools/list',{}
    else:
        if args.run:
            wrapper=ROOT/'fusion/tests/McpNativeTest/native_test.py'
            script=('PROJECT_ROOT = '+repr(str(ROOT))+'\nRUN_DIRECTORY = '+repr(str(output))+'\n'+
                    wrapper.read_text(encoding='utf-8'))
            print('Native test dispatched; progress: '+str(output/'native-test.log'),flush=True)
        else:
            script="""import adsk.core
def run(_context: str):
    app=adsk.core.Application.get()
    print('Fusion version: '+app.version)
    print('Open documents: '+str(app.documents.count))
    print('Active command: '+app.userInterface.activeCommand)
"""
        method='tools/call'
        params={'name':'fusion_mcp_execute','arguments':{'featureType':'script',
                'object':{'script':script,'readOnly':not args.run}}}
    connection=http.client.HTTPConnection('127.0.0.1',args.port,timeout=1800)
    try:
        result=call(connection,method,params)
    finally:
        connection.close()
    (output/'response.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps([tool['name'] for tool in result['tools']] if args.list_tools else result,
                     ensure_ascii=False))
    print('Local response: '+str(output/'response.json'))


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
