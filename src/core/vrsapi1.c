// vrsapi.c
// Build Command:
//cl /LD vrsapi1.c /I"C:\Program Files\OpenSSL-Win64\include" /MT /link /LIBPATH:"C:\Program Files\OpenSSL-Win64\lib\VC\x64\MT" libcrypto_static.lib libssl_static.lib ws2_32.lib wininet.lib advapi32.lib user32.lib crypt32.lib /out:vrsapi1.dll

#ifdef _WIN32
    #include <windows.h>
    #include <wininet.h>
    #define DLL_EXPORT __declspec(dllexport)
#else
    #define DLL_EXPORT
    #define BOOL int
    #define WINAPI
    #define HINSTANCE void*
    #define DWORD unsigned long
    #define LPVOID void*
    #define TRUE 1
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>

#define ENV_VAR_KEY "VIRUSTOTAL_API_KEY"
#define RESULT_BUFFER_SIZE 4096
#define API_HOST "www.virustotal.com"
#define API_PATH "/api/v3/files/%s"

// Windows DLL 초기화
#ifdef _WIN32
BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    return TRUE;
}
#endif

// SHA-256 해시값 계산 함수
static BOOL calculate_file_hash(const char* file_path, char* hash_result, size_t result_size) {
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    EVP_MD_CTX* ctx = EVP_MD_CTX_new();
    
    if (!ctx) return FALSE;
    
    FILE* file = NULL;
#ifdef _WIN32
    wchar_t wfile_path[MAX_PATH];
    int conversion_result = MultiByteToWideChar(CP_UTF8, 0, file_path, -1, wfile_path, MAX_PATH);
    if (conversion_result == 0) {
        printf("[DEBUG] Failed to convert file path to wide char: %s\n", file_path);
        EVP_MD_CTX_free(ctx);
        return FALSE;
    }
    file = _wfopen(wfile_path, L"rb");
#else
    file = fopen(file_path, "rb");
#endif

    if (!file) {
        printf("[DEBUG] Failed to open file: %s\n", file_path);
        EVP_MD_CTX_free(ctx);
        return FALSE;
    }

    EVP_DigestInit_ex(ctx, EVP_sha256(), NULL);
    
    unsigned char buffer[32768];
    size_t bytes;
    
    while ((bytes = fread(buffer, 1, sizeof(buffer), file)) > 0) {
        EVP_DigestUpdate(ctx, buffer, bytes);
    }
    
    EVP_DigestFinal_ex(ctx, hash, &hash_len);
    
    for (unsigned int i = 0; i < hash_len; i++) {
        snprintf(hash_result + (i * 2), result_size - (i * 2), "%02x", hash[i]);
    }
    
    fclose(file);
    EVP_MD_CTX_free(ctx);
    printf("[DEBUG] Calculated file hash: %s\n", hash_result);
    return TRUE;
}

