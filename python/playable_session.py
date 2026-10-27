"""Thin session boundary over validated model execution; no flood/win rules."""
from copy import deepcopy
from dodge_common import require
from neutral_runtime import Runtime

class PlayableSession:
    def __init__(self, model, scenario_id):
        self.model = model
        self.scenario_id = scenario_id
        self.reset()

    def reset(self):
        self.runtime = Runtime(self.model, self.scenario_id)
        self.terminal = None
        return self.view()

    def snapshot(self):
        """Full oracle projection for tests; do not expose hidden grid in the UI."""
        values = self.runtime.scope['values']
        cells = sorted(self.runtime.scope['inventory'],key=lambda x:(x['values']['cell-row'],x['values']['cell-column']))
        result = {k:values[k] for k in ['rows','columns','mines','flags','generation']}
        result.update(grid=''.join(x['values']['cell-grid'] for x in cells),
                      visible=''.join(x['values']['cell-visible'] for x in cells),
                      undo_index=values['undo-index'],undo_enabled=values['undo-enabled'],
                      grid_initialized=values['grid-initialized'],
                      won=int(self.runtime._condition(self.scenario_id+'-won',{})))
        return result

    def view(self):
        snapshot = self.snapshot()
        return {k:snapshot[k] for k in ['rows','columns','mines','flags','visible']} | dict(outcome=self.terminal)

    def move(self, trigger, row, column):
        require(self.terminal is None, 'session is terminal; restart to play again')
        require(type(row) is int and type(column) is int and 0 <= row < self.runtime.scope['values']['rows'] and 0 <= column < self.runtime.scope['values']['columns'], 'coordinate outside the admitted board')
        record = self.core_move(trigger,row,column)
        self.terminal = self.runtime.outcome()
        return dict(result=record['result'],outcome=self.terminal,board=self.view())

    def core_move(self, trigger, row, column):
        """Direct-call comparison interface. The UI must use move()."""
        require(trigger in ('dig','flag','unflag'), 'unknown input trigger')
        require(type(row) is int and type(column) is int, 'coordinates must be integers')
        cells = [x for x in self.runtime.scope['inventory'] if
                 x['values']['cell-row'] == row and x['values']['cell-column'] == column]
        if not cells and trigger == 'dig':
            cells = self.runtime.scope['inventory'][:1]
            trigger = 'dig-outside'
        require(len(cells) == 1, 'coordinate outside the admitted board')
        choices = [x for x in cells[0]['invocations'] if x['trigger'] == trigger]
        require(len(choices) == 1, 'missing/ambiguous invocation')
        before = self.snapshot()
        self.runtime.invoke(cells[0]['instance_id'],choices[0]['id'])
        return dict(before=before,after=self.snapshot(),result=self.runtime.scope['values']['result'])
