#include "dsu_tree.hpp"

#include <stdexcept>
#include <string>

DSUTree::DSUTree(int n, Trace* trace) : n_(n), trace_(trace) {
    if (n < 0) {
        throw std::invalid_argument("n debe ser >= 0");
    }
    int capacity = 2 * n;
    dsuParent_.resize(n + 1);
    dsuSize_.assign(n + 1, 1);
    compNode_.resize(n + 1);
    for (int i = 0; i <= n; ++i) {
        dsuParent_[i] = i;
        compNode_[i] = i;
    }
    treeParent_.assign(capacity, kNone);
    treeTime_.assign(capacity, 0);
    treeChildren_.assign(capacity, {kNone, kNone});

    if (trace_) {
        trace_->push(Trace::Event("init").field("n", n));
    }
}

void DSUTree::checkLeaf(int x) const {
    if (x < 1 || x > n_) {
        throw std::out_of_range("nodo fuera de rango: " + std::to_string(x));
    }
}

int DSUTree::find(int x) {
    std::vector<int> path;
    int root = x;
    while (dsuParent_[root] != root) {
        if (trace_) {
            path.push_back(root);
        }
        root = dsuParent_[root];
    }
    if (trace_) {
        path.push_back(root);
    }

    std::vector<std::pair<int, int>> compressed;
    while (dsuParent_[x] != root) {
        int next = dsuParent_[x];
        dsuParent_[x] = root;
        if (trace_) {
            compressed.push_back({x, root});
        }
        x = next;
    }

    if (trace_) {
        trace_->push(Trace::Event("find")
                         .field("x", path.front())
                         .field("path", path)
                         .field("root", root)
                         .field("compressed", compressed));
    }
    return root;
}

int DSUTree::componentNode(int x) {
    checkLeaf(x);
    return compNode_[find(x)];
}

bool DSUTree::unite(int a, int b) {
    checkLeaf(a);
    checkLeaf(b);
    int rootA = find(a);
    int rootB = find(b);

    if (rootA == rootB) {
        if (trace_) {
            trace_->push(Trace::Event("unite")
                             .field("a", a)
                             .field("b", b)
                             .field("rootA", rootA)
                             .field("rootB", rootB)
                             .field("merged", false)
                             .field("reason", "ya conectados")
                             .field("node", compNode_[rootA]));
        }
        return false;
    }

    int nodeA = compNode_[rootA];
    int nodeB = compNode_[rootB];
    int t = ++unions_;
    int newNode = n_ + t;

    treeParent_[nodeA] = newNode;
    treeParent_[nodeB] = newNode;
    treeTime_[newNode] = t;
    treeChildren_[newNode] = {nodeA, nodeB};

    int big = rootA;
    int small = rootB;
    if (dsuSize_[big] < dsuSize_[small]) {
        std::swap(big, small);
    }
    dsuParent_[small] = big;
    dsuSize_[big] += dsuSize_[small];
    compNode_[big] = newNode;

    if (trace_) {
        trace_->push(Trace::Event("unite")
                         .field("a", a)
                         .field("b", b)
                         .field("t", t)
                         .field("rootA", rootA)
                         .field("rootB", rootB)
                         .field("merged", true)
                         .field("dsuChild", small)
                         .field("dsuParent", big)
                         .field("size", dsuSize_[big])
                         .field("newNode", newNode)
                         .field("children", std::vector<int>{nodeA, nodeB}));
    }
    return true;
}

bool DSUTree::connected(int a, int b) {
    checkLeaf(a);
    checkLeaf(b);
    int rootA = find(a);
    int rootB = find(b);
    bool answer = rootA == rootB;
    if (trace_) {
        trace_->push(Trace::Event("connected")
                         .field("a", a)
                         .field("b", b)
                         .field("rootA", rootA)
                         .field("rootB", rootB)
                         .field("answer", answer));
    }
    return answer;
}

int DSUTree::whenConnected(int a, int b) const {
    checkLeaf(a);
    checkLeaf(b);
    std::vector<int> climbA{a};
    std::vector<int> climbB{b};
    int u = a;
    int v = b;
    int answer = 0;
    int meet = a;

    while (u != v) {
        bool moveU = treeTime_[u] < treeTime_[v] || (treeTime_[u] == treeTime_[v] && u < v);
        int& side = moveU ? u : v;
        int next = treeParent_[side];
        if (next == kNone) {
            answer = kNone;
            meet = kNone;
            break;
        }
        side = next;
        (moveU ? climbA : climbB).push_back(next);
    }
    if (answer != kNone) {
        meet = u;
        answer = treeTime_[u];
    }

    if (trace_) {
        trace_->push(Trace::Event("query")
                         .field("a", a)
                         .field("b", b)
                         .field("answer", answer)
                         .field("meetNode", meet)
                         .field("climbA", climbA)
                         .field("climbB", climbB));
    }
    return answer;
}
