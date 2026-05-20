---
생성일: 2026-05-19
최근_업데이트: 2026-05-19
카테고리: 개념사전 / 시스템_패턴
태그: [Physical AI, 로보틱스, WAM, VLA, Embodied AI, NVIDIA, GR00T]
관련_문서: [[Long-Horizon_에이전트]], [[2026-05_Jim_Fan_Robotics_EndGame]]
신뢰도: 검증됨
출처: Jim Fan (NVIDIA) — Sequoia AI Ascent 2026
---

# Physical AI & 로보틱스 엔드게임

## 한 줄 정의
> AI가 디지털 세계를 넘어 물리 세계에서 자율적으로 작업을 수행하는 시스템. LLM이 소프트웨어를 변혁했듯, Physical AI는 하드웨어·제조·노동 시장을 변혁한다.

## 왜 알아야 하나?
NVIDIA의 Jim Fan은 로보틱스가 LLM 진화 경로를 "스피드런"하고 있다고 선언했다. 2028~2029년 Physical Turing Test, 2030년대 Physical API, 2040년 Physical Auto-Research라는 명확한 로드맵이 제시됐다. $38조 글로벌 제조·노동 시장이 AI로 재편되는 타임라인이 구체화되고 있다.

## The Great Parallel — LLM 플레이북의 로보틱스 재현

| 단계 | LLM (텍스트) | 로보틱스 (물리) | 도달 시점 |
|------|------------|--------------|---------|
| **1. 사전학습** | 인터넷 텍스트 예측 | 비디오 기반 세계 상태 예측 | 진행 중 |
| **2. 정렬** | RLHF, 지시 파인튜닝 | 특정 작업 파인튜닝 | 진행 중 |
| **3. 추론** | Chain-of-thought, o1 | 다단계 물리 계획 수립 | 초기 단계 |
| **4. 자율 연구** | AI Scientist | 로봇이 더 나은 로봇 설계 | 2040 목표 |

## VLA → WAM 패러다임 전환

### VLA (Vision-Language-Action) — 구식 패러다임
- "언어 우선" 아키텍처: 언어 모델에 액션 헤드를 얹은 구조
- "명사(Nouns)"는 잘 인식하지만 "동사(Verbs, 물리 법칙)"에 취약
- 테일러 스위프트 사진 옆 콜라캔 인식 ✓, 중력에 따른 물체 움직임 ✗

### WAM (World Action Model) — 새 패러다임
- "비디오 우선" 아키텍처: 다음 토큰 예측 → 다음 물리 상태 예측
- 미래 픽셀과 관절 토크를 동시에 "꿈꾸는(Dream)" 방식
- 대표 모델: NVIDIA DreamZero (140억 파라미터)
- Sora, Veo 같은 비디오 모델에서 이미 물리 법칙 이해가 창발됨

## 데이터 전략의 혁명 — 텔레오퍼레이션의 죽음

### 기존 방식의 한계
```
텔레오퍼레이션 = "인간 연료(Human Fuel)"
- 하루 최대 24시간이라는 물리적 한계
- 로봇 하드웨어 오작동
- 수백만 시간 필요 → 수천 년 소요
```

### 새로운 방식: 센서화된 인간 데이터
| 방법 | 설명 | 성과 |
|------|------|------|
| **UMI** (Universal Manipulation Interface) | 인간 손에 착용하는 단순 액추에이터 | 로봇 없이 데이터 수집 |
| **EgoScale** | 1인칭 시점 인간 영상 20,854시간 | 덱스테러티 로그-선형 스케일링 법칙 발견 |

→ 텔레오퍼레이션 비중: 학습 데이터의 **0.1% 미만**으로 축소

## 컴퓨트 = 환경 = 데이터

물리 세계 데이터 병목을 우회하는 핵심 전략:

```
DreamDojo (신경망 시뮬레이터)
- 고전 물리 방정식 대신 데이터 기반 비디오 생성
- 10FPS 이상 실시간 센서 상태 출력
- 로봇이 "꿈 공간(Dream Space)"에서 강화학습 수행
- 44,000시간 분량, 오픈소스 공개
```

## 로보틱스 기술 트리 — 3단계 잠금 해제

```
현재 → [1] Physical Turing Test → [2] Physical API → [3] Physical Auto-Research
```

### [1] Physical Turing Test (2028~2029년, 2~3년 후)
집에 돌아왔을 때 완벽하게 정리된 아파트와 캔들 저녁 식사 — 인간이 했는지 로봇이 했는지 구분 불가.
경제적으로 관련된 작업 전반에서 로봇이 인간과 구별 불가능한 수준.

### [2] Physical API (2030년대)
소프트웨어가 비트를 다루듯, 로봇이 원자를 다룬다:
- 불이 꺼진 공장(Lights-out Factory) 24/7 자율 운영
- 자동화된 실험실 (AI가 수백만 건의 임상시험 병렬 수행)
- 로봇 스킬 앱 스토어 (미슐랭 셰프 → 저녁식사-as-a-Service)

### [3] Physical Auto-Research (2040년, 확률 95%)
로봇이 스스로 더 나은 로봇을 설계·제작하는 단계.
"AlexNet(2012) → AI Scientist(2026)" = 14년, 같은 기간 이후 2040년.

## 핵심 명언

> *"Our generation was born too late to explore the earth and too early to explore the stars, but we are born just in time to solve robotics."*
> — Jim Fan, Sequoia AI Ascent 2026

## 참고 자료
- [YouTube: Jim Fan — Robotics' End Game](https://www.youtube.com/watch?v=3Y8aq_ofEVs)
- [Humanoids Daily: The Great Parallel](https://www.humanoidsdaily.com/news/the-great-parallel-nvidia-s-jim-fan-outlines-the-robotics-end-game-strategy)
- [Sequoia Inference: The Physical Turing Test](https://inferencebysequoia.substack.com/p/the-physical-turing-test-jim-fan)

---
## 나의 코멘트
> ✍️

(Physical AI가 우리 사업·투자 전략에 주는 시사점을 여기에)
