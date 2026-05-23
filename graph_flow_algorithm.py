import networkx as nx

def graph_flow_minimize(transactions):
    G = nx.DiGraph()
    balance = {}

    for payer, payee, amt in transactions:
        balance.setdefault(payer, 0)
        balance.setdefault(payee, 0)
        balance[payer] -= amt
        balance[payee] += amt
        G.add_edge(payer, payee, capacity=amt, weight=1)

    source = "__SOURCE__"
    sink = "__SINK__"
    G.add_node(source)
    G.add_node(sink)

    for person, bal in balance.items():
        if bal > 0:
            G.add_edge(source, person, capacity=bal, weight=0)
        elif bal < 0:
            G.add_edge(person, sink, capacity=-bal, weight=0)

    try:
        flow_cost, flow_dict = nx.network_simplex(G)
    except nx.NetworkXUnfeasible:
        return []

    result = []
    for u in flow_dict:
        for v in flow_dict[u]:
            flow = flow_dict[u][v]
            if flow > 0 and u != source and v != sink:
                result.append((u, v, flow))

    return result