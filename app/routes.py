from flask import Blueprint, render_template, request
from app.logic.tes_dfa import run_dfa
from app.logic.regex_to_nfa import RegexToNFA
from app.logic.minimization_dfa import DFA
from app.logic.minimization_dfa import build_and_minimize_dfa
from app.logic.tes_equivalen import parse_dfa, are_equivalent

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/tes-dfa', methods=["GET", "POST"])
def tes_dfa():
    output = None
    result_steps = []
    
    if request.method == "POST":
        states = request.form["states"].split()
        alphabet = request.form["alphabet"].split()
        start_state = request.form["start_state"]
        accept_states = request.form["accept_states"].split()
        transitions_input = request.form["transitions"]
        test_string = request.form["test_string"]

        result_steps, accepted = run_dfa(states, alphabet, start_state, accept_states, transitions_input, test_string)
        output = "Accepted" if accepted else "Rejected"

    return render_template("tes_dfa.html", result=output, steps=result_steps)

@main.route('/minimization', methods=['GET', 'POST'])
def minimization():
    if request.method == 'POST':
        try:
            # Parsing input dengan pembersihan yang lebih baik
            states = [s.strip() for s in request.form["states"].split(",") if s.strip()]
            alphabet = [a.strip() for a in request.form["alphabet"].split(",") if a.strip()]
            start_state = request.form["start_state"].strip()
            final_states = [s.strip() for s in request.form["final_states"].split(",") if s.strip()]
            raw_transitions = request.form["transitions"].strip().splitlines()

            transitions = {}
            for line in raw_transitions:
                line = line.strip()
                if not line:
                    continue

                # Pisahkan berdasarkan koma dan hapus spasi ekstra
                parts = [x.strip() for x in line.split(',')]
                
                if len(parts) >= 3:
                    state = parts[0].strip()
                    symbol = parts[1].strip()
                    target = parts[2].strip()
                    transitions[f"{state},{symbol}"] = target
                else:
                    # Skip baris yang formatnya salah
                    continue

            input_data = {
                "states": states,
                "alphabet": alphabet,
                "start_state": start_state,
                "final_states": final_states,
                "transitions": transitions
            }

            result = build_and_minimize_dfa(input_data)
            return render_template("minimization.html", result=result)
            
        except Exception as e:
            error_msg = str(e)
            return render_template("minimization.html", error=error_msg)

    return render_template("minimization.html")

@main.route('/regex-to-nfa', methods=['GET', 'POST'])
def regex_to_nfaview():
    nfa_description = None
    regex_input = ""
    test_result = None
    test_path = None
    test_string = ""
    
    if request.method == 'POST':
        regex_input = request.form.get('regex', '')
        test_string = request.form.get('test_string', '')
        converter = RegexToNFA()
        nfa = converter.regex_to_nfa(regex_input)
        nfa_description = converter.get_nfa_description(nfa)
        
        if test_string:
            is_accepted, path = nfa.test_string(test_string)
            test_result = is_accepted
            test_path = []
            for states, symbol in path:
                state_names = [state.name for state in states]
                test_path.append({
                    'states': state_names,
                    'symbol': symbol if symbol is not None else 'ε'
                })
    
    return render_template('regex_to_nfa.html', 
                         nfa=nfa_description, 
                         regex=regex_input,
                         test_string=test_string,
                         test_result=test_result,
                         test_path=test_path)

@main.route('/equivalence', methods=['POST'])
def check_equivalence():
    try:
        # Ambil data dari form
        states1 = request.form["states1"]
        symbols1 = request.form["symbols1"]
        start1 = request.form["start1"]
        finals1 = request.form["final1"]
        transitions1 = request.form["transitions1"]

        states2 = request.form["states2"]
        symbols2 = request.form["symbols2"]
        start2 = request.form["start2"]
        finals2 = request.form["final2"]
        transitions2 = request.form["transitions2"]

        # Parsing kedua DFA
        dfa1 = parse_dfa(states1, symbols1, start1, finals1, transitions1)
        dfa2 = parse_dfa(states2, symbols2, start2, finals2, transitions2)

        # Cek ekivalensi
        equivalent = are_equivalent(dfa1, dfa2)
        result = "Kedua DFA adalah ekuivalen." if equivalent else "Kedua DFA **tidak** ekuivalen."

        return render_template("equivalence.html", result=result)
    
    except Exception as e:
        return render_template("equivalence.html", error=str(e))

