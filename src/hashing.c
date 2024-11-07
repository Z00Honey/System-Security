#include <openssl/sha.h>
#include <string.h>
#include <stdlib.h>

// SHA-256 해시 함수
__declspec(dllexport) void hash_password(const char* password, const unsigned char* salt, unsigned char* output) {
    SHA256_CTX sha256;
    SHA256_Init(&sha256);

    // 솔트를 먼저 해싱
    SHA256_Update(&sha256, salt, 16);  // 16바이트 솔트
    // 비밀번호를 추가하여 해싱
    SHA256_Update(&sha256, password, strlen(password));
    
    SHA256_Final(output, &sha256);
}
