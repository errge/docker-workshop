#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
#include <signal.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define PORT 3000
#define BUFFER_SIZE 1024

volatile sig_atomic_t keep_running = 1;

void sigint_handler(int sig) {
  keep_running = 0;
}

void handle_connection(int client_sock);
void clean_input(char *str);

int main() {
  int listen_fd, client_fd;
  struct sockaddr_in serv_addr;

  // Use sigaction to gain control over syscall restarting
  struct sigaction sa;
  memset(&sa, 0, sizeof(sa));
  sa.sa_handler = sigint_handler;
  sigemptyset(&sa.sa_mask);
  sa.sa_flags = 0; // Explicitly do NOT set SA_RESTART
  if (sigaction(SIGINT, &sa, NULL) == -1) {
    perror("sigaction");
    exit(EXIT_FAILURE);
  }

  signal(SIGCHLD, SIG_IGN);

  listen_fd = socket(AF_INET, SOCK_STREAM, 0);
  if (listen_fd < 0) {
    perror("socket");
    exit(EXIT_FAILURE);
  }

  int optval = 1;
  setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(optval));

  memset(&serv_addr, 0, sizeof(serv_addr));
  serv_addr.sin_family = AF_INET;
  serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
  serv_addr.sin_port = htons(PORT);

  if (bind(listen_fd, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
    perror("bind");
    exit(EXIT_FAILURE);
  }

  if (listen(listen_fd, 10) < 0) {
    perror("listen");
    exit(EXIT_FAILURE);
  }

  fprintf(stderr, "Server is ready and listening on port %d\n", PORT);

  while (keep_running) {
    client_fd = accept(listen_fd, NULL, NULL);
    if (client_fd < 0) {
      if (errno == EINTR) {
        continue;
      }
      perror("accept");
      continue;
    }

    if (fork() == 0) {
      close(listen_fd);
      handle_connection(client_fd);
      close(client_fd);
      exit(0);
    } else {
      close(client_fd);
    }
  }

  fprintf(stderr, "\nShutting down server gracefully.\n");
  close(listen_fd);

  return 0;
}

void handle_connection(int sock) {
  char buffer[BUFFER_SIZE];
  ssize_t n;

  while ((n = read(sock, buffer, BUFFER_SIZE - 1)) > 0) {
    buffer[n] = '\0';

    if (strncmp(buffer, "GET ", 4) == 0 || strncmp(buffer, "POST ", 5) == 0 ||
        strncmp(buffer, "HEAD ", 5) == 0 || strncmp(buffer, "PUT ", 4) == 0) {
      const char *http_response =
                "HTTP/1.1 400 Bad Request\r\n"
                "Content-Type: text/plain\r\n"
                "Connection: close\r\n"
                "\r\n"
                "This is a TCP service, please use telnet or nc\n";
      write(sock, http_response, strlen(http_response));
      break;
    }

    clean_input(buffer);

    if (strcmp(buffer, "friend") == 0) {
      const char *success_msg = "Congrats! You are a friend. Closing connection.\n";
      write(sock, success_msg, strlen(success_msg));
      break;
    } else {
      const char *help_msg = "Unknown command. The only accepted message is 'friend'.\n";
      write(sock, help_msg, strlen(help_msg));
    }
  }
}

void clean_input(char *str) {
  char *start = str;
  while (*start && isspace((unsigned char)*start)) {
    start++;
  }

  char *end = start + strlen(start) - 1;
  while (end > start && isspace((unsigned char)*end)) {
    end--;
  }
  *(end + 1) = '\0';

  memmove(str, start, strlen(start) + 1);

  for (int i = 0; str[i]; i++) {
    str[i] = tolower((unsigned char)str[i]);
  }
}
