#include "aether_core/error.h"

const char *aether_code_name(int code) {
    switch (code) {
    case AE_OK: return "OK";
    case AE_INVALID: return "INVALID";
    case AE_NOT_FOUND: return "NOT_FOUND";
    case E_DENIED: return "DENIED";
    case AE_TIMEOUT: return "TIMEOUT";
    case AE_IO: return "IO";
    case AE_BUSY: return "BUSY";
    case AE_UNSUPPORTED: return "UNSUPPORTED";
    case AE_CANCELLED: return "CANCELLED";
    default: return "UNKNOWN";
    }
}
