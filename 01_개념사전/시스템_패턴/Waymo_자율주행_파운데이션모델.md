---
생성일: 2026-05-19
최근_업데이트: 2026-05-19
카테고리: 개념사전 / 시스템_패턴
태그: [Waymo, 자율주행, 파운데이션모델, Physical AI, LiDAR, 로보택시, Dmitri Dolgov, RLFT, EMMA]
관련_문서: [[Physical_AI_로보틱스]], [[Long-Horizon_에이전트]], [[2026-05_Dolgov_Waymo_Full_Autonomy]]
신뢰도: 검증됨
출처: Dmitri Dolgov (Waymo Co-CEO) — Sequoia AI Ascent 2026 + Cheeky Pint Podcast
---

# Waymo 자율주행 파운데이션 모델 — 20년의 여정

## 한 줄 정의
> LLM이 텍스트를 이해하듯, Waymo는 물리 세계를 이해하는 파운데이션 모델을 구축했다. Driver·Simulator·Critic 3개 교사(Teacher) 모델이 한 개의 파운데이션에서 파생되어, 자율주행의 LLM 플레이북을 완성했다.

## 왜 알아야 하나?
Waymo는 2026년 현재 주 50만 건, 누적 2천만 건 로보택시를 운영하며 인간 운전 대비 13배 안전한 기록을 세웠다. Dmitri Dolgov가 Sequoia AI Ascent 2026에서 공개한 아키텍처는 물리 세계의 AI 시스템이 어떻게 LLM 패러다임(파운데이션 모델 → 파인튜닝 → 증류)을 차용하는지 보여주는 가장 구체적인 사례다.

## Waymo 파운데이션 모델 아키텍처

### 3-Teacher 시스템

```
[파운데이션 모델] (대형 오프보드)
        ↓ 전문화(Specialization) / 파인튜닝
  ┌─────┼──────┐
[Driver] [Simulator] [Critic]  ← 3대 Teacher (오프보드)
  ↓         ↓          ↓
[차량 내 경량 모델] [클라우드 훈련환경] [보상함수/평가]
```

| Teacher | 역할 | 실행 위치 |
|---------|------|---------|
| **Waymo Driver** | 실시간 자율주행 의사결정 | 차량 온보드 (실시간) |
| **Simulator** | 현실적인 합성 주행 환경 생성 | 클라우드 (훈련/평가) |
| **Critic** | 좋은/나쁜 행동 판별 → 보상 신호 | 오프보드 (RL 훈련) |

> "세 Teacher는 모두 동일한 파운데이션 모델에서 파생된다. 파운데이션 모델에 투자하면 세 방향 모두에 복리 효과가 발생한다." — Dolgov

### LLM 플레이북과의 대응 관계

| LLM 패러다임 | Waymo 물리 세계 대응 |
|------------|------------------|
| 텍스트 사전학습 | 수백만 마일 주행 데이터 학습 |
| RLHF (인간 피드백) | **RLFT** (강화학습 기반 파인튜닝) |
| Chain-of-Thought | 중간 표현 (Intermediate Representations) |
| RAG / 컨텍스트 | VLM에서 일반 세계 지식 상속 |
| 토큰 예측 | 미래 물리 상태 예측 (trajectories) |

## 센서 삼각편대 — 왜 LiDAR를 포기할 수 없나

### 3가지 센싱 모달리티

| 센서 | 원리 | 강점 | 약점 |
|------|------|------|------|
| **카메라** | 빛 반사 | 고해상도, 색상, 텍스트 인식 | 야간·역광·안개에서 저하 |
| **LiDAR** | 레이저 펄스 (초당 수백만 회) | 정밀 3D 공간 구조, 야간 무관 | 짙은 안개·폭설에서 약화 |
| **레이더** | 전파 반사 | 악천후(안개·눈·비)에 강건 | 해상도 낮음 |

> "각각의 노이즈 특성이 다른 환경에서 다르게 나타난다. 스위치가 아닌 조합이다. 맑은 날은 카메라가, 역광이나 야간은 LiDAR가, 짙은 안개는 레이더가 주도한다." — Dolgov

### 버스 뒤 보행자 — 창발 행동의 실증 사례

```
상황: 신호 대기 → 초록불 → 버스가 차선 절반 막음
      → 버스 옆으로 회피 기동 중 갑자기 감속·우측 회피

이유: 주변 LiDAR가 버스 하단 틈새로 반사파 탐지
     → 보행자 발의 움직임 감지 (카메라·레이더로는 불가)
     → "저쪽에 보행자 있을 가능성" 예측 후 행동
     → 실제 보행자가 버스 뒤에서 등장
```

**의미**: 순수 엔드투엔드(픽셀→궤적) 시스템으로는 이 수준의 안전 성능 달성 사실상 불가능. **중간 표현 + 다중 센서 융합**이 핵심.

## End-to-End vs 모듈형 — Dolgov의 결론

> "완전히 엔드투엔드인가? 그렇다. 하지만 완전 자율주행 규모에서는 구조화된 중간 표현으로 보강해야 한다."

