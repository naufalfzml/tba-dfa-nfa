from flask import Blueprint, render_template, request
from app.logic.regex_to_nfa import RegexToNFA

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/regex-to-nfa', methods=['GET', 'POST'])
def regex_to_nfaview():
    nfa_description = None
    regex_input = ""
    if request.method == 'POST':
        regex_input = request.form.get('regex', '')
        converter = RegexToNFA()
        nfa = converter.regex_to_nfa(regex_input)
        nfa_description = converter.get_nfa_description(nfa)
    return render_template('regex_to_nfa.html', nfa=nfa_description, regex=regex_input)
