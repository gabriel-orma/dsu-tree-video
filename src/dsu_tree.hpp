#pragma once

#include <utility>
#include <vector>

#include "trace.hpp"

class DSUTree {
public:
    static constexpr int kNone = -1;

    explicit DSUTree(int n, Trace* trace = nullptr);

    bool unite(int a, int b);
    bool connected(int a, int b);
    int whenConnected(int a, int b) const;

    int leafCount() const { return n_; }
    int nodeCount() const { return n_ + unions_; }
    int unionCount() const { return unions_; }
    int componentCount() const { return n_ - unions_; }

    int parent(int node) const { return treeParent_[node]; }
    int time(int node) const { return treeTime_[node]; }
    std::pair<int, int> children(int node) const { return treeChildren_[node]; }
    bool isLeaf(int node) const { return node <= n_; }
    int componentNode(int x);

private:
    int find(int x);
    int rootOf(int x) const;
    void addState(Trace::Event& event) const;
    void checkLeaf(int x) const;

    int n_;
    int unions_ = 0;
    Trace* trace_;

    std::vector<int> dsuParent_;
    std::vector<int> dsuSize_;
    std::vector<int> compNode_;

    std::vector<int> treeParent_;
    std::vector<int> treeTime_;
    std::vector<std::pair<int, int>> treeChildren_;
};
