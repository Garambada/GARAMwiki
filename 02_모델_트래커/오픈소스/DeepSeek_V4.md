---
생성일: 2026-05-20
최근_업데이트: 2026-05-20
카테고리: 모델트래커
신뢰도: 검토완료
출처: 노정석 AI Frontier EP95 — DeepSeek-V4 논문 읽기
---

# DeepSeek-V4 리뷰

> YouTube: https://www.youtube.com/watch?v=rJEMaldMyLE  
> 원논문 출시: 2026-04-24 | DeepSeek-AI

---

## 기본 정보

| 항목 | V4-Pro | V4-Flash |
|------|--------|---------|
| **개발사** | DeepSeek-AI (중국, 오픈소스) | DeepSeek-AI |
| **출시일** | 2026-04-24 | 2026-04-24 |
| **총 파라미터** | 1.6조 (1.6T) | 2840억 (284B) |
| **활성 파라미터** | 490억 (49B) / 토큰 | 130억 (13B) / 토큰 |
| **아키텍처** | MoE + CSA + mHC + Engram | MoE + CSA |
| **컨텍스트 윈도우** | 1M 토큰 | 1M 토큰 |
| **입력 단가 (1M 토큰)** | ~$0.28 | ~$0.07 |
| **출력 단가 (1M 토큰)** | ~$1.10 | ~$0.28 |
| **멀티모달 지원** | 텍스트 (멀티모달 지원 예정) | 텍스트 |
| **오픈 웨이트** | ✅ (Apache 2.0) | ✅ |
| **API 제공** | ✅ DeepSeek API | ✅ |

## 한 줄 포지셔닝

> **"프론티어 수준 수학·코딩 성능을, GPT-5.5 대비 85% 저렴하게"**

---

## 핵심 기술 혁신

### 1. Compressed Sparse Attention (CSA) + Heavily Compressed Attention (HCA)

DeepSeek-V4의 핵심. 1M 토큰 컨텍스트를 경제적으로 처리하기 위한 하이브리드 어텐션.

```
CSA (Compressed Sparse Attention):
  - 압축 비율 m으로 K/V 압축 → top-k 엔트리에만 sparse attention
  - 중요한 토큰은 정밀하게, 나머지는 효율적으로

HCA (Heavily Compressed Attention):
  - 더 극단적 압축 → dense attention으로 그룹 처리
  - 장거리 의존성 저비용 캡처

결과: V3.2 대비 KV Cache 90% 감소, FLOPs 27% 수준
```

### 2. Multi-Head Latent Attention (MLA) — V3 계승

히든 상태를 소형 잠재 벡터로 압축 후 attention 계산. KV Cache 메모리 요구량 대폭 감소. 특히 멀티스텝 에이전트 작업에서 장점.

### 3. Manifold-Constrained Hyper-Connections (mHC)

레이어 간 잔차(residual) 연결을 매니폴드 기하학적 제약 위에서 최적화. 학습 안정성 향상, 깊은 네트워크에서 그래디언트 소실 억제.

### 4. Engram Conditional Memory

생물학적 뇌의 Engram(기억 흔적) 개념 차용. 조건부 메모리 활성화로 장문 컨텍스트에서 관련 정보 선택적 강화. 200K+ 컨텍스트 추론 품질 향상.

### 5. Multi-Token Prediction (MTP) — V3 계승

단일 forward pass에서 여러 토큰 동시 예측. 256~384 전문가 중 6 routed + 1 shared expert 활성화. 추론 속도 향상.

---

## 아키텍처 비교 — DeepSeek 세대별

| 항목 | V2 | V3 / V3.2 | V4-Pro |
|------|-----|----------|--------|
| **총 파라미터** | 236B | 671B | 1.6T |
| **활성 파라미터** | 21B | 37B | 49B |
| **컨텍스트** | 128K | 128K | 1M |
| **핵심 어텐션** | MLA | MLA + MTP | MLA + MTP + CSA + HCA |
| **메모리 (KV Cache)** | 기준 | 기준 | 기준 대비 90% 감소 |

---

## 벤치마크 성능 (2026-04~05 기준)

| 벤치마크 | DeepSeek V4-Pro | Claude Opus 4.7 | GPT-5.5 | Gemini 3.1 Pro |
|---------|----------------|----------------|---------|---------------|
| **HMMT 2026 Feb** | **95.2%** | ~89% | ~91% | ~93% |
| **Putnam 2025** | **120/120** | 115/120 | 118/120 | 119/120 |
| **SWE-bench Verified** | **80.6%** | 64.3% (Pro) | ~75% | ~72% |
| **IMO Ans Bench** | 89.8% | ~86% | ~88% | ~91% |
| **GPQA Diamond** | ~85% | ~92% | ~88% | **94.6%** |

> 수학·코딩에서 최강, 과학 추론에서 Gemini에 밀림.

---

## 비용 비교 (입력 1M 토큰 기준)

| 모델 | 가격 | DeepSeek V4-Pro 대비 |
|------|------|-------------------|
| DeepSeek V4-Pro | **$0.28** | 1× (기준) |
| DeepSeek V4-Flash | $0.07 | 0.25× |
| GPT-5.5 | ~$1.90 | 6.8× 비쌈 |
| Claude Opus 4.6 | ~$15 | **54× 비쌈** |
| Gemini 3.1 Pro | ~$1.25 | 4.5× 비쌈 |

