// std.compat exports the compatibility surface for traditional C library
// interfaces, including global names such as printf and strlen.
import std.compat;

int main() {
    const char* greeting = "Hello from std.compat";
    printf("%s (length: %zu)\n", greeting, strlen(greeting));
    return 0;
}
