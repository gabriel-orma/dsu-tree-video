#include <fstream>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>

#include "dsu_tree.hpp"
#include "trace.hpp"

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "uso: " << argv[0] << " <escenario.txt> [salida.json]\n";
        return 1;
    }

    std::ifstream in(argv[1]);
    if (!in) {
        std::cerr << "no se pudo abrir " << argv[1] << "\n";
        return 1;
    }

    Trace trace;
    std::unique_ptr<DSUTree> tree;
    std::string line;
    int lineNo = 0;

    try {
        while (std::getline(in, line)) {
            ++lineNo;
            std::istringstream ss(line);
            std::string op;
            if (!(ss >> op) || op[0] == '#') {
                continue;
            }
            if (op == "init") {
                int n;
                ss >> n;
                tree = std::make_unique<DSUTree>(n, &trace);
                continue;
            }
            if (!tree) {
                throw std::runtime_error("falta 'init n' antes de las operaciones");
            }
            int a;
            int b;
            if (!(ss >> a >> b)) {
                throw std::runtime_error("se esperaban dos nodos");
            }
            if (op == "unite") {
                tree->unite(a, b);
            } else if (op == "connected") {
                tree->connected(a, b);
            } else if (op == "query") {
                tree->whenConnected(a, b);
            } else {
                throw std::runtime_error("operacion desconocida: " + op);
            }
        }
    } catch (const std::exception& e) {
        std::cerr << argv[1] << ":" << lineNo << ": " << e.what() << "\n";
        return 1;
    }

    if (argc >= 3) {
        std::ofstream out(argv[2]);
        trace.writeJson(out);
    } else {
        trace.writeJson(std::cout);
    }
    return 0;
}
