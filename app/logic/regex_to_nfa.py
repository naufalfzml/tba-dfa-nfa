class State:
    def __init__(self, name):
        self.name = name
        self.transitions = {}  # {symbol: [states]}
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
        if symbol != '&':  # epsilon represented as '&'
            self.alphabet.add(symbol)

class RegexToNFA:
    def __init__(self):
        self.operators = {'|', '*', '(', ')'}
        self.epsilon = '&'  # Using & as epsilon symbol

    def create_basic_nfa(self, symbol):
        """Create NFA for a single symbol"""
        nfa = NFA()
        start = nfa.create_state()
        end = nfa.create_state()
        end.is_final = True
        
        nfa.initial_state = start
        nfa.final_states = [end]
        nfa.add_transition(start, end, symbol)
        
        return nfa

    def concatenate(self, nfa1, nfa2):
        """Concatenate two NFAs"""
        result = NFA()
        result.states = nfa1.states + nfa2.states
        result.alphabet = nfa1.alphabet.union(nfa2.alphabet)
        result.initial_state = nfa1.initial_state
        result.final_states = nfa2.final_states
        result.state_counter = max(nfa1.state_counter, nfa2.state_counter)

        # Connect final states of nfa1 to initial state of nfa2 with epsilon
        for final_state in nfa1.final_states:
            final_state.is_final = False
            result.add_transition(final_state, nfa2.initial_state, self.epsilon)

        return result

    def union(self, nfa1, nfa2):
        """Create union of two NFAs"""
        result = NFA()
        start = result.create_state()
        end = result.create_state()
        end.is_final = True

        result.states.extend(nfa1.states + nfa2.states)
        result.alphabet = nfa1.alphabet.union(nfa2.alphabet)
        result.initial_state = start
        result.final_states = [end]

        # Connect new start state to both NFAs' start states
        result.add_transition(start, nfa1.initial_state, self.epsilon)
        result.add_transition(start, nfa2.initial_state, self.epsilon)

        # Connect both NFAs' final states to new final state
        for final_state in nfa1.final_states + nfa2.final_states:
            final_state.is_final = False
            result.add_transition(final_state, end, self.epsilon)

        return result

    def kleene_star(self, nfa):
        """Apply Kleene star operation to NFA"""
        result = NFA()
        start = result.create_state()
        end = result.create_state()
        end.is_final = True

        result.states.extend(nfa.states)
        result.alphabet = nfa.alphabet
        result.initial_state = start
        result.final_states = [end]

        # Connect start to end with epsilon (for empty string)
        result.add_transition(start, end, self.epsilon)
        
        # Connect start to nfa's start
        result.add_transition(start, nfa.initial_state, self.epsilon)
        
        # Connect nfa's final states to nfa's start (for repetition)
        for final_state in nfa.final_states:
            final_state.is_final = False
            result.add_transition(final_state, end, self.epsilon)
            result.add_transition(final_state, nfa.initial_state, self.epsilon)

        return result

    def infix_to_postfix(self, regex):
        """Convert infix regex to postfix notation"""
        precedence = {'*': 3, '.': 2, '|': 1}
        stack = []
        output = []
        
        # Add explicit concatenation operator '.'
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
                stack.pop()  # Remove '('
            else:
                while (stack and stack[-1] != '(' and 
                       precedence.get(stack[-1], 0) >= precedence.get(char, 0)):
                    output.append(stack.pop())
                stack.append(char)

        while stack:
            output.append(stack.pop())

        return output

    def regex_to_nfa(self, regex):
        """Convert regex to NFA"""
        if not regex:
            # Create NFA that accepts empty string
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
        """Get a readable description of the NFA"""
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
