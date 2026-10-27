/* Source-assisted experiment probe. Setup/serialization only; unchanged native actions. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "minesweeper.h"

static void snapshot(msw *game)
{
    printf("{\"rows\":4,\"columns\":4,\"mines\":%d,\"grid\":\"", game->mines);
    fwrite(game->grid, 1, 16, stdout);
    printf("\",\"visible\":\"");
    fwrite(game->visible, 1, 16, stdout);
    printf("\",\"flags\":%d,\"generation\":%d,\"undo_index\":%d,"
           "\"undo_enabled\":%s,\"grid_initialized\":true,\"won\":%d}",
           game->flags, game->gen, game->undoidx,
           game->undo ? "true" : "false", msw_won(game));
}

int main(int argc, char **argv)
{
    msw game;
    int mines = 0, flags = 0, row, column, result;
    char command;
    if (argc != 3 || strlen(argv[1]) != 16 || strlen(argv[2]) != 16) return 2;
    for (int i = 0; i < 16; i++) {
        char g = argv[1][i], v = argv[2][i];
        if (g != '!' && (g < '0' || g > '8')) return 2;
        if (v != '#' && v != 'F' && v != '!' && (v < '0' || v > '8')) return 2;
        mines += g == '!';
        flags += v == 'F';
    }
    msw_init(&game, 4, 4, mines);
    game.grid = malloc(16);
    if (!game.grid) { msw_destroy(&game); return 2; }
    memcpy(game.grid, argv[1], 16);
    memcpy(game.visible, argv[2], 16);
    game.flags = flags;
    printf("{\"setup\":"); snapshot(&game); puts("}");
    while (scanf(" %c %d %d", &command, &row, &column) == 3) {
        /* Native dig checks bounds. Flag/unflag do not: probe guards those. */
        if ((command != 'd' && command != 'f' && command != 'u') ||
            (command != 'd' && (row < 0 || row >= 4 || column < 0 || column >= 4))) {
            msw_destroy(&game); return 2;
        }
        printf("{\"action\":\"%c\",\"row\":%d,\"column\":%d,\"before\":", command, row, column);
        snapshot(&game);
        result = command == 'd' ? msw_dig(&game, row, column) :
                 command == 'f' ? msw_flag(&game, row, column) : msw_unflag(&game, row, column);
        printf(",\"result\":%d,\"message\":\"%s\",\"after\":", result, MSW_MSG[result]);
        snapshot(&game);
        printf(",\"cli_would_stop\":%s}\n", result == MSW_MBOOM || msw_won(&game) ? "true" : "false");
        /* Deliberately continue after terminal observations to inspect core behavior. */
    }
    msw_destroy(&game);
    return 0;
}
