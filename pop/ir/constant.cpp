#ifdef HAVE_CONFIG_H
#include <pop/config.h>
#endif

#include <pop/ir/constant.hpp>
#include <pop/common/utils.hpp>

#include <cstring>
#include <sstream>

namespace Pop {

  Constant Constant::new_nil() {
    return Constant(TC::NIL);
  }

  Constant Constant::new_bool(bool value) {
    Constant tmp(TC::BLN);
    tmp.u.as_bool = value;
    return tmp;
  }

  Constant Constant::new_int(long long int value) {
    Constant tmp(TC::INT);
    tmp.u.as_int = value;
    return tmp;
  }

  Constant Constant::new_float(long double value) {
    Constant tmp(TC::FLT);
    tmp.u.as_float = value;
    return tmp;
  }

  Constant Constant::new_string(const std::string &s) {
    Constant tmp(TC::STR);
    tmp.u.as_str = new std::string(s);
    return tmp;
  }

  Constant Constant::new_symbol(const std::string &s) {
    Constant tmp(TC::SYM);
    tmp.u.as_str = new std::string(s);
    return tmp;
  }

  Constant::Constant(const Constant &other) : type(other.type) {
    switch (type) {
      case TC::NIL:
        break;
      case TC::BLN:
        u.as_bool = other.u.as_bool;
        break;
      case TC::INT:
        u.as_int = other.u.as_int;
        break;
      case TC::FLT:
        u.as_float = other.u.as_float;
        break;
      case TC::STR:
      case TC::SYM:
        u.as_str = new std::string(other.u.as_str ? *other.u.as_str : "");
        break;
    }
  }

  Constant::Constant(Constant &&other) : Constant() {
    swap(other);
  }

  Constant &Constant::operator=(const Constant &other) {
    Constant tmp(other);
    swap(tmp);
    return *this;
  }

  Constant &Constant::operator=(Constant &&other) {
    swap(other);
    return *this;
  }

  Constant::~Constant() {
    if (type == TC::STR || type == TC::SYM)
      delete u.as_str;
  }

  void Constant::swap(Constant &other) {
    std::swap(type, other.type);
    Value tmp;
    std::memcpy(&tmp, &u, sizeof(Value));
    std::memcpy(&u, &other.u, sizeof(Value));
    std::memcpy(&other.u, &tmp, sizeof(Value));
  }

  bool Constant::operator==(const Constant &other) const {
    if (type != other.type)
      return false;
    switch (type) {
      case TC::NIL:
        return true;
      case TC::BLN:
        return (u.as_bool == other.u.as_bool);
      case TC::INT:
        return (u.as_int == other.u.as_int);
      case TC::FLT:
        return (u.as_float == other.u.as_float);
      case TC::STR:
      case TC::SYM:
        if (u.as_str && other.u.as_str)
          return (*u.as_str == *other.u.as_str);
        else if (!u.as_str && !other.u.as_str)
          return true;
        return false;
    }
    return false;
  }

  std::string Constant::to_string() const {
    std::stringstream ss;
    switch (type) {
      case TC::NIL:
        ss << "null";
        break;
      case TC::BLN:
        ss << (u.as_bool ? "true" : "false");
        break;
      case TC::INT:
        ss << u.as_int;
        break;
      case TC::FLT:
        ss << u.as_float;
        break;
      case TC::STR:
      case TC::SYM:
        if (u.as_str)
          ss << *u.as_str;
        break;
    }
    return ss.str();
  }

  size_t Constant::hash() const {
    size_t seed =
        std::hash< std::uint8_t >()(static_cast< std::uint8_t >(type));
    switch (type) {
      case TC::NIL:
        break;
      case TC::BLN:
        hash_combine(seed, u.as_bool);
        break;
      case TC::INT:
        hash_combine(seed, u.as_int);
        break;
      case TC::FLT:
        hash_combine(seed, u.as_float);
        break;
      case TC::STR:
      case TC::SYM:
        if (u.as_str)
          hash_combine(seed, *u.as_str);
        break;
    }
    return seed;
  }

  // namespace Pop
}
