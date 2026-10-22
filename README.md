# 계단을 피하면 환승길은 얼마나 달라질까

왕십리역의 추가 보행과 설비 중단 영향을 공개자료로 분석한 코드입니다. 2026년 「AI와 함께하는 교통문제 해결을 위한 데이터 분석 공모전」 분석보고서의 재현 자료입니다.

## 먼저 볼 결과

- 같은 국소 출발·도착점에서 계단 회피 경로는 평면 자력 이동이 **8.6 m** 길었습니다. 비교 경로의 계단 높이는 모형상 **4.4 m**입니다.
- EL3 중단을 승강장 출발 전에 알 때와 설비 앞에서 알 때를 비교하면, 계단을 이용할 수 있는 사람의 국소 모형 경로에서 **30.4 m** 차이가 났습니다. 반대 방향은 **0.4 m**입니다.
- 24개 설비와 305개 중단 집합을 40개 연결 가정에서 계산했습니다. 미확인 통로의 연결 여부에 따라 정비 조합의 영향이 바뀝니다.

**이 수치는 현장 실측이나 현재 왕십리 전체 환승거리 결과가 아닙니다.** 3D 모형의 B4–B5 국소 경로와 조건부 연결망 계산입니다. 현장사진과 도면에서 확인한 단차 때문에 긴 두 팔의 무계단 연결은 보류했습니다. 이 저장소를 실제 이동 안내로 사용하지 마세요.

## 내려받기

**[전체 코드·입력 ZIP 내려받기](wangsimni_analysis_code.zip)** → 압축을 푼 폴더에서 아래 명령을 실행합니다. 폴더 안에 `reproduce.py`, `data/`, `research/`가 함께 있어야 합니다. 전체 소스와 데이터 파일 목록·해시는 `MANIFEST.json`에서 볼 수 있습니다.

## 바로 실행

Python 3.10 이상, 외부 패키지·API 키·로그인 없이 실행합니다.

```bash
python reproduce.py
```

`results/report_values.json`에 보고서 수치와 경로를 저장합니다. 거리 입력은 `data/local_metric_edges.csv`의 **연구자가 계산한 구간 거리**입니다. 원본 3D 모델에서 다시 도형을 추출하는 과정과 구분됩니다.

실행 검증: 국소 Dijkstra–Floyd 비교 5,000건, 연결망 BFS–Warshall 비교 195,200건, 별도 수기 간선 DFS 비교 2,560건에서 불일치 0건. 검산은 해당 입력에 대한 계산의 일치를 뜻합니다.

## 입력과 계산

| 파일 | 역할 |
|---|---|
| `data/local_metric_edges.csv` | 25개 연구자 지정 지점 사이의 계산 간선 206개. 계단 평면길이 포함, EL 탑승거리는 별도 |
| `data/annotated_nodes.json` | 원점·도착점과 시설 접근점. 현재 열차 문 위치 실측이 아님 |
| `data/provenance.json` | S-MAP 출처, 원본 해시, 해상도, 계산 정의 |
| `research/geometry/core_topology_edges.csv` | 방향을 가진 기본 연결망 |
| `research/upper_check/*candidate_edges.csv` | 코레일 연결과 EL5를 추가하는 조건부 간선 |
| `research/data/` | 서울교통공사 2026-09-01 EL·ES 설치현황 원문 CSV |
| `research/design_round2/` | 40개 연결 가정, 설비 중단 및 독립 검산 코드 |
| `research/range_model/` | 전체거리 식별 가능성·정보 시점·계단 부담 분석의 원래 코드 |

40개 가정 = 기본 연결 5종 × 상왕십리 측 긴 ES 접근 여부 2종 × 한양대 측 접근 여부 2종 × EL1 B2 접근 여부 2종. 기본 연결 5종은 코레일 연결 제외 1종과, 코레일 연결 포함 시 EL5 포함 여부·일부 ES 방향의 4개 조합입니다. 이 가정에는 발생확률을 부여하지 않았습니다.

305개 중단 집합 = 정상 1 + 단일 설비 24 + 두 설비 조합 276 + 공통 통로·설비군 중단 4. 8개 OD는 2호선 2방향 × 5호선 2방향 × 환승 양방향이며 승객 수나 비율이 아닙니다. 가상의 중단은 실측 고장 이력이 아닙니다.

## 원본 모델부터 다시 계산할 때

원본 GLB·설계도·상업 사진·학술논문 PDF는 재배포하지 않습니다. `SOURCES.md`의 출처와 이용조건을 확인해 확보한 GLB를 `research/sources/wangsimni_smap.glb`에 놓습니다. 파일 해시는 `data/provenance.json`과 대조합니다. 모형 취득 시점과 제작·갱신 시점은 다릅니다.

별도 환경에 `numpy scipy Pillow DracoPy`를 설치한 뒤 다음 순서로 실행합니다.

```bash
python research/geometry/inspect_model.py
python research/geometry/analyze_verified_section.py
python research/geometry/verify_fine_grid.py
python research/metric_extension/extend_checked_section.py
python research/range_model/conditional_range_model.py
python research/range_model/validate_ranges.py
```

원래 그림 코드 일부는 Windows 글꼴을 사용합니다. 핵심 결과를 확인하는 `reproduce.py`는 운영체제 글꼴에 의존하지 않습니다. 원본부터의 실행은 별도 입력 취득이 필요하며 기본 재현 명령의 오프라인 실행 범위에 포함하지 않습니다.

## 해석 범위

- 거리: 평면 자력 이동. ES 탑승, EL 수직 이동·대기, 혼잡, 문 안쪽 이동은 합산하지 않았습니다.
- EL-only, ES-allowed/no-stairs, stairs-allowed를 구분했습니다. 연령이나 장애명만으로 수단을 지정하지 않았습니다.
- 코레일 경유 전체 무계단 통로, 개찰구 조건, EL1 중간 정차층의 승객 접근은 미확인입니다. 미측정 거리를 0으로 대입하지 않았습니다.
- 모형의 0.125 m 격자는 현장 측량 정확도가 아닙니다. 두 격자 비교도 신뢰구간이 아닙니다.
- 참가신청서, 연락처, 로그인 정보, 제3자 사진·도면·논문 원문은 공개 대상에서 제외했습니다.

분석 기준일: 2026-10-22. 작성: 이동현. AI 활용: OpenAI Codex를 통한 자료 대조, 코드 작성·실행·검산 및 문장 정리. 입력 사실과 시나리오를 구분하고 원문 및 알고리즘 대조로 검증했습니다.
