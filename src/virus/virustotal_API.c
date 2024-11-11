#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>
#include <curl/curl.h>
#include <windows.h>

#define ENV_VAR_KEY "VIRUSTOTAL_API_KEY"

// MemoryStruct 구조체 정의
struct MemoryStruct {
    char* memory;
    size_t size;
};

// 응답을 메모리에 저장하는 콜백 함수
__declspec(dllexport) size_t WriteMemoryCallback(void* contents, size_t size, size_t nmemb, struct MemoryStruct* mem) {
    size_t realsize = size * nmemb;
    mem->memory = (char*)realloc(mem->memory, mem->size + realsize + 1);
    if (mem->memory == NULL) {
        printf("메모리 할당 오류!\n");
        return 0;
    }
    memcpy(&(mem->memory[mem->size]), contents, realsize);
    mem->size += realsize;
    mem->memory[mem->size] = 0;
    return realsize;
}

// last_analysis_stats 필드에서 탐지 수와 검사 엔진 수를 추출하는 함수
__declspec(dllexport) void parse_json_response(const char* json, int* detected_count, int* total_count) {
    const char* stats = strstr(json, "\"last_analysis_stats\":");
    if (!stats) return;

    const char* malicious = strstr(stats, "\"malicious\":");
    const char* harmless = strstr(stats, "\"harmless\":");
    const char* undetected = strstr(stats, "\"undetected\":");

    if (malicious) *detected_count = atoi(malicious + strlen("\"malicious\":"));
    if (harmless && undetected) {
        int harmless_count = atoi(harmless + strlen("\"harmless\":"));
        int undetected_count = atoi(undetected + strlen("\"undetected\":"));
        *total_count = *detected_count + harmless_count + undetected_count;
    }
}

// SHA-256 해시값 계산 함수
__declspec(dllexport) void calculate_sha256(const char* file_path, char* outputBuffer) {
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    EVP_MD_CTX* ctx = EVP_MD_CTX_new();
    const EVP_MD* md = EVP_sha256();

    FILE* file = fopen(file_path, "rb");
    if (!file) {
        EVP_MD_CTX_free(ctx);
        return;
    }

    EVP_DigestInit_ex(ctx, md, NULL);
    const int bufSize = 32768;
    unsigned char* buffer = (unsigned char*)malloc(bufSize);
    int bytesRead = 0;

    if (!buffer) {
        EVP_MD_CTX_free(ctx);
        fclose(file);
        return;
    }

    while ((bytesRead = fread(buffer, 1, bufSize, file))) {
        EVP_DigestUpdate(ctx, buffer, bytesRead);
    }

    EVP_DigestFinal_ex(ctx, hash, &hash_len);

    for (unsigned int i = 0; i < hash_len; i++) {
        sprintf(outputBuffer + (i * 2), "%02x", hash[i]);
    }

    fclose(file);
    free(buffer);
    EVP_MD_CTX_free(ctx);
}

// VirusTotal API에 해시값으로 검사 요청
__declspec(dllexport) void scan_file_with_virustotal(const char* file_hash) {
    CURL* curl;
    CURLcode res;
    struct curl_slist* headers = NULL;
    struct MemoryStruct chunk = { NULL, 0 };

    // 환경 변수에서 API 키 가져오기
    char api_key[100];
    DWORD api_key_length = GetEnvironmentVariable(ENV_VAR_KEY, api_key, sizeof(api_key));
    if (api_key_length == 0) {
        printf("API 키를 환경 변수에서 가져올 수 없습니다.\n");
        return;
    }

    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();

    if (curl) {
        char url[256];
        snprintf(url, sizeof(url), "https://www.virustotal.com/api/v3/files/%s", file_hash);

        headers = curl_slist_append(headers, "accept: application/json");

        char auth_header[150];
        snprintf(auth_header, sizeof(auth_header), "x-apikey: %s", api_key);
        headers = curl_slist_append(headers, auth_header);

        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void*)&chunk);

        res = curl_easy_perform(curl);

        if (res != CURLE_OK) {
            printf("curl_easy_perform() 실패: %s\n", curl_easy_strerror(res));
        }
        else {
            int detected_count = 0, total_count = 0;
            parse_json_response(chunk.memory, &detected_count, &total_count);
            printf("탐지 결과: %d/%d, %s\n", detected_count, total_count, detected_count > 0 ? "이상 있음" : "이상 없음");
        }

        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
    }

    free(chunk.memory);
    curl_global_cleanup();
}

// 폴더 내의 모든 파일 검사 함수
__declspec(dllexport) void scan_folder(const char* folder_path) {
    WIN32_FIND_DATA findFileData;
    HANDLE hFind = INVALID_HANDLE_VALUE;

    char search_path[MAX_PATH];
    snprintf(search_path, MAX_PATH, "%s\\*", folder_path);

    hFind = FindFirstFile(search_path, &findFileData);

    if (hFind == INVALID_HANDLE_VALUE) {
        printf("유효한 폴더 경로가 아닙니다: %s\n", folder_path);
        return;
    }

    do {
        if (!(findFileData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)) {
            char file_path[MAX_PATH];
            snprintf(file_path, MAX_PATH, "%s\\%s", folder_path, findFileData.cFileName);

            char file_hash[EVP_MAX_MD_SIZE * 2 + 1];
            calculate_sha256(file_path, file_hash);

            printf("파일: %s\n", findFileData.cFileName);
            scan_file_with_virustotal(file_hash);
        }
    } while (FindNextFile(hFind, &findFileData) != 0);

    FindClose(hFind);
}

int main() {
    char folder_path[MAX_PATH];

    printf("검사할 폴더 경로를 입력하세요: ");
    scanf("%s", folder_path);

    scan_folder(folder_path);

    return 0;
}