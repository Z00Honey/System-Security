#ifdef _WIN32
    #include <windows.h>
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
    #include <curl/curl.h>

    #define ENV_VAR_KEY "VIRUSTOTAL_API_KEY"
    #define RESULT_BUFFER_SIZE 4096

    // MemoryStruct 구조체 정의
    typedef struct {
        char* memory;
        size_t size;
    } MemoryStruct;

    // Windows DLL 초기화
    #ifdef _WIN32
    BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
        switch (fdwReason) {
            case DLL_PROCESS_ATTACH:
                curl_global_init(CURL_GLOBAL_ALL);
                break;
            case DLL_PROCESS_DETACH:
                curl_global_cleanup();
                break;
        }
        return TRUE;
    }
    #endif

    // 응답을 메모리에 저장하는 콜백 함수
    static size_t WriteMemoryCallback(void* contents, size_t size, size_t nmemb, MemoryStruct* mem) {
        size_t realsize = size * nmemb;
        char* ptr = realloc(mem->memory, mem->size + realsize + 1);
        
    if (!ptr) {
        return 0;
    }
    
    mem->memory = ptr;
    memcpy(&(mem->memory[mem->size]), contents, realsize);
    mem->size += realsize;
    mem->memory[mem->size] = 0;
    
    return realsize;
}

// SHA-256 해시값 계산 함수
DLL_EXPORT BOOL calculate_file_hash(const char* file_path, char* hash_result, size_t result_size) {
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    EVP_MD_CTX* ctx = EVP_MD_CTX_new();
    
    if (!ctx) return FALSE;
    
    FILE* file = NULL;
#ifdef _WIN32
    wchar_t wfile_path[MAX_PATH];
    MultiByteToWideChar(CP_UTF8, 0, file_path, -1, wfile_path, MAX_PATH);
    file = _wfopen(wfile_path, L"rb");
#else
    file = fopen(file_path, "rb");
#endif

    if (!file) {
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
    return TRUE;
}

// VirusTotal API 검사 함수
DLL_EXPORT BOOL scan_file_virustotal(const char* file_path, char* result, size_t result_size) {
    char hash[EVP_MAX_MD_SIZE * 2 + 1] = {0};
    if (!calculate_file_hash(file_path, hash, sizeof(hash))) {
        snprintf(result, result_size, "해시 계산 실패");
        return FALSE;
    }

    char api_key[100];
    DWORD api_key_length = GetEnvironmentVariable(ENV_VAR_KEY, api_key, sizeof(api_key));
    if (api_key_length == 0) {
        snprintf(result, result_size, "API 키를 찾을 수 없습니다");
        return FALSE;
    }

    CURL* curl = curl_easy_init();
    if (!curl) {
        snprintf(result, result_size, "CURL 초기화 실패");
        return FALSE;
    }

    MemoryStruct chunk = {0};
    chunk.memory = malloc(1);
    chunk.size = 0;

    char url[256];
    snprintf(url, sizeof(url), "https://www.virustotal.com/api/v3/files/%s", hash);

    struct curl_slist* headers = NULL;
    headers = curl_slist_append(headers, "accept: application/json");
    
    char auth_header[150];
    snprintf(auth_header, sizeof(auth_header), "x-apikey: %s", api_key);
    headers = curl_slist_append(headers, auth_header);

    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void*)&chunk);

    CURLcode res = curl_easy_perform(curl);
    
    if (res != CURLE_OK) {
        snprintf(result, result_size, "API 요청 실패: %s", curl_easy_strerror(res));
        free(chunk.memory);
        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
        return FALSE;
    }

    // 결과 복사
    snprintf(result, result_size, "%s", chunk.memory);

    free(chunk.memory);
    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);
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
        return FALSE;
    }

    do {
        if (!(findFileData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)) {
            char file_path[MAX_PATH];
            char scan_result[RESULT_BUFFER_SIZE];
            
            snprintf(file_path, MAX_PATH, "%s\\%s", folder_path, findFileData.cFileName);
            
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