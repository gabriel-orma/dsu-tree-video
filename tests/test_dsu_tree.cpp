#include <cstdlib>
#include <iostream>
#include <random>
#include <string>
#include <vector>

#include "../src/dsu_tree.hpp"

namespace {

int failures = 0;
int checks = 0;

void expect(bool cond, const std::string& what) {
    ++checks;
    if (!cond) {
        ++failures;
        std::cerr << "FALLO: " << what << "\n";
    }
}

class NaiveOracle {
public:
    explicit NaiveOracle(int n)
        : n_(n), label_(n + 1), first_(n + 1, std::vector<int>(n + 1, DSUTree::kNone)) {
        for (int i = 1; i <= n; ++i) {
            label_[i] = i;
            first_[i][i] = 0;
        }
    }

    bool unite(int a, int b) {
        int la = label_[a];
        int lb = label_[b];
        if (la == lb) {
            return false;
        }
        ++t_;
        for (int i = 1; i <= n_; ++i) {
            if (label_[i] == lb) {
                label_[i] = la;
            }
        }
        for (int i = 1; i <= n_; ++i) {
            for (int j = 1; j <= n_; ++j) {
                if (first_[i][j] == DSUTree::kNone && label_[i] == label_[j]) {
                    first_[i][j] = t_;
                }
            }
        }
        return true;
    }

