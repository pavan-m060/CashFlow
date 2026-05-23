from collections import defaultdict

def greedy_minimize(transactions):
    net = defaultdict(int)
    for payer, payee, amt in transactions:
        net[payer] -= amt
        net[payee] += amt

    debtors = [(p, b) for p, b in net.items() if b < 0]
    creditors = [(p, b) for p, b in net.items() if b > 0]

    debtors.sort(key=lambda x: x[1])
    creditors.sort(key=lambda x: x[1], reverse=True)

    result = []
    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debtor, dbal = debtors[i]
        creditor, cbal = creditors[j]
        pay = min(-dbal, cbal)

        if pay > 0:
            result.append((debtor, creditor, pay))

        debtors[i] = (debtor, dbal + pay)
        creditors[j] = (creditor, cbal - pay)

        if debtors[i][1] >= 0: i += 1
        if creditors[j][1] <= 0: j += 1

    return result