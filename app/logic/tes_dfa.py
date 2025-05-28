def parse_transitions(transition_input):
    transition_dict = {}
    transitions = transition_input.split(',')
    for t in transitions:
        parts = t.strip().split()
        if len(parts) == 3:
            from_state, symbol, to_state = parts
            transition_dict[(from_state, symbol)] = to_state
    return transition_dict

def run_dfa(states, alphabet, start_state, accept_states, transitions_input, test_string):
    result = []
    transitions = parse_transitions(transitions_input)
    current_state = start_state
    rejected_due_to_error = False

    for symbol in test_string:
        key = (current_state, symbol)
        next_state = transitions.get(key)
        result.append((symbol, current_state, next_state))

        if next_state is None:
            rejected_due_to_error = True
            break 

        current_state = next_state

    accepted = not rejected_due_to_error and current_state in accept_states
    return result, accepted