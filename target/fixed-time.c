#include <time.h>

/* Experiment-only clock interposition, not a gameplay or PRNG replacement. */
time_t time(time_t *out)
{
    const time_t fixed = (time_t)1700000000;
    if (out) *out = fixed;
    return fixed;
}