// HTTP 요청 함수
static BOOL make_api_request(const char* file_hash, char* result, size_t result_size) {
    HINTERNET hInternet = NULL;
    HINTERNET hConnect = NULL;
    HINTERNET hRequest = NULL;
    BOOL success = FALSE;
    char api_key[100] = {0};
    char path[256] = {0};
    
    // API 키 가져오기
    DWORD api_key_len = GetEnvironmentVariable(ENV_VAR_KEY, api_key, sizeof(api_key));
    if (api_key_len == 0) {
        DWORD error_code = GetLastError();
        snprintf(result, result_size, "API 키를 찾을 수 없습니다. Error Code: %lu", error_code);
        printf("[DEBUG] Failed to get API key. Error Code: %lu\n", error_code);
        return FALSE;
    }

    printf("[DEBUG] API Key: %s\n", api_key);

    // API 경로 생성
    snprintf(path, sizeof(path), API_PATH, file_hash);
    printf("[DEBUG] API Path: %s\n", path);

    hInternet = InternetOpen("vrsapi/1.0", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, 0);
    if (!hInternet) {
        snprintf(result, result_size, "인터넷 연결 초기화 실패");
        printf("[DEBUG] Internet connection initialization failed.\n");
        return FALSE;
    }

    hConnect = InternetConnect(hInternet, API_HOST, INTERNET_DEFAULT_HTTPS_PORT, NULL, NULL, INTERNET_SERVICE_HTTP, 0, 0);
    if (!hConnect) {
        snprintf(result, result_size, "서버 연결 실패");
        printf("[DEBUG] Server connection failed.\n");
        InternetCloseHandle(hInternet);
        return FALSE;
    }

    hRequest = HttpOpenRequest(hConnect, "GET", path, NULL, NULL, NULL, INTERNET_FLAG_SECURE, 0);
    if (!hRequest) {
        snprintf(result, result_size, "HTTP 요청 생성 실패");
        printf("[DEBUG] HTTP request creation failed.\n");
        InternetCloseHandle(hConnect);
        InternetCloseHandle(hInternet);
        return FALSE;
    }

    // 헤더 추가
    char headers[256];
    snprintf(headers, sizeof(headers), "accept: application/json\r\nx-apikey: %s\r\n", api_key);
    printf("[DEBUG] HTTP Headers: %s\n", headers);

    if (!HttpSendRequest(hRequest, headers, strlen(headers), NULL, 0)) {
        snprintf(result, result_size, "HTTP 요청 전송 실패");
        printf("[DEBUG] HTTP request sending failed.\n");
        InternetCloseHandle(hRequest);
        InternetCloseHandle(hConnect);
        InternetCloseHandle(hInternet);
        return FALSE;
    }

    // 응답 읽기
    char buffer[1024];
    DWORD bytes_read;
    size_t total_read = 0;

    while (InternetReadFile(hRequest, buffer, sizeof(buffer), &bytes_read) 
           && bytes_read > 0 
           && total_read < result_size - 1) {
        memcpy(result + total_read, buffer, bytes_read);
        total_read += bytes_read;
    }
    result[total_read] = '\0';
    printf("[DEBUG] HTTP Response: %s\n", result);
    success = TRUE;

    InternetCloseHandle(hRequest);
    InternetCloseHandle(hConnect);
    InternetCloseHandle(hInternet);
    return success;
}

// 메인 검사 함수
DLL_EXPORT BOOL scan_file_virustotal(const char* file_path, char* result, size_t result_size) {
    char hash[EVP_MAX_MD_SIZE * 2 + 1] = {0};
    
    // 파일 해시 계산
    if (!calculate_file_hash(file_path, hash, sizeof(hash))) {
        snprintf(result, result_size, "파일 해시 계산 실패");
        return FALSE;
    }

    // API 요청
    if (!make_api_request(hash, result, result_size)) {
        return FALSE;
    }

    return TRUE;
}

// 폴더 스캔 함수
DLL_EXPORT BOOL scan_folder_virustotal(const char* folder_path, char* result, size_t result_size) {
    WIN32_FIND_DATA findFileData;
    char search_path[MAX_PATH];
    char full_result[RESULT_BUFFER_SIZE] = {0};
    size_t result_offset = 0;

    snprintf(search_path, MAX_PATH, "%s\\*", folder_path);
    
    HANDLE hFind = FindFirstFile(search_path, &findFileData);
    if (hFind == INVALID_HANDLE_VALUE) {
        snprintf(result, result_size, "폴더를 열 수 없습니다");
        printf("[DEBUG] Folder cannot be opened: %s\n", folder_path);
        return FALSE;
    }

    do {
        if (!(findFileData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)) {
            char file_path[MAX_PATH];
            char scan_result[RESULT_BUFFER_SIZE];
            
            snprintf(file_path, MAX_PATH, "%s\\%s", folder_path, findFileData.cFileName);
            printf("[DEBUG] Scanning file: %s\n", file_path);
            
            if (scan_file_virustotal(file_path, scan_result, sizeof(scan_result))) {
                result_offset += snprintf(full_result + result_offset, 
                                        sizeof(full_result) - result_offset,
                                        "파일: %s\n%s\n\n", 
                                        findFileData.cFileName, 
                                        scan_result);
            }
        }
    } while (FindNextFile(hFind, &findFileData) != 0);

    FindClose(hFind);
    strncpy(result, full_result, result_size);
    return TRUE;
}