    bool connected(int a, int b) const { return label_[a] == label_[b]; }
    int when(int a, int b) const { return first_[a][b]; }

private:
    int n_;
    int t_ = 0;
    std::vector<int> label_;
    std::vector<std::vector<int>> first_;
};

void checkInvariants(const DSUTree& tree, const std::string& ctx) {
    int n = tree.leafCount();
    expect(tree.nodeCount() <= (n == 0 ? 0 : 2 * n - 1), ctx + ": a lo mas 2n-1 nodos");
    for (int v = 1; v <= tree.nodeCount(); ++v) {
        int p = tree.parent(v);
        if (p != DSUTree::kNone) {
            expect(tree.time(p) > tree.time(v), ctx + ": tiempo del padre mayor que el del hijo");
            auto ch = tree.children(p);
            expect(ch.first == v || ch.second == v, ctx + ": hijo registrado en el padre");
        }
        if (!tree.isLeaf(v)) {
            expect(tree.time(v) == v - n, ctx + ": nodo n+t guarda el momento t");
        }
    }
}

void compareAll(DSUTree& tree, const NaiveOracle& oracle, int n, const std::string& ctx) {
    for (int a = 1; a <= n; ++a) {
        for (int b = 1; b <= n; ++b) {
            expect(tree.whenConnected(a, b) == oracle.when(a, b),
                   ctx + ": whenConnected(" + std::to_string(a) + "," + std::to_string(b) + ")");
            expect(tree.connected(a, b) == oracle.connected(a, b),
                   ctx + ": connected(" + std::to_string(a) + "," + std::to_string(b) + ")");
        }
    }
}

void testSingleNode() {
    DSUTree tree(1);
    expect(tree.whenConnected(1, 1) == 0, "n=1: consulta consigo mismo");
    expect(!tree.unite(1, 1), "n=1: unite(1,1) no fusiona");
    expect(tree.nodeCount() == 1, "n=1: no se crean nodos");
    expect(tree.componentCount() == 1, "n=1: una componente");
}

void testEmpty() {
    DSUTree tree(0);
    expect(tree.nodeCount() == 0, "n=0: sin nodos");
    bool threw = false;
    try {
        tree.unite(1, 1);
    } catch (const std::out_of_range&) {
        threw = true;
    }
    expect(threw, "n=0: unite fuera de rango lanza excepcion");
}

void testNoUnions() {
    DSUTree tree(5);
    for (int a = 1; a <= 5; ++a) {
        for (int b = 1; b <= 5; ++b) {
            expect(tree.whenConnected(a, b) == (a == b ? 0 : DSUTree::kNone), "sin uniones");
        }
    }
}

void testRepeatedUnion() {
    DSUTree tree(4);
    expect(tree.unite(1, 2), "union repetida: primera fusiona");
    expect(!tree.unite(2, 1), "union repetida: segunda no fusiona");
    expect(!tree.unite(1, 2), "union repetida: tercera no fusiona");
    expect(tree.nodeCount() == 5, "union repetida: solo un nodo nuevo");
    expect(tree.unite(3, 4), "union repetida: otra componente");
    expect(tree.whenConnected(3, 4) == 2, "union repetida: el tiempo no avanza con uniones fallidas");
}

void testChain() {
    const int n = 2000;
    DSUTree tree(n);
    for (int i = 2; i <= n; ++i) {
        tree.unite(i - 1, i);
    }
    expect(tree.nodeCount() == 2 * n - 1, "cadena: 2n-1 nodos");
    expect(tree.componentCount() == 1, "cadena: una componente");
    expect(tree.whenConnected(1, 2) == 1, "cadena: (1,2) en t=1");
    expect(tree.whenConnected(1, n) == n - 1, "cadena: (1,n) en t=n-1");
    expect(tree.whenConnected(n - 1, n) == n - 1, "cadena: (n-1,n) en t=n-1");
    expect(tree.whenConnected(10, 20) == 19, "cadena: (10,20) en t=19");
    checkInvariants(tree, "cadena");
}

void testDemoScenario() {
    DSUTree tree(6);
    NaiveOracle oracle(6);
    int ops[][2] = {{1, 2}, {3, 4}, {2, 4}, {5, 6}, {1, 3}, {4, 6}};
    for (auto& op : ops) {
        expect(tree.unite(op[0], op[1]) == oracle.unite(op[0], op[1]), "demo: resultado de unite");
    }
    expect(tree.whenConnected(1, 4) == 3, "demo: (1,4) en t=3");
    expect(tree.whenConnected(2, 6) == 5, "demo: (2,6) en t=5");
    compareAll(tree, oracle, 6, "demo");
    checkInvariants(tree, "demo");
}

void testTraceDoesNotChangeResults() {
    std::mt19937 rng(7);
    for (int run = 0; run < 200; ++run) {
        int n = 1 + static_cast<int>(rng() % 10);
        Trace trace;
        DSUTree plain(n);
        DSUTree traced(n, &trace);
        std::uniform_int_distribution<int> pick(1, n);
        for (int k = 0; k < 2 * n; ++k) {
            int a = pick(rng);
            int b = pick(rng);
            expect(plain.unite(a, b) == traced.unite(a, b), "traza: unite igual");
            int x = pick(rng);
            int y = pick(rng);
            expect(plain.whenConnected(x, y) == traced.whenConnected(x, y), "traza: consulta igual");
        }
        expect(trace.size() > 0, "traza: registra eventos");
    }
}

void testRandomAgainstOracle(int runs, unsigned seed) {
    std::mt19937 rng(seed);
    for (int run = 0; run < runs; ++run) {
        int n = 1 + static_cast<int>(rng() % 10);
        DSUTree tree(n);
        NaiveOracle oracle(n);
        std::uniform_int_distribution<int> pick(1, n);
        int ops = static_cast<int>(rng() % (3 * n + 1));
        std::string ctx = "aleatorio run=" + std::to_string(run) + " n=" + std::to_string(n);
        for (int k = 0; k < ops; ++k) {
            int a = pick(rng);
            int b = pick(rng);
            expect(tree.unite(a, b) == oracle.unite(a, b), ctx + ": unite");
            compareAll(tree, oracle, n, ctx);
        }
        checkInvariants(tree, ctx);
    }
}

}

int main() {
    testEmpty();
    testSingleNode();
    testNoUnions();
    testRepeatedUnion();
    testChain();
    testDemoScenario();
    testTraceDoesNotChangeResults();
    testRandomAgainstOracle(5000, 12345);

    std::cout << checks << " verificaciones, " << failures << " fallos\n";
    return failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
