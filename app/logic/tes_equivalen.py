from collections import deque

def parse_dfa(states, symbols, start, finals, transitions):
    """Parse DFA dengan validasi input yang lebih baik"""
    try:
        # Bersihkan dan split input
        state_set = set(s.strip() for s in states.split(',') if s.strip())
        symbol_set = set(s.strip() for s in symbols.split(',') if s.strip())
        final_set = set(s.strip() for s in finals.split(',') if s.strip())
        start_state = start.strip()
        
        # Validasi start state ada dalam state set
        if start_state not in state_set:
            raise ValueError(f"Start state '{start_state}' tidak ada dalam states")
        
        # Validasi final states ada dalam state set
        invalid_finals = final_set - state_set
        if invalid_finals:
            raise ValueError(f"Final states tidak valid: {invalid_finals}")
        
        # Parse transitions
        transition_lines = [line.strip() for line in transitions.strip().split('\n') if line.strip()]
        transition_dict = {state: {} for state in state_set}
        
        for line in transition_lines:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) != 3:
                raise ValueError(f"Format transisi salah: '{line}'. Gunakan format: state,symbol,target")
            
            from_state, symbol, to_state = parts
            
            # Validasi states dan symbols
            if from_state not in state_set:
                raise ValueError(f"State '{from_state}' tidak ada dalam states")
            if to_state not in state_set:
                raise ValueError(f"Target state '{to_state}' tidak ada dalam states")
            if symbol not in symbol_set:
                raise ValueError(f"Symbol '{symbol}' tidak ada dalam input symbols")
            
            transition_dict[from_state][symbol] = to_state
        
        # Validasi kelengkapan transisi
        for state in state_set:
            for symbol in symbol_set:
                if symbol not in transition_dict[state]:
                    raise ValueError(f"Transisi tidak lengkap: state '{state}' dengan symbol '{symbol}'")
        
        return {
            'states': state_set,
            'symbols': symbol_set,
            'start': start_state,
            'finals': final_set,
            'transitions': transition_dict
        }
    
    except Exception as e:
        raise ValueError(f"Error parsing DFA: {str(e)}")

def are_equivalent(dfa1, dfa2):
    """Cek ekivalensi dua DFA menggunakan algoritma BFS"""
    # Validasi input symbols sama
    if dfa1['symbols'] != dfa2['symbols']:
        return False
    
    visited = set()
    queue = deque([(dfa1['start'], dfa2['start'])])

    while queue:
        s1, s2 = queue.popleft()
        
        # Skip jika sudah dikunjungi
        if (s1, s2) in visited:
            continue
        visited.add((s1, s2))

        # Cek apakah kedua state memiliki status final yang sama
        is_final_1 = s1 in dfa1['finals']
        is_final_2 = s2 in dfa2['finals']
        if is_final_1 != is_final_2:
            return False

        # Cek semua transisi untuk setiap symbol
        for symbol in dfa1['symbols']:
            t1 = dfa1['transitions'].get(s1, {}).get(symbol)
            t2 = dfa2['transitions'].get(s2, {}).get(symbol)
            
            # Jika ada transisi yang tidak terdefinisi, DFA tidak ekivalen
            if t1 is None or t2 is None:
                return False
            
            # Tambahkan pasangan state baru ke queue
            if (t1, t2) not in visited:
                queue.append((t1, t2))

    return True