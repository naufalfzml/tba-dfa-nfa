from collections import deque

def parse_dfa(states, symbols, start, finals, transitions):
    state_set = set(states.split(','))
    symbol_set = set(symbols.split(','))
    final_set = set(finals.split(','))
    transition_lines = transitions.strip().split('\n')
    
    transition_dict = {state: {} for state in state_set}
    for line in transition_lines:
        from_state, symbol, to_state = line.strip().split(',')
        transition_dict[from_state][symbol] = to_state
    return {
        'states': state_set,
        'symbols': symbol_set,
        'start': start,
        'finals': final_set,
        'transitions': transition_dict
    }

def are_equivalent(dfa1, dfa2):
    visited = set()
    queue = deque([(dfa1['start'], dfa2['start'])])

    while queue:
        s1, s2 = queue.popleft()
        if (s1, s2) in visited:
            continue
        visited.add((s1, s2))

        is_final_1 = s1 in dfa1['finals']
        is_final_2 = s2 in dfa2['finals']
        if is_final_1 != is_final_2:
            return False

        for symbol in dfa1['symbols']:
            t1 = dfa1['transitions'].get(s1, {}).get(symbol)
            t2 = dfa2['transitions'].get(s2, {}).get(symbol)
            if t1 is None or t2 is None:
                continue
            queue.append((t1, t2))

    return True
