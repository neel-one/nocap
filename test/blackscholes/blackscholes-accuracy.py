import sys

if __name__ == '__main__':
    regular_f = sys.argv[1]
    nocap_f = sys.argv[2]
    regular_prices = []
    nocap_prices = []

    with open(regular_f) as f:
        f.readline()
        for line in f:
            line = line.strip()
            if line:
                regular_prices.append(float(line))
    f.close()

    with open(nocap_f) as f:
        f.readline()
        for line in f:
            line = line.strip()
            if line:
                nocap_prices.append(float(line))
    f.close()

    if len(regular_prices) != len(nocap_prices):
        print(1.0)

    errors = [abs(p-a) for (p,a) in zip(regular_prices, nocap_prices)]
    max_price = max(regular_prices)
    errors = [min(e / max_price, 1.0) for e in errors]
    print(sum(errors)/len(errors))