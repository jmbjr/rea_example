"""Small interpreter for the validated neutral subset, not Minesweeper rules."""
from copy import deepcopy
from dodge_common import matches, require

class Runtime:
    def __init__(self, model, scenario_id):
        self.rules = deepcopy(model['rules'])
        choices = [s for s in model['scenarios'] if s['id'] == scenario_id]
        require(len(choices) == 1, 'scenario must resolve exactly once')
        self.scope = deepcopy(choices[0])
        self.trace = []

    def instance(self, instance_id):
        items = [x for x in self.scope['inventory'] if x['instance_id'] == instance_id]
        require(len(items) == 1, 'instance must resolve exactly once')
        return items[0]

    def _values(self, subject, context):
        if 'instance_ref' in subject:
            return self.instance(subject['instance_ref'])['values']
        slot = subject['relative']
        if slot == 'scenario':
            return self.scope['values']
        require(slot in context, 'required execution context missing')
        return self.instance(context[slot])['values']

    def _condition(self, ref, context):
        condition = self.rules['conditions'][ref]
        require(condition['op'] == 'eq', 'unsupported predicate')
        operand = condition['left']
        actual = self._values(operand['subject'], context)[operand['ref']]
        return type(actual) is type(condition['right']) and actual == condition['right']

    def _effect(self, ref, context):
        effect = self.rules['effects'][ref]
        values = self._values(effect['subject'], context)
        target = effect['target_ref']
        before = deepcopy(values.get(target, {'unset': True}))
        if effect['op'] == 'set':
            after = effect['value']
        elif effect['op'] == 'add':
            after = values[target] + effect['value']
        elif effect['op'] == 'subtract':
            after = values[target] - effect['value']
        else:
            raise ValueError('unsupported effect operation')
        matches(self.rules['values'][target], after)
        values[target] = deepcopy(after)
        self.trace.append(dict(kind='effect', ref=ref, subject=effect['subject'], before=before, after=after))

    def _steps(self, steps, context, depth=0):
        require(depth < 100, 'execution depth exceeded')
        for step in steps:
            kind = step['kind']
            if kind == 'effect':
                self._effect(step['ref'], context)
            elif kind == 'procedure':
                self._steps(self.rules['procedures'][step['ref']]['steps'], context, depth + 1)
            elif kind == 'action':
                require(step['ref'] in self.scope['action_refs'], 'action unavailable')
                action = self.rules['actions'][step['ref']]
                self.trace.append(dict(kind='action', ref=step['ref']))
                self._steps(self.rules['procedures'][action['procedure_ref']]['steps'], context, depth + 1)
            elif kind == 'branch':
                selected = step['else_steps']
                for branch in step['branches']:
                    satisfied = self._condition(branch['condition'], context)
                    self.trace.append(dict(kind='predicate', ref=branch['condition'], satisfied=satisfied))
                    if satisfied:
                        selected = branch['steps']
                        break
                self._steps(selected, context, depth + 1)
            else:
                raise ValueError('unsupported step kind')

    def invoke(self, instance_id, invocation_id):
        item = self.instance(instance_id)
        choices = [x for x in item['invocations'] if x['id'] == invocation_id]
        require(len(choices) == 1, 'explicit invocation missing or ambiguous')
        invocation = choices[0]
        context = {}
        for binding in invocation['subject_bindings']:
            require(binding['source'] == 'using-object', 'unsupported context source')
            context[binding['slot']] = instance_id
        before, previous_trace = deepcopy(self.scope), deepcopy(self.trace)
        self.trace = []
        try:
            self._steps(invocation['steps'], context)
        except Exception:
            self.scope, self.trace = before, previous_trace
            raise
        return deepcopy(self.trace)