> 동급 최고 수준의 수학·코딩 성능을 54배 낮은 비용으로 → 원가 구조 파괴적.

---

## 강점

- **수학·정량 추론 최강**: Putnam 만점, HMMT 95% — 오픈소스 모델 중 전례 없는 수준
- **코딩 성능**: SWE-bench Verified 80%+ — Claude Pro, GPT-5.5 능가
- **1M 토큰 컨텍스트**: 실용적 비용으로 초장문 처리 가능 (CSA 덕분)
- **비용 파괴**: 프론티어 모델 대비 50~80배 저렴
- **오픈 웨이트**: Apache 2.0 — 완전 자체 호스팅, 파인튜닝, 상업적 사용 가능
- **KV Cache 효율**: V3.2 대비 90% 감소 → 셀프호스팅 GPU 요구량 대폭 감소

## 약점 / 한계

- **과학 추론**: GPQA Diamond에서 Gemini 3.1 Pro에 밀림 (85% vs 94.6%)
- **멀티모달 미지원**: 현재 텍스트 전용 (로드맵에 있음)
- **자체 호스팅 난이도**: 1.6T 파라미터 → 풀 모델 호스팅에 NVL72급 클러스터 필요
- **중국 기업 리스크**: 데이터 프라이버시, 지정학 리스크 고려 필요
- **에이전트 툴 생태계**: Claude, GPT 대비 툴/플러그인 생태계 미성숙

---

## 이 모델이 빛나는 유스케이스

1. **수학·정량 분석 자동화**: 금융 모델링, 통계 분석, 수식 기반 의사결정
2. **대용량 코드베이스 분석**: 1M 토큰으로 전체 레포지토리 한 번에 분석
3. **비용 민감 대량 처리**: 분류, 추출, 요약 파이프라인 (GPT/Claude 대비 80% 절감)
4. **RAG 파이프라인 백엔드**: 저비용 + 고성능으로 검색 증강 시스템 구성
5. **오픈소스 파인튜닝**: 도메인 특화 모델 커스터마이징 (Apache 2.0)

## 피해야 할 유스케이스

1. **이미지·멀티모달 처리**: 텍스트 전용, 멀티모달 불가
2. **의료·금융 데이터 처리**: 중국 기업 데이터 정책 리스크
3. **복잡한 과학 추론 단독 사용**: GPQA에서 Gemini/Claude에 밀림
4. **에이전트 툴 헤비 워크플로우**: Claude Code, GPT Actions 대비 생태계 미성숙

---

## 비용 계산 예시

```
시나리오: 내부 문서 RAG 파이프라인 (기존 Claude Opus 사용)

현재 (Claude Opus 4.6):
- 월 요청 수: 50,000회
- 평균 입력 토큰: 8,000 (문서 + 쿼리)
- 평균 출력 토큰: 800
- 월 비용: (50K × 8K × $15/M) + (50K × 800 × $75/M) ≈ $9,000

DeepSeek V4-Pro 전환 시:
- 입력: 50K × 8K × $0.28/M ≈ $112
- 출력: 50K × 800 × $1.10/M ≈ $44
- 월 비용: ~$156

절감: $9,000 → $156 = 98.3% 절감 (단, 성능·보안 검토 필요)
```

---

## C-레벨 전략 시사점

| 검토 항목 | 시사점 |
|---------|--------|
| **API 비용 감사** | 현재 GPT/Claude에 쓰는 비용의 수학·코딩 워크로드를 DeepSeek V4로 대체 시 ROI |
| **오픈소스 전략** | Apache 2.0으로 파인튜닝 자산화 가능. 도메인 특화 모델 내재화 경로 |
| **지정학 리스크** | 중요 데이터는 자체 호스팅 검토. API 버전은 데이터 정책 면밀 확인 |
| **경쟁 압력** | 중국 오픈소스가 프론티어 성능에 도달 → 미국 모델 가격 하락 압력 가속 |
| **MoE 아키텍처 이해** | 1.6T 파라미터 = 마케팅 숫자. 실제 연산은 49B. Roofline 분석으로 실제 GPU 비용 계산 |

---

## 참고 자료

- [노정석 AI Frontier EP95 — DeepSeek-V4 논문 읽기](https://www.youtube.com/watch?v=rJEMaldMyLE)
- [DeepSeek V4 Preview Release — DeepSeek API Docs](https://api-docs.deepseek.com/news/news260424)
- [DeepSeek-V4: 1M-Token Contexts via Compressed Sparse Attention](https://earezki.com/ai-news/2026-04-24-deepseek-ai-releases-deepseek-v4-compressed-sparse-attention-and-heavily-compressed-attention-enable-one-million-token-contexts/)
- [HuggingFace — DeepSeek-V4-Pro](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro)

## 나의 평가

> ✍️ 직접 써본 경험

(직접 테스트 후 기록)

---

*LLM wiki | 02_모델_트래커/오픈소스 | 2026-05-20*
