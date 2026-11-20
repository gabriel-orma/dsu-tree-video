#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <vector>

#include "../src/dsu_tree.hpp"

namespace {

using Clock = std::chrono::steady_clock;

double nanosPer(Clock::time_point start, Clock::time_point stop, long long ops) {
    return std::chrono::duration<double, std::nano>(stop - start).count() / static_cast<double>(ops);
}

int treeHeight(const DSUTree& tree) {
    std::vector<int> depth(tree.nodeCount() + 1, 0);
    int best = 0;
    for (int v = tree.nodeCount(); v >= 1; --v) {
        int p = tree.parent(v);
        if (p != DSUTree::kNone) {
            depth[v] = depth[p] + 1;
        }
        best = std::max(best, depth[v]);
    }
    return best;
}

volatile long long sink = 0;

struct Sample {
    double unite;
    double query;
    int height;
};

Sample randomCase(int n, unsigned seed) {
    std::mt19937 rng(seed);
    std::uniform_int_distribution<int> pick(1, n);
    DSUTree tree(n);
    std::vector<std::pair<int, int>> pairs;
    {
        DSUTree probe(n);
        while (probe.componentCount() > 1) {
            int a = pick(rng);
            int b = pick(rng);
            probe.unite(a, b);
            pairs.push_back({a, b});
        }
    }
    auto start = Clock::now();
    for (const auto& [a, b] : pairs) {
        sink += tree.unite(a, b);
    }
    auto stop = Clock::now();
    double unite = nanosPer(start, stop, static_cast<long long>(pairs.size()));

    const int queries = std::max(2000, 200000000 / n);
    std::vector<int> qa(queries), qb(queries);
    for (int i = 0; i < queries; ++i) {
        qa[i] = pick(rng);
        qb[i] = pick(rng);
    }
    start = Clock::now();
    for (int i = 0; i < queries; ++i) {
        sink += tree.whenConnected(qa[i], qb[i]);
    }
    stop = Clock::now();
    return {unite, nanosPer(start, stop, queries), treeHeight(tree)};
}

Sample chainCase(int n) {
    DSUTree tree(n);
    auto start = Clock::now();
    for (int i = 2; i <= n; ++i) {
        sink += tree.unite(i - 1, i);
    }
    auto stop = Clock::now();
    double unite = nanosPer(start, stop, n - 1);

    const int queries = std::max(10, 20000000 / n);
    start = Clock::now();
    for (int i = 0; i < queries; ++i) {
        sink += tree.whenConnected(1 + (i % 2), n);
    }
    stop = Clock::now();
    return {unite, nanosPer(start, stop, queries), treeHeight(tree)};
}

double median(std::vector<double> values) {
    std::sort(values.begin(), values.end());
    return values[values.size() / 2];
}

void report(const char* label, int n, std::vector<double> unite, std::vector<double> query, int height) {
    std::printf("%s,%d,%.2f,%.2f,%d\n", label, n, median(unite), median(query), height);
    std::fflush(stdout);
}

}

int main(int argc, char** argv) {
    const int repetitions = 5;
    const int maxN = argc > 1 ? std::atoi(argv[1]) : 1000000;
    const int sizes[] = {1000, 10000, 100000, 1000000};
    std::printf("caso,n,unite_ns,query_ns,altura\n");
    for (int n : sizes) {
        if (n > maxN) {
            break;
        }
        std::vector<double> unite, query;
        int height = 0;
        for (int r = 0; r < repetitions; ++r) {
            Sample s = randomCase(n, 1000u + static_cast<unsigned>(r));
            unite.push_back(s.unite);
            query.push_back(s.query);
            height = s.height;
        }
        report("aleatorio", n, unite, query, height);
    }
    for (int n : sizes) {
        if (n > maxN) {
            break;
        }
        std::vector<double> unite, query;
        int height = 0;
        for (int r = 0; r < repetitions; ++r) {
            Sample s = chainCase(n);
            unite.push_back(s.unite);
            query.push_back(s.query);
            height = s.height;
        }
        report("cadena", n, unite, query, height);
    }
    std::fprintf(stderr, "%lld\n", static_cast<long long>(sink));
    return 0;
}
