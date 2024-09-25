#include "include/file_explorer.h"
#include <stdio.h>
#include <dirent.h>

void list_files(const char* directory) {
    DIR *d;
    struct dirent *dir;
    d = opendir(directory);
    if (d) {
        while ((dir = readdir(d)) != NULL) {
            printf("%s\n", dir->d_name);
        }
        closedir(d);
    } else {
        printf("Unable to open directory: %s\n", directory);
    }
}