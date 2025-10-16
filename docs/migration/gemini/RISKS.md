# Gemini Migration Risk Register

**Project:** MindMend AI Migration
**Date:** 2025-10-10
**Owner:** DevOps Lead / CTO

---

## Risk Assessment Matrix

| Risk Level | Impact | Probability | Action Required |
|-----------|--------|-------------|-----------------|
| **CRITICAL** | High | High | Immediate mitigation |
| **HIGH** | High | Medium | Mitigation plan required |
| **MEDIUM** | Medium | Medium | Monitor and prepare |
| **LOW** | Low | Low | Accept and document |

---

## Critical Risks

### RISK-001: API Quota Exhaustion
**Category:** Technical
**Probability:** MEDIUM
**Impact:** CRITICAL
**Risk Level:** HIGH

**Description:**
Vertex AI has per-project per-region quotas. During migration, we may exceed default quotas, causing service disruption.

**Triggers:**
- Sudden traffic spike
- Load testing without quota awareness
- Concurrent users exceed quota limits

**Impact:**
- Complete AI service outage
- 100% error rate on AI endpoints
- User-facing failures
- Revenue loss

**Mitigation:**
```bash
# Pre-migration: Request quota increase
gcloud alpha quotas update \
  --service=aiplatform.googleapis.com \
  --metric=generate_content_requests_per_minute \
  --value=2000 \
  --region=australia-southeast1 \
  --project=mindmend-production

# Implement rate limiting in application
# Set up quota monitoring alerts
```

**Contingency:**
- Immediate rollback to OpenAI
- Implement request queueing
- Activate fallback provider

**Status:** OPEN
**Owner:** Platform Engineer

---

### RISK-002: Model Quality Regression
**Category:** Product
**Probability:** MEDIUM
**Impact:** HIGH
**Risk Level:** HIGH

**Description:**
Gemini responses may not match OpenAI quality for mental health conversations, affecting user trust.

**Triggers:**
- Different model training data
- Prompt engineering differences
- Safety filter over-triggering

**Impact:**
- User dissatisfaction
- Increased churn
- Support ticket spike
- Reputation damage

**Mitigation:**
- Golden prompt evaluation (see TESTING_AND_EVALS.md)
- A/B testing with user feedback
- Gradual canary rollout (10% → 50% → 100%)
- Monitor user satisfaction scores

**Acceptance Criteria:**
- User satisfaction ≥ 4.5/5
- < 5% increase in negative feedback
- Therapy session completion rate maintained

**Contingency:**
- Roll back if satisfaction drops > 10%
- Adjust system prompts
- Consider Gemini Pro vs Flash models

**Status:** OPEN
**Owner:** Product Manager / AI Lead

---

### RISK-003: Cost Overrun
**Category:** Financial
**Probability:** MEDIUM
**Impact:** MEDIUM
**Risk Level:** MEDIUM

**Description:**
Gemini costs may exceed OpenAI costs if not properly optimized.

**Current Costs (OpenAI):**
- GPT-3.5 Turbo: $0.0015/1K input, $0.002/1K output
- Estimated monthly: $[TODO: Calculate]

**Target Costs (Gemini):**
- Gemini 1.5 Pro: $0.00125/1K input, $0.005/1K output
- Gemini 1.5 Flash: $0.000125/1K input, $0.000375/1K output

**Risk Factors:**
- Higher output token usage
- Longer context windows
- Inefficient model selection (Pro vs Flash)

**Mitigation:**
- Set billing alerts at 50%, 75%, 100% of budget
- Monitor token usage per endpoint
- Use Flash for simple tasks, Pro for complex
- Implement response caching
- Optimize prompts for token efficiency

**Budget:**
```bash
# Set budget alert
gcloud billing budgets create \
  --billing-account=<BILLING_ACCOUNT> \
  --display-name="Vertex AI Budget" \
  --budget-amount=5000 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=75 \
  --threshold-rule=percent=100
```

**Status:** OPEN
**Owner:** Finance / DevOps Lead

---

## High Risks

### RISK-004: Regional Latency
**Probability:** LOW
**Impact:** HIGH

**Description:**
australia-southeast1 may have higher latency than current asia-southeast1 deployment.

**Mitigation:**
- Benchmark latency before full rollout
- Consider CDN/caching layer
- Accept if latency p95 < 20% increase

**Status:** OPEN

---

### RISK-005: Authentication / IAM Issues
**Probability:** MEDIUM
**Impact:** HIGH

**Description:**
Workload Identity or service account misconfiguration could cause auth failures.

**Mitigation:**
- Thorough IAM testing in staging
- Document all required roles
- Test with limited permissions first

**Contingency:**
- Emergency service account key (break-glass)
- Fallback to OpenAI

**Status:** OPEN

---

### RISK-006: Safety Filter False Positives
**Probability:** MEDIUM
**Impact:** HIGH

**Description:**
Gemini's safety filters may block legitimate mental health discussions about self-harm, suicide, etc.

**Example:**
- User: "I'm having thoughts of self-harm but want help"
- Gemini: BLOCKED (safety filter)
- Result: User unable to get therapy

**Mitigation:**
- Comprehensive safety filter testing
- Tune safety thresholds
- Implement graceful error handling
- Log all blocked requests for review

**Testing:**
```bash
# Test safety filters with legitimate mental health prompts
./docs/migration/gemini/scripts/safety_filter_tests.sh
```

**Acceptance Criteria:**
- False positive rate < 2%
- All legitimate therapy discussions allowed
- Dangerous content still blocked

**Status:** CRITICAL - Test before production

---

## Medium Risks

### RISK-007: Streaming Response Differences
**Probability:** LOW
**Impact:** MEDIUM

**Description:**
Gemini streaming chunks may differ from OpenAI, affecting real-time UI.

**Mitigation:**
- Test streaming thoroughly
- Update frontend chunk handling if needed

**Status:** OPEN

---

### RISK-008: Token Counting Differences
**Probability:** MEDIUM
**Impact:** LOW

**Description:**
Different tokenization may affect usage tracking and billing.

**Mitigation:**
- Update token counting logic
- Monitor and adjust billing

**Status:** OPEN

---

### RISK-009: Migration Timeline Delays
**Probability:** MEDIUM
**Impact:** MEDIUM

**Description:**
6-week timeline may slip due to unforeseen issues.

**Mitigation:**
- Buffer time in schedule
- Prioritize critical paths
- Parallel work where possible

**Status:** ACCEPT

---

### RISK-010: Team Knowledge Gap
**Probability:** HIGH
**Impact:** MEDIUM

**Description:**
Team unfamiliar with Vertex AI, GCP APIs, and Gemini specifics.

**Mitigation:**
- Training sessions on Vertex AI
- Documentation (this migration kit)
- Pair programming during implementation

**Status:** IN PROGRESS (this documentation)

---

## Low Risks

### RISK-011: Documentation Staleness
**Probability:** MEDIUM
**Impact:** LOW

**Mitigation:** Regular doc reviews

**Status:** ACCEPT

---

### RISK-012: Rollback Practice Gaps
**Probability:** LOW
**Impact:** LOW

**Mitigation:** Monthly rollback drills

**Status:** OPEN

---

## Risk Monitoring

### Weekly Risk Review Agenda

1. Review all OPEN risks
2. Update probabilities based on progress
3. Add new risks discovered
4. Close mitigated risks
5. Escalate CRITICAL risks to leadership

### Risk Dashboard

```bash
# Generate risk status report
cat > /tmp/risk_report.sh << 'EOF'
#!/bin/bash
echo "=== MIGRATION RISK DASHBOARD ==="
echo "Date: $(date)"
echo ""
echo "Critical Risks: $(grep -c 'CRITICAL' docs/migration/gemini/RISKS.md)"
echo "High Risks: $(grep -c 'HIGH' docs/migration/gemini/RISKS.md)"
echo "Medium Risks: $(grep -c 'MEDIUM' docs/migration/gemini/RISKS.md)"
echo ""
echo "Open Risks:"
grep "Status: OPEN" docs/migration/gemini/RISKS.md | wc -l
EOF
chmod +x /tmp/risk_report.sh
```

---

## Acceptance Criteria for Go-Live

Migration CANNOT proceed to production unless:

- ✅ RISK-001 (Quotas): Quota increase approved
- ✅ RISK-002 (Quality): Golden prompts pass quality threshold
- ✅ RISK-003 (Cost): Budget alerts configured
- ✅ RISK-006 (Safety): False positive rate < 2%
- ✅ All CRITICAL risks mitigated or accepted by CTO

---

**Status:** Living Document (Update Weekly)
**Last Updated:** 2025-10-10
**Next Review:** [TODO: Schedule]
