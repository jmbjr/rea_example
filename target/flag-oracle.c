/* Experiment probe: setup/serialization only; actions call unchanged upstream. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "minesweeper.h"

static void snapshot(const msw *game)
{
    printf("{\"rows\":%d,\"columns\":%d,\"mines\":%d,\"visible\":\"",
           game->rows, game->columns, game->mines);
    fwrite(game->visible, 1, (size_t)(game->rows * game->columns), stdout);
    printf("\",\"flags\":%d,\"generation\":%d,\"undo_index\":%d,"
           "\"undo_enabled\":%s,\"grid_initialized\":%s}",
           game->flags, game->gen, game->undoidx,
           game->undo ? "true" : "false", game->grid ? "true" : "false");
}

int main(int argc, char **argv)
{
    msw game;
    char command;
    int row, col, flags = 0, result;
    if (argc != 2 || strlen(argv[1]) != 6) return 2;
    for (int i = 0; i < 6; i++) {
        char cell = argv[1][i];
        if (cell != '#' && cell != 'F' && (cell < '0' || cell > '8')) return 2;
        if (cell == 'F') flags++;
    }
    /* The 2x3 state is synthetic, not a generated or reachable-board claim. */
    msw_init(&game, 2, 3, 1);
    printf("{\"initialized\":");
    snapshot(&game);
    memcpy(game.visible, argv[1], 6);
    game.flags = flags;
    printf(",\"setup\":");
    snapshot(&game);
    printf("}\n");
    while (scanf(" %c %d %d", &command, &row, &col) == 3) {
        /* Probe admission guards are not claimed as upstream safety checks. */
        if ((command != 'f' && command != 'u') || row < 0 || row >= 2 || col < 0 || col >= 3) {
            msw_destroy(&game);
            return 2;
        }
        printf("{\"action\":\"%c\",\"row\":%d,\"column\":%d,\"before\":", command, row, col);
        snapshot(&game);
        result = command == 'f' ? msw_flag(&game, row, col) : msw_unflag(&game, row, col);
        printf(",\"result\":%d,\"message\":\"%s\",\"after\":", result, MSW_MSG[result]);
        snapshot(&game);
        printf("}\n");
    }
    msw_destroy(&game);
    return 0;
}
