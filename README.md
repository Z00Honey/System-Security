# System-Security
### Team-4


#### UI Branch Structer
```bash
src
├── main.py                      # 프로그램의 진입점. GUI 애플리케이션을 초기화 -> 메인 창 실행
├── test.py                      # PySide6 test(QuteWindow) (메인 빌드 X)
├── testwindow.py                # Windows 시스템 이벤트와 상호작용을 테스트하는 파일 (메인 빌드 X)
├── window.py                    # 주요 GUI 창 구성
│	assets
│	├── css
│	│   ├── main.css             # QMainWindow의 기본 배경 및 스타일
│	│   └── title_bar.css        # 타이틀 바의 버튼 스타일과 레이아웃을 설정
│	└── images					 # 이미지 리소스
│
├── utils                        # 유틸리티
│   ├── load.py                  # 이미지, CSS 파일 경로 관리 및 스타일 시트를 로드
│   └── native                   # 네이티브 윈도우 시스템과 상호작용하는 모듈
│       ├── c_structure.py       # GUI 효과에 사용(ctypes로 작성된 C 구조체)
│       ├── native_event.py      # 윈도우 시스템의 이벤트 (창 크기 및 상태 관리)
│       └── util.py              # 창 그림자 효과 추가 및 크기 조정 기능 등 구현
└── widgets
    └── title_bar.py             # 사용자 정의 타이틀 바 구성 파일 (창의 minimize, maximize, close 버튼 포함)
```