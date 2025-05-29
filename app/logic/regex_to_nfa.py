class State:
    def __init__(self, name):
        self.name = name
        self.transitions = {}  
        self.is_final = False

class NFA:
    def __init__(self):
        self.states = []
        self.alphabet = set()
        self.initial_state = None
        self.final_states = []
        self.state_counter = 0

    def create_state(self):
        state = State(f"q{self.state_counter}")
        self.state_counter += 1
        self.states.append(state)
        return state

    def add_transition(self, from_state, to_state, symbol):
        if symbol not in from_state.transitions:
            from_state.transitions[symbol] = []
        if to_state not in from_state.transitions[symbol]:
            from_state.transitions[symbol].append(to_state)
        if symbol != '&':  # epsilon menggunakan '&'
            self.alphabet.add(symbol)

    def epsilon_closure(self, states):
        closure = set(states)
        stack = list(states)
        
        while stack:
            state = stack.pop()
            if '&' in state.transitions:  
                for next_state in state.transitions['&']:
                    if next_state not in closure:
                        closure.add(next_state)
                        stack.append(next_state)
        return closure

    def test_string(self, input_string):
        if not self.initial_state:
            return False, []
            
        current_states = self.epsilon_closure([self.initial_state])
        path = [(list(current_states), None)]  
        
        for symbol in input_string:
            if symbol not in self.alphabet:
                return False, path
                
            next_states = set()
            for state in current_states:
                if symbol in state.transitions:
                    next_states.update(state.transitions[symbol])
            
            next_states = self.epsilon_closure(next_states)
            if not next_states: 
                return False, path
                
            current_states = next_states
            path.append((list(current_states), symbol))
        
        is_accepted = any(state in self.final_states for state in current_states)
        return is_accepted, path

class RegexToNFA:
    def __init__(self):
        self.operators = {'|', '*', '(', ')'}
        self.epsilon = '&' # & sbg epsilon

    def create_basic_nfa(self, symbol):
        nfa = NFA()
        start = nfa.create_state()
        end = nfa.create_state()
        end.is_final = True
        nfa.initial_state = start
        nfa.final_states = [end]
        nfa.add_transition(start, end, symbol)
        
        return nfa

    def concatenate(self, nfa1, nfa2):
        result = NFA()
        result.states = nfa1.states + nfa2.states
        result.alphabet = nfa1.alphabet.union(nfa2.alphabet)
        result.initial_state = nfa1.initial_state
        result.final_states = nfa2.final_states
        result.state_counter = max(nfa1.state_counter, nfa2.state_counter)

        for final_state in nfa1.final_states:
            final_state.is_final = False
            result.add_transition(final_state, nfa2.initial_state, self.epsilon)

        return result

    def union(self, nfa1, nfa2):
        result = NFA()
        start = result.create_state()
        end = result.create_state()
        end.is_final = True

        result.states.extend(nfa1.states + nfa2.states)
        result.alphabet = nfa1.alphabet.union(nfa2.alphabet)
        result.initial_state = start
        result.final_states = [end]

        result.add_transition(start, nfa1.initial_state, self.epsilon)
        result.add_transition(start, nfa2.initial_state, self.epsilon)

        for final_state in nfa1.final_states + nfa2.final_states:
            final_state.is_final = False
            result.add_transition(final_state, end, self.epsilon)

        return result

    def kleene_star(self, nfa):
        result = NFA()
        start = result.create_state()
        end = result.create_state()
        end.is_final = True

        result.states.extend(nfa.states)
        result.alphabet = nfa.alphabet
        result.initial_state = start
        result.final_states = [end]

        result.add_transition(start, end, self.epsilon)
        
        result.add_transition(start, nfa.initial_state, self.epsilon)
        
        for final_state in nfa.final_states:
            final_state.is_final = False
            result.add_transition(final_state, end, self.epsilon)
            result.add_transition(final_state, nfa.initial_state, self.epsilon)

        return result

    def infix_to_postfix(self, regex):
        precedence = {'*': 3, '.': 2, '|': 1}
        stack = []
        output = []
        
        explicit_regex = []
        for i in range(len(regex)):
            explicit_regex.append(regex[i])
            if i + 1 < len(regex):
                if (regex[i] not in '(|' and regex[i+1] not in ')|*'):
                    explicit_regex.append('.')

        for char in explicit_regex:
            if char not in self.operators and char != '.':
                output.append(char)
            elif char == '(':
                stack.append(char)
            elif char == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()  
            else:
                while (stack and stack[-1] != '(' and 
                       precedence.get(stack[-1], 0) >= precedence.get(char, 0)):
                    output.append(stack.pop())
                stack.append(char)

        while stack:
            output.append(stack.pop())

        return output

    def regex_to_nfa(self, regex):
        if not regex:
            nfa = NFA()
            start = nfa.create_state()
            end = nfa.create_state()
            end.is_final = True
            nfa.initial_state = start
            nfa.final_states = [end]
            nfa.add_transition(start, end, self.epsilon)
            return nfa

        postfix = self.infix_to_postfix(regex)
        stack = []

        for char in postfix:
            if char not in self.operators and char != '.':
                stack.append(self.create_basic_nfa(char))
            elif char == '*':
                nfa = stack.pop()
                stack.append(self.kleene_star(nfa))
            elif char == '|':
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                stack.append(self.union(nfa1, nfa2))
            elif char == '.':
                nfa2 = stack.pop()
                nfa1 = stack.pop()
                stack.append(self.concatenate(nfa1, nfa2))

        return stack[0]

    def get_nfa_description(self, nfa):
        description = {
            'states': [state.name for state in nfa.states],
            'alphabet': list(nfa.alphabet),
            'initial_state': nfa.initial_state.name,
            'final_states': [state.name for state in nfa.final_states],
            'transitions': {}
        }

        for state in nfa.states:
            description['transitions'][state.name] = {}
            for symbol, next_states in state.transitions.items():
                description['transitions'][state.name][symbol] = [s.name for s in next_states]

        return description
