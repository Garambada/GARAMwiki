# LLM 추론 인프라 & 토큰 이코노믹스

> 출처: 노정석 AI Frontier EP96 — LLM Inference Infrastructure and Token Economics (2026-05-08)  
> YouTube: https://www.youtube.com/watch?v=V_Z-ydQJ54c  
> 원강의: Dwarkesh Patel의 칠판 강의 형식을 노정석이 한국어로 재해석

---

## 핵심 명제

> **"LLM 인프라의 모든 비용·성능 문제는 Prefill/Decode 분리와 KV Cache 메모리 병목으로 환원된다."**

토큰 경제학(Token Economics)은 이 물리적 제약에서 파생된다. API 가격 구조, GPU 플릿 규모, 자체 호스팅 의사결정 — 모두 같은 뿌리에서 나온다.

---

## 1. Prefill vs Decode — 두 가지 다른 병목

LLM 추론은 두 단계로 완전히 다른 성격을 가진다.

| 구분 | Prefill | Decode |
|------|---------|--------|
| **역할** | 입력 프롬프트 처리, KV Cache 채우기 | 토큰 1개씩 순차 생성 |
| **병목** | Compute-bound (FLOPs 한계) | Memory-bound (HBM 대역폭 한계) |
| **병렬성** | 입력 토큰 전체를 동시 처리 가능 | 토큰마다 KV Cache 전체를 읽어야 함 |
| **속도 감각** | 빠름 (배치 처리) | 느림 (순차, 한 토큰씩) |
| **비용 드라이버** | GPU FLOP/s | GPU HBM 대역폭 |

### 왜 Decode가 느린가?

Decode 단계에서는 새 토큰 하나를 생성할 때마다 **지금까지 생성된 모든 토큰의 KV Cache를 전부 읽어야 한다.** 컨텍스트가 길수록 읽어야 할 데이터가 선형으로 늘어난다.

반면 계산(FLOPs)은 토큰 1개 생성 분밖에 안 된다 → **산술 강도(Arithmetic Intensity)가 극단적으로 낮음** → Memory-bound 고착.

---

## 2. Roofline 분석 — 병목을 수식으로

```
t_mem     = 메모리 접근 바이트 수 / HBM 대역폭 (TB/s)
t_compute = 필요 FLOPs / GPU FLOP/s

실제 소요 시간 = max(t_mem, t_compute)
```

### H100 / Blackwell 기준값

| 하드웨어 | HBM 대역폭 | FLOP/s (BF16) |
|---------|-----------|---------------|
| H100 SXM | ~3.35 TB/s | ~989 TFLOP/s |
| Blackwell B200 | ~8 TB/s | ~4,500 TFLOP/s |

**Decode 병목 직관:** 70B 모델 파라미터 = ~140GB (BF16). HBM 3.35 TB/s로 읽으면 토큰당 약 42ms. 토큰/초로 환산하면 약 24 tok/s 상한선. 배치를 키우지 않으면 GPU의 FLOPs는 90%+ 유휴 상태.

### 배치 사이즈와 효율

```
배치 사이즈 ↑ → 토큰당 메모리 접근 고정 / FLOPs 증가
→ Arithmetic Intensity 상승 → Compute-bound 영역 진입 가능
→ GPU 이용률 상승, 단가 하락
```

API 사업자가 수천 명 요청을 묶어 배치 처리하는 것이 핵심 원가 우위의 원천.

---

## 3. KV Cache — 메모리 경제의 핵심

### 구조

- **K(Key)와 V(Value)**: Transformer attention 계산 시 각 레이어·헤드별로 생성
- **크기**: 모델 크기 × 레이어 수 × 헤드 수 × 시퀀스 길이에 비례
- **70B 모델, 128K 컨텍스트**: KV Cache만 수십 GB 이상 소비 가능

### Prefill이 KV Cache를 채운다

```
[입력 토큰 전체] → Prefill → KV Cache 완성
                              ↓
                         Decode 시작
[토큰1] ← KV Cache 전체 읽기
[토큰2] ← KV Cache + 토큰1 읽기
[토큰3] ← KV Cache + 토큰1 + 토큰2 읽기
...
```

### KV Cache 재사용 (Prompt Caching)

동일한 시스템 프롬프트·문서가 반복 사용되면 KV Cache를 저장·재사용 가능.  
→ API 제공업체의 **Cached Input** 가격 할인 근거.

### PagedAttention (vLLM)

OS의 가상 메모리 페이지 방식을 KV Cache에 적용. 메모리 단편화 최소화, 동시 처리 요청 수(throughput) 대폭 향상.

---

## 4. 토큰 이코노믹스 — 가격 구조의 물리적 근거

### 가격 계층

```
Input tokens  <  Cached Input tokens  <<  Output tokens
    (1×)              (0.1~0.3×)            (3~10×)
```

| 토큰 유형 | 물리적 이유 | 가격 |
|----------|-----------|------|
| **Input** | Prefill 처리, 배치 효율 좋음 | 기준 |
| **Cached Input** | KV Cache 재사용, 실제 연산 거의 없음 | 70~90% 할인 |
| **Output** | Decode 순차 처리, HBM 대역폭 독점 소비 | 3~10배 비쌈 |

### 200K 컨텍스트 임계점

긴 컨텍스트는 KV Cache를 HBM 전체를 차지할 수 있음.  
→ 일부 제공업체가 200K 이상에서 추가 과금 또는 별도 가격 책정.  
→ 장문서 처리 애플리케이션 설계 시 주요 비용 변수.

### 비용 최적화 전략 매트릭스

