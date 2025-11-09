#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

int main() {
  const char *version_str = getenv("VERSION");
  long env_version_num = 0;
  int version_ok = 0;

  if (version_str != NULL) {
    char *endptr;
    env_version_num = strtol(version_str, &endptr, 10);

    if (endptr != version_str && *endptr == '\0' && env_version_num > 42) {
      version_ok = 1;
    }
  }

  if (!version_ok) {
    fprintf(stderr, "docker-workshop: VERSION has to be at least 42.\n");
    return 1;
  }

  const char *config_path = "/data/app.cfg";
  FILE *fp = fopen(config_path, "r");
  if (fp == NULL) {
    fprintf(stderr, "docker-workshop: can't open %s\n", config_path);
    return 1;
  }
  char line_buf[256];
  if (fgets(line_buf, sizeof(line_buf), fp) == NULL) {
    fprintf(stderr, "docker-workshop: incorrect number format in %s\n", config_path);
    fclose(fp);
    return 1;
  }
  fclose(fp);

  char *file_endptr;
  long file_version_num = strtol(line_buf, &file_endptr, 10);

  if (file_endptr == line_buf) {
    fprintf(stderr, "docker-workshop: incorrect number format in %s\n", config_path);
    return 1;
  }

  while (*file_endptr != '\0') {
    if (!isspace((unsigned char)*file_endptr)) {
      fprintf(stderr, "docker-workshop: incorrect number format in %s\n", config_path);
      return 1;
    }
    file_endptr++;
  }

  if (file_version_num != env_version_num) {
    fprintf(stderr, "docker-workshop: mismatch between the config file and environment variable\n");
    return 1;
  }

  printf("docker-workshop: congrats on getting all the details right! Good job!\n");
  return 0;
}
