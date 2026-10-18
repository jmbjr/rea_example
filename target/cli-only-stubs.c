#include <stdio.h>

int gui_main(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    fputs("GUI mode is unavailable in this CLI-only experiment build.\n", stderr);
    return 1;
}

int curses_main(int argc, char **argv)
{
    (void)argc;
    (void)argv;
    fputs("Curses mode is unavailable in this CLI-only experiment build.\n", stderr);
    return 1;
}
