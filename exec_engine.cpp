#include <iostream>
#include <string>
#include <cstdlib>
#include <csignal>
#include <cerrno>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/wait.h>

static volatile bool g_timed_out = false;

static void sigalrm_handler(int) { g_timed_out = true; }

static std::string json_escape(const std::string& s) {
    std::string out;
    out.reserve(s.size() * 2);
    for (unsigned char c : s) {
        switch (c) {
            case '"':  out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\n': out += "\\n";  break;
            case '\r': out += "\\r";  break;
            case '\t': out += "\\t";  break;
            default:
                if (c >= 0x20) out += c;
        }
    }
    return out;
}

static void drain_fd(int fd, std::string& buf, size_t cap) {
    char tmp[4096];
    while (buf.size() < cap) {
        ssize_t n = read(fd, tmp, std::min(sizeof(tmp), cap - buf.size()));
        if (n > 0) {
            buf.append(tmp, n);
        } else if (n == 0) {
            break;
        } else {
            if (errno == EAGAIN || errno == EWOULDBLOCK) break;
            if (errno == EINTR) continue;
            break;
        }
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout << "{\"exit_code\":-1,\"stdout\":\"\",\"stderr\":\"Usage: exec_engine <cmd> [timeout]\",\"timed_out\":false}\n";
        return 1;
    }

    const char* cmd     = argv[1];
    int timeout_secs    = (argc >= 3) ? std::atoi(argv[2]) : 30;
    if (timeout_secs <= 0) timeout_secs = 30;

    const size_t CAP = 8192;

    int fd_out[2], fd_err[2];
    if (pipe(fd_out) < 0 || pipe(fd_err) < 0) {
        std::cout << "{\"exit_code\":-1,\"stdout\":\"\",\"stderr\":\"pipe failed\",\"timed_out\":false}\n";
        return 1;
    }

    pid_t pid = fork();
    if (pid < 0) {
        std::cout << "{\"exit_code\":-1,\"stdout\":\"\",\"stderr\":\"fork failed\",\"timed_out\":false}\n";
        return 1;
    }

    if (pid == 0) {
        close(fd_out[0]); close(fd_err[0]);
        dup2(fd_out[1], STDOUT_FILENO);
        dup2(fd_err[1], STDERR_FILENO);
        close(fd_out[1]); close(fd_err[1]);
        execl("/bin/sh", "sh", "-c", cmd, nullptr);
        _exit(127);
    }

    close(fd_out[1]); close(fd_err[1]);

    // Non-blocking reads to drain pipes during wait (prevents pipe-full deadlock)
    fcntl(fd_out[0], F_SETFL, O_NONBLOCK);
    fcntl(fd_err[0], F_SETFL, O_NONBLOCK);

    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = sigalrm_handler;
    sigaction(SIGALRM, &sa, nullptr);
    alarm((unsigned int)timeout_secs);

    std::string out_buf, err_buf;
    int exit_code = -1;
    int status    = 0;

    while (true) {
        drain_fd(fd_out[0], out_buf, CAP);
        drain_fd(fd_err[0], err_buf, CAP);

        if (g_timed_out) {
            kill(pid, SIGKILL);
            waitpid(pid, &status, 0);
            break;
        }

        int ret = waitpid(pid, &status, WNOHANG);
        if (ret > 0) {
            exit_code = WIFEXITED(status) ? WEXITSTATUS(status) : -1;
            break;
        }
        if (ret < 0 && errno != EINTR) break;

        usleep(50000);
    }

    alarm(0);

    // Remove O_NONBLOCK for final blocking drain to get any remaining buffered output
    int fl_out = fcntl(fd_out[0], F_GETFL);
    int fl_err = fcntl(fd_err[0], F_GETFL);
    fcntl(fd_out[0], F_SETFL, fl_out & ~O_NONBLOCK);
    fcntl(fd_err[0], F_SETFL, fl_err & ~O_NONBLOCK);
    drain_fd(fd_out[0], out_buf, CAP);
    drain_fd(fd_err[0], err_buf, CAP);

    close(fd_out[0]);
    close(fd_err[0]);

    std::cout << "{"
              << "\"exit_code\":"  << exit_code
              << ",\"stdout\":\""  << json_escape(out_buf) << "\""
              << ",\"stderr\":\""  << json_escape(err_buf) << "\""
              << ",\"timed_out\":" << (g_timed_out ? "true" : "false")
              << "}" << std::endl;

    return 0;
}
