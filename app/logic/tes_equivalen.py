from automata.fa.dfa import DFA

def cek_ekuivalensi(dfa1_data, dfa2_data):
    try:
        # Bangun DFA 1
        dfa1 = DFA(
            states=set(dfa1_data['states']),
            input_symbols=set(dfa1_data['input_symbols']),
            transitions=dfa1_data['transitions'],
            initial_state=dfa1_data['initial_state'],
            final_states=set(dfa1_data['final_states'])
        )

        # Bangun DFA 2
        dfa2 = DFA(
            states=set(dfa2_data['states']),
            input_symbols=set(dfa2_data['input_symbols']),
            transitions=dfa2_data['transitions'],
            initial_state=dfa2_data['initial_state'],
            final_states=set(dfa2_data['final_states'])
        )

        # Cek ekivalensi
        return dfa1.minify() == dfa2.minify(), None

    except Exception as e:
        return False, str(e)
