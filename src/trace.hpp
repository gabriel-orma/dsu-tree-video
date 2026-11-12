#pragma once

#include <ostream>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

class Trace {
public:
    class Event {
    public:
        explicit Event(const std::string& op) { out_ << "{\"op\": \"" << op << "\""; }

        Event& field(const std::string& key, int value) {
            out_ << ", \"" << key << "\": " << value;
            return *this;
        }

        Event& field(const std::string& key, bool value) {
            out_ << ", \"" << key << "\": " << (value ? "true" : "false");
            return *this;
        }

        Event& field(const std::string& key, const char* value) {
            out_ << ", \"" << key << "\": \"" << value << "\"";
            return *this;
        }

        Event& field(const std::string& key, const std::vector<int>& values) {
            out_ << ", \"" << key << "\": [";
            for (std::size_t i = 0; i < values.size(); ++i) {
                out_ << (i ? ", " : "") << values[i];
            }
            out_ << "]";
            return *this;
        }

        Event& field(const std::string& key, const std::vector<std::pair<int, int>>& pairs) {
            out_ << ", \"" << key << "\": [";
            for (std::size_t i = 0; i < pairs.size(); ++i) {
                out_ << (i ? ", " : "") << "[" << pairs[i].first << ", " << pairs[i].second << "]";
            }
            out_ << "]";
            return *this;
        }

        Event& field(const std::string& key, const std::vector<std::vector<int>>& rows) {
            out_ << ", \"" << key << "\": [";
            for (std::size_t i = 0; i < rows.size(); ++i) {
                out_ << (i ? ", " : "") << "[";
                for (std::size_t j = 0; j < rows[i].size(); ++j) {
                    out_ << (j ? ", " : "") << rows[i][j];
                }
                out_ << "]";
            }
            out_ << "]";
            return *this;
        }

        std::string str() const { return out_.str() + "}"; }

    private:
        std::ostringstream out_;
    };

    void push(const Event& event) { events_.push_back(event.str()); }

    std::size_t size() const { return events_.size(); }

    void writeJson(std::ostream& os) const {
        os << "[\n";
        for (std::size_t i = 0; i < events_.size(); ++i) {
            os << "  " << events_[i] << (i + 1 < events_.size() ? ",\n" : "\n");
        }
        os << "]\n";
    }

private:
    std::vector<std::string> events_;
};