| 패턴 | 최적화 방법 | 절감율 |
|------|-----------|--------|
| 반복 시스템 프롬프트 | Prompt Caching 활용 | 50~80% |
| 장문 문서 분석 | 한 번 캐시 → 다회 질의 | 70~90% |
| Output 최소화 | 구조화된 짧은 응답 유도 | 30~60% |
| 배치 처리 | 비실시간 작업 배치 API | 50% |

---

## 5. Erlang-C 대기열 이론 — GPU 플릿 규모 결정

### 핵심 통찰: 수요 분산(Variance)이 비용을 결정한다

GPU 플릿을 몇 개 운영해야 하는가? 평균 수요량이 아니라 **수요의 변동계수(CV, Coefficient of Variation)**가 결정한다.

```
CV = 표준편차 / 평균

CV = 0   → 수요 완전 예측 가능, GPU = 평균 수요량
CV = 0.3 → 버퍼 30~50% 필요
CV = 1.0 → GPU 2~3배 과잉 프로비저닝 필요
CV > 1   → 비용 폭발, 자체 호스팅 불가
```

### 자체 호스팅 손익분기점

**자체 호스팅이 경제적으로 유리한 조건:**
```
수요 CV < 0.3~0.4  AND  월 GPU 비용 > API 비용
```

대부분의 기업에서 수요 CV는 0.5~2.0 수준 → **자체 호스팅은 비경제적**.

---

## 6. API 사업자의 구조적 우위 — 수요 풀링

### 통계적 다각화 효과

```
고객 N명의 수요를 통합 처리 시:
통합 수요 변동 = 개별 변동 / √N

N = 1,000명 → 변동 1/32로 축소
N = 10,000명 → 변동 1/100로 축소
```

Anthropic, OpenAI는 수만 명의 수요를 풀링 → CV가 극단적으로 낮음 → GPU 이용률 90%+ 달성 가능.

개별 기업이 자체 호스팅 시 이 이점을 누릴 수 없음.

### 자체 호스팅이 유효한 예외 케이스

| 조건 | 설명 |
|------|------|
| 규제·보안 요구 | 데이터가 외부 나갈 수 없는 의료·금융·국방 |
| 극도로 예측 가능한 수요 | 배치 처리만 하는 내부 파이프라인 |
| 초대형 스케일 | 자체 GPU 수천 개 이상, 자체 풀링 가능 |
| 파인튜닝 필수 | 범용 API로 성능 충족 불가한 도메인 |

---

## 7. 서빙 프레임워크 선택 — vLLM vs SGLang

| 항목 | vLLM | SGLang |
|------|------|--------|
| **강점** | 범용성, 안정성, 생태계 | 다중 호출 워크플로우 최적화 |
| **적합 용도** | 채팅·완성 API | 에이전트·멀티스텝 파이프라인 |
| **KV Cache** | PagedAttention | RadixAttention (공유 prefix 캐시) |
| **TTFT 개선** | 기준 | 30~60% 단축 (공유 prefix 시) |
| **커뮤니티** | 더 큰 생태계 | 연구·고성능 팀 선호 |

**선택 기준:**
- 단순 Chat/Completions API → vLLM
- 에이전트가 같은 시스템 프롬프트로 수십 회 호출 → SGLang
- RAG + 동일 문서 반복 참조 → SGLang (RadixAttention으로 prefix 공유)

---

## 8. NVIDIA 하드웨어 생태계

### Blackwell NVL72 구성

```
72 GPU → NVLink로 내부 연결 → NVSwitch로 토폴로지 관리
→ 단일 논리 GPU처럼 동작 가능
→ 초대형 모델(GPT-4급 이상) 서빙의 사실상 표준
```

### MoE (Mixture of Experts)

- **원리**: 입력마다 일부 전문가 네트워크만 활성화
- **효과**: 전체 파라미터의 20~30%만 실제 연산 → Compute 효율 4~5배
- **트레이드오프**: 전문가 로드밸런싱 복잡, 메모리는 전체 파라미터 유지 필요

---

## 9. C-레벨 전략 적용

### 즉각 검토 (30일)

1. **현재 LLM API 지출 감사**: Input/Cached/Output 비율 분석 → Prompt Caching 도입 여부 결정
2. **수요 CV 측정**: 내부 LLM 호출 패턴의 시간대별 분산 계측
3. **자체 호스팅 ROI 재계산**: Erlang-C 기반으로 실제 GPU 프로비저닝 필요량 산출

### 중기 설계 (3~6개월)

1. **에이전트 아키텍처 최적화**: 다중 호출 에이전트 파이프라인에 SGLang 또는 shared prefix 캐싱 적용
2. **Output 토큰 경제화**: 프롬프트 엔지니어링으로 출력 토큰 압축 → 비용의 50~70% 절감 가능
3. **컨텍스트 길이 전략**: 200K 임계점을 넘지 않는 청킹 전략 vs. 긴 컨텍스트의 생산성 가치 비교

### 장기 포지셔닝 (1년+)

| 질문 | 검토 방향 |
|------|----------|
| 우리 제품의 LLM 비용 구조는? | Output 중심이면 가격 경쟁에 취약. 캐싱 가능한 구조 설계 |
| GPU 확보 전략은? | Blackwell 선예약 vs. 온디맨드 API의 장기 계약 비교 |
| 수직화 vs. 범용 API? | 도메인 특화 파인튜닝이 필요한가? CV 0.3 이하 달성 가능한가? |

---

## 참고 링크

- [노정석 AI Frontier EP96](https://www.youtube.com/watch?v=V_Z-ydQJ54c)
- [vLLM 공식 문서](https://docs.vllm.ai)
- [SGLang GitHub](https://github.com/sgl-project/sglang)
- [Hebbia: Hidden Economics of LLM Inference](https://www.hebbia.ai/post/hidden-economics-of-llm-inference)

---

*LLM wiki | 01_개념사전/시스템_패턴 | 2026-05-20*
