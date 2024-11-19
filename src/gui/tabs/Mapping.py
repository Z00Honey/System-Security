import json
import os
import uuid


class MappingManager:
    def __init__(self):
        # 매핑 데이터를 저장할 파일 설정
        self.mapping_file = os.path.join(os.path.dirname(__file__), "meta.json")
        self.mapping = self.load_mapping()

    def load_mapping(self):
        # 메타데이터 로드
        if os.path.exists(self.mapping_file):
            with open(self.mapping_file, "r") as f:
                return json.load(f)
        return {}

    def save_mapping(self):
        # 메타데이터 저장
        with open(self.mapping_file, "w") as f:
            json.dump(self.mapping, f, indent=4)

    def generate_id(self, path):
        # 고유 ID 생성 및 매핑 저장
        file_id = str(uuid.uuid4())
        self.mapping[file_id] = {"original_path": path}
        self.save_mapping()
        return file_id

    def get_original_path(self, file_id):
        # ID를 통해 원래 경로 검색
        return self.mapping.get(file_id, {}).get("original_path")

    def get_file_id(self, filename):
        # 파일 이름을 통해 ID 검색
        for file_id, info in self.mapping.items():
            if os.path.basename(info["original_path"]) == filename:
                return file_id
        return None

    def delete_mapping(self, file_id):
        # ID 매핑 삭제
        if file_id in self.mapping:
            del self.mapping[file_id]
            self.save_mapping()
