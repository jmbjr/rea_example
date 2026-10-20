"""Native fixture protocol and output formatting; no transition rules."""
from dodge_common import fixture_records, read_json, require
from neutral_runtime import Runtime

class FlagSession:
    def __init__(self, model, scenario_id, root):
        self.runtime = Runtime(model, scenario_id)
        self.messages = {}
        for source in model['sources'].values():
            if source['kind'] == 'scenario' and source['version'] == 'milestone-5':
                for record in fixture_records(read_json(root / source['uri']))[1:]:
                    code, message = record['result'], record['message']
                    require(code not in self.messages or self.messages[code] == message, 'message source conflict')
                    self.messages[code] = message

    def snapshot(self):
        values = self.runtime.scope['values']
        cells = sorted(self.runtime.scope['inventory'], key=lambda x: (x['values']['cell-row'], x['values']['cell-column']))
        result = {key: values[key] for key in ['rows', 'columns', 'mines', 'flags', 'generation']}
        result.update(visible=''.join(x['values']['cell-visible'] for x in cells),
                      undo_index=values['undo-index'], undo_enabled=values['undo-enabled'],
                      grid_initialized=values['grid-initialized'])
        return result

    def command(self, line):
        parts = line.split()
        require(len(parts) == 3 and parts[0] in ['f', 'u'], 'expected f ROW COL or u ROW COL')
        letter, row, column = parts[0], int(parts[1]), int(parts[2])
        cells = [x for x in self.runtime.scope['inventory'] if
                 x['values']['cell-row'] == row and x['values']['cell-column'] == column]
        require(len(cells) == 1, 'coordinate is outside the admitted scope')
        # Letters select input triggers, not action implementation or game outcomes.
        trigger = {'f': 'flag', 'u': 'unflag'}[letter]
        invocations = [x for x in cells[0]['invocations'] if x['trigger'] == trigger]
        require(len(invocations) == 1, 'input has no explicit invocation')
        before = self.snapshot()
        self.runtime.invoke(cells[0]['instance_id'], invocations[0]['id'])
        code = self.runtime.scope['values']['result']
        return dict(action=letter, row=row, column=column, before=before,
                    result=code, message=self.messages[code], after=self.snapshot())
