#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

int main() {
  char* filename = "test.txt";
  void* buf;

  int fd = open(filename, O_RDONLY);
  ssize_t rcode = pread(fd, buf, 100, 0);

  if (rcode < 0) {
    printf("errno %s\n", strerror(errno));
    return rcode;
  } else {
    return 0;
  }
}
