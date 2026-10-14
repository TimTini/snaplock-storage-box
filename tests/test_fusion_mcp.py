"""MCP transport sequencing and error propagation without running CAD."""
import importlib.util
import json
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch
from tempfile import TemporaryDirectory
from types import ModuleType, SimpleNamespace
import unittest

PATH=Path(__file__).resolve().parents[1]/'tools/fusion-mcp-test.py'


class FusionMcp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location('fusion_mcp_test',PATH)
        cls.model=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.model)

    def connection(self, results):
        responses=[]
        for index,value in enumerate(results):
            if 'result' in value or 'error' in value:
                value=dict(value,id=1 if index==0 else 2)
            responses.append(Mock(status=200, read=lambda value=value:json.dumps(value).encode(),
                                  getheader=lambda name:'test-session' if name=='MCP-Session-Id' else None))
        connection=Mock()
        connection.getresponse.side_effect=responses
        return connection

    def test_initialize_notification_and_tool_share_connection(self):
        c=self.connection([{'result':{}},{},{'result':{'content':[]}}])
        result=self.model.call(c,'tools/call',{'name':'fusion_mcp_execute','arguments':{}})
        self.assertEqual(result,{'content':[]})
        requests=[json.loads(call.args[2]) for call in c.request.call_args_list]
        self.assertEqual([r['method'] for r in requests],
                         ['initialize','notifications/initialized','tools/call'])
        self.assertEqual(c.request.call_args_list[-1].args[3]['MCP-Session-Id'],'test-session')
        self.assertEqual(c.request.call_args_list[-1].args[3]['Accept'],'application/json')

    def test_jsonrpc_error_is_raised(self):
        c=self.connection([{'result':{}},{},{'error':{'code':-32600,'message':'Session not initialized'}}])
        with self.assertRaisesRegex(RuntimeError,'Session not initialized'):
            self.model.call(c,'tools/list',{})

    def test_tool_error_is_raised(self):
        c=self.connection([{'result':{}},{},{'result':{'isError':True,
                          'content':[{'type':'text','text':'Native loft failed'}]}}])
        with self.assertRaisesRegex(RuntimeError,'Native loft failed'):
            self.model.call(c,'tools/call',{})

    def test_nested_fusion_failure_is_raised(self):
        c=self.connection([{'result':{}},{},{'result':{'content':[{'type':'text',
                           'text':json.dumps({'success':False,'message':'Close command dialog'})}]}}])
        with self.assertRaisesRegex(RuntimeError,'Close command dialog'):
            self.model.call(c,'tools/call',{})

    def test_empty_accepted_response_is_not_a_completed_request(self):
        c=self.connection([{'result':{}},{},{}])
        responses=list(c.getresponse.side_effect)
        responses[-1]=Mock(status=202,read=lambda:b'',getheader=lambda name:None)
        c.getresponse.side_effect=responses
        with self.assertRaisesRegex(RuntimeError,'completed JSON-RPC'):
            self.model.call(c,'tools/call',{})

    def test_request_without_matching_result_is_rejected(self):
        c=self.connection([{'result':{}},{},{'id':2}])
        with self.assertRaisesRegex(RuntimeError,'JSON-RPC result'):
            self.model.call(c,'tools/list',{})

    def test_native_failure_keeps_previous_production_log(self):
        adsk=ModuleType('adsk')
        adsk.core=ModuleType('adsk.core')
        adsk.fusion=ModuleType('adsk.fusion')
        adsk.core.Application=SimpleNamespace(get=lambda:SimpleNamespace(version='fixture'))
        with TemporaryDirectory() as temp:
            root=Path(temp)
            folder=root/'fusion/SnaplockStorageBox'
            folder.mkdir(parents=True)
            (folder/'SnaplockStorageBox.py').write_text(
                "DEFAULTS={}\ndef dimensions(p):\n    raise RuntimeError('fixture stop')\n")
            previous=folder/'last-run.log'
            previous.write_text('previous evidence')
            run_folder=root/'work/isolated-run'
            run_folder.mkdir(parents=True)
            wrapper=PATH.parents[1]/'fusion/tests/McpNativeTest/native_test.py'
            with patch.dict('sys.modules',{'adsk':adsk,'adsk.core':adsk.core,'adsk.fusion':adsk.fusion}):
                spec=importlib.util.spec_from_file_location('native_log_test',wrapper)
                module=importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module.PROJECT_ROOT=str(root)
                module.RUN_DIRECTORY=str(run_folder)
                with self.assertRaisesRegex(RuntimeError,'fixture stop'):
                    module.run('')
            self.assertEqual(previous.read_text(),'previous evidence')
            self.assertIn('Validate dimensions',(run_folder/'native-test.log').read_text())