```
순수 E2E (EMMA 논문):
  픽셀 입력 → VLM 파인튜닝 → 궤적 출력
  → 일반 상황에선 놀라울 정도로 잘 작동
  → 완전 자율화에 필요한 수준에서 "수 오더 오브 매그니튜드" 부족

Waymo 방식:
  E2E 아키텍처 + 중간 표현 보강
  → 시뮬레이터 효율적 운영 가능
  → 실시간 안전 검증 레이어 추가
  → Critic의 보상 함수 정교화 가능
```

## Waymo Driver 세대별 진화

| 세대 | 특징 | 의의 |
|------|------|------|
| **4세대** (2020) | 작은 AI 모델 다수, 애리조나 Chandler 상업 런칭 | 최초 완전 자율 유료 서비스 |
| **5세대** (현재) | **AI를 핵심 백본으로 큰 도박**, 전국 데이터, SF·피닉스 진출 | 불연속적 도약 — "이게 가능했던 이유" |
| **6세대** (2026 출시 예정) | Ojai 플랫폼 (맞춤 차량), 새 센서 스택, 비용 "5세대의 극히 일부" | 소프트웨어는 5세대와 동일, 하드웨어 혁신 |

> "5세대는 진정한 불연속 점프였다. 미국 전역에서 데이터를 수집하고, 가장 어려운 SF와 피닉스 환경에서 시작했다. 그 이후 지금의 확장이 가능해졌다." — Dolgov

### Ojai (6세대 차량) 특징
- 승객 중심 설계 (운전자 중심 → 승객 중심)
- 슬라이딩 도어, 플랫 플로어, 리빙룸 같은 공간감
- 외부 크기는 I-PACE와 유사하나 내부 공간 대폭 확대
- 현대 아이오닉 등 타 플랫폼에도 6세대 드라이버 탑재 예정

## 현재 운영 지표 (2026년 기준)

| 지표 | 수치 |
|------|------|
| 운영 차량 수 | ~3,000대 |
| 주간 라이드 | ~50만 건 |
| 주간 자율주행 마일 | 400만+ 마일 |
| 운영 도시 수 | 11개 (미국) |
| 누적 라이드 | 2천만 건 |
| 누적 자율주행 마일 | 2억 마일+ |
| 안전성 | 인간 대비 **13배** 적은 심각 부상/사망 사고율 |
| 부상 사고 | 인간 대비 **82% 감소** |
| 보행자 부상 | 인간 대비 **92% 감소** |
| 기업가치 (2026.02) | $1,260억 (투자금 $160억) |
| 글로벌 진출 예정 | 런던·도쿄 2026년 |

> "4개 도시에 처음 라이더를 태우기까지 8년 걸렸다. 지난주에는 하루에 4개 도시를 동시 런칭했다." — Dolgov

## 완전 자율주행 vs 운전 보조 — "질적 도약"

Dolgov의 핵심 주장:

> "운전 보조 시스템을 순차적으로 개선해서 완전 자율주행이 된다고 생각하는 건 착각이다. 이 두 가지는 동일 스펙트럼의 연속선이 아닌, 근본적으로 다른 문제다."

- Level 4/5 목표로 설계된 시스템 → 완전 자율주행
- Level 2/3 운전 보조 → 인간 감독이 전제, 절대 자율화로 자연 진화 없음

## 두 번째 오더 효과 — 자율주행이 도시를 바꾼다

```
단기: 교통 정체 감소
  → "Slow is smooth and smooth is fast" (Navy SEALs)
  → 급가속/급제동 없음 → 정체 전파파(Standing Wave) 해소

중기: 주차 공간의 해방
  → 현재 차량은 90% 이상 주차 상태
  → 자율 차량 = 항상 이동 가능
  → 도심 주차장·주차 빌딩 → 공원·주거·상업 공간

장기: 도시 설계 재편
  → 주차 의무 규정 폐지
  → 카페 야외 좌석, 공원 확장 등 가능
```

## 핵심 명언

> *"We've clearly moved past the stage of scientific research and deep core technology development to this new phase of accelerated global scaling and deployment."*
> — Dmitri Dolgov, Sequoia AI Ascent 2026

> *"The first time I saw it, I couldn't actually believe it."*
> — 버스 뒤 보행자를 LiDAR로 감지한 순간에 대해

## 참고 자료
- [YouTube: Waymo's Dmitri Dolgov — 20 Million Rides and the Road to Full Autonomy](https://www.youtube.com/watch?v=I_0Kuf6Aa2c)
- [Waymo 공식 블로그: The Waymo World Model](https://waymo.com/blog/2026/02/the-waymo-world-model-a-new-frontier-for-autonomous-driving-simulation/)
- [Waymo Research: EMMA (End-to-End Multimodal Model)](https://waymo.com/research/emma/)
- [Cheeky Pint: The 20-year journey to fully autonomous cars](https://cheekypint.substack.com/p/the-20-year-journey-to-fully-autonomous)

---
## 나의 코멘트
> ✍️

(Waymo의 Physical AI 아키텍처가 우리 사업·투자 전략에 주는 시사점을 여기에)
