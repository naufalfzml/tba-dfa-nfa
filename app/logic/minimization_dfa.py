from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64

class DFA:
    def __init__(self, states, alphabet, start_state, final_states, transitions):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.start_state = start_state
        self.final_states = set(final_states)
        self.transitions = {tuple(k): v for k, v in transitions.items()}

    def transition(self, state, symbol):
        return self.transitions.get((state, symbol))

    def get_partition_index(self, state, partitions):
        for i, group in enumerate(partitions):
            if state in group:
                return i
        return None

    def minimize(self):
        non_final = self.states - self.final_states
        partitions = [self.final_states, non_final]

        while True:
            new_partitions = []
            for group in partitions:
                grouped = defaultdict(set)
                for state in group:
                    signature = tuple(
                        self.get_partition_index(self.transition(state, symbol), partitions)
                        for symbol in self.alphabet
                    )
                    grouped[signature].add(state)
                new_partitions.extend(grouped.values())
            if new_partitions == partitions:
                break
            partitions = new_partitions

        minimized_states = {frozenset(p): f'Q{i}' for i, p in enumerate(partitions)}
        minimized_transitions = {}
        minimized_final_states = set()
        minimized_start_state = None

        for group in partitions:
            representative = next(iter(group))
            group_name = minimized_states[frozenset(group)]

            if representative in self.final_states:
                minimized_final_states.add(group_name)
            if self.start_state in group:
                minimized_start_state = group_name

            for symbol in self.alphabet:
                target = self.transition(representative, symbol)
                if target is not None:
                    for g in partitions:
                        if target in g:
                            target_group_name = minimized_states[frozenset(g)]
                            minimized_transitions[(group_name, symbol)] = target_group_name
                            break

        return DFA(
            states=set(minimized_states.values()),
            alphabet=self.alphabet,
            start_state=minimized_start_state,
            final_states=minimized_final_states,
            transitions=minimized_transitions
        )

    def draw(self):
        G = nx.MultiDiGraph()
        edge_labels = {}

        for state in self.states:
            G.add_node(state)

        for (state, symbol), target in self.transitions.items():
            G.add_edge(state, target)
            if (state, target) in edge_labels:
                edge_labels[(state, target)] += f", {symbol}"
            else:
                edge_labels[(state, target)] = symbol

        pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', edgecolors='black', node_size=1200)
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle='->', connectionstyle='arc3,rad=0.2')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        plt.text(pos[self.start_state][0] - 0.15, pos[self.start_state][1] + 0.1, "→", fontsize=20, color='green')
        plt.axis('off')

        # Simpan ke base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return img_base64

    def to_dict(self):
        return {
            "states": list(self.states),
            "alphabet": list(self.alphabet),
            "start_state": self.start_state,
            "final_states": list(self.final_states),
            "transitions": {f"{k[0]},{k[1]}": v for k, v in self.transitions.items()}
        }


def build_and_minimize_dfa(input_data):
    dfa = DFA(
        states=input_data["states"],
        alphabet=input_data["alphabet"],
        start_state=input_data["start_state"],
        final_states=input_data["final_states"],
        transitions={tuple(k.split(",")): v for k, v in input_data["transitions"].items()}
    )

    minimized_dfa = dfa.minimize()
    img_base64 = minimized_dfa.draw()

    return {
        "original": dfa.to_dict(),
        "minimized": minimized_dfa.to_dict(),
        "image_base64": img_base64
    }