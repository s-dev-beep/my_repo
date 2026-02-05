# STEP 15 — Product Decision: Live Crawling Strategy

**Date:** February 2, 2026  
**Status:** Decision Required  
**Audience:** Product Leadership, Engineering Leadership, Legal/Compliance  
**Decision Deadline:** [To Be Set]

---

## 1. Executive Summary

### What Happened

We completed a controlled pilot test of our real estate listing crawler against Sahibinden.com, Turkey's largest property listing platform. The technical systems performed flawlessly—our safety mechanisms, error handling, and data integrity safeguards all worked as designed.

However, **Sahibinden blocked 100% of our requests** with HTTP 403 Forbidden errors. This was an expected outcome based on industry knowledge, but we needed empirical confirmation.

### What This Means

We have a **fully functional, production-ready crawler** that cannot currently access its primary data source without triggering defensive blocks. This is a strategic decision point, not a technical failure.

### Decision Required

**Do we invest in infrastructure to overcome blocks, negotiate access, pivot to alternatives, or pause this initiative?**

This document outlines four strategic paths forward, compares their costs and risks, and provides decision criteria for leadership.

---

## 2. What the Pilot Proved (Facts Only)

### Technical Validation ✅

| Component | Status | Evidence |
|-----------|--------|----------|
| **Data Extraction Logic** | Validated | Parsers tested against 100+ synthetic pages (STEP 1–9) |
| **Database Persistence** | Validated | MongoDB integration working, schema enforced |
| **Block Detection** | Validated | System correctly identified 3 consecutive 403s and stopped |
| **Safety Mechanisms** | Validated | Triggered automatic abort at 50% failure threshold |
| **Error Reporting** | Validated | Complete JSON report generated with failure categorization |
| **Data Integrity** | Validated | Zero partial writes; clean abort with no database corruption |

**Conclusion:** The crawler system is production-ready from an engineering perspective.

### Market Validation ❌

| Outcome | Result | Implication |
|---------|--------|-------------|
| **Sahibinden Access** | 100% blocked (403 Forbidden) | Cannot crawl without countermeasures |
| **Block Detection Speed** | 3 requests in <60 seconds | Sahibinden has aggressive anti-bot defenses |
| **Retry Tolerance** | 0% (blocked on first attempt) | Not a temporary network issue; permanent policy |
| **Alternative Test** | Not yet conducted | Unknown if Hepsiemlak or others have similar defenses |

**Conclusion:** Sahibinden actively prevents automated data extraction. This is a business/legal boundary, not a technical one.

### What We Did NOT Learn

- ❓ Would slower crawling (1 req/minute) avoid detection?
- ❓ Would residential proxies bypass blocks?
- ❓ Does Sahibinden offer a commercial API or data partnership?
- ❓ Are other Turkish property platforms equally restrictive?
- ❓ What are the legal risks if we escalate technical countermeasures?

---

## 3. Strategic Options

### Option 1: Proxy Infrastructure (Overcome Blocks Technically)

**Description:**  
Deploy rotating residential proxy network to distribute requests across thousands of IP addresses, making our traffic indistinguishable from organic users.

**What We'd Build:**
- Integrate commercial proxy service (BrightData, Oxylabs, Smartproxy)
- Add IP rotation logic to fetcher module
- Implement CAPTCHA solving service (2Captcha, Anti-Captcha)
- Enhanced rate limiting per proxy pool
- Monitoring dashboard for proxy health

**Timeline:** 4–6 weeks to production-ready

**Ongoing Costs:**
- Proxy service: $500–$2,000/month (scales with request volume)
- CAPTCHA solving: $2–$10 per 1,000 CAPTCHAs
- Infrastructure: $200/month (monitoring, logging, storage)
- **Total recurring:** ~$700–$2,200/month

**One-Time Costs:**
- Engineering time: 3–4 weeks (1 senior engineer)
- Testing/validation: 1 week
- Legal review: $5,000–$10,000 (outside counsel)

**Risks:**
- 🔴 **Legal:** Violating Sahibinden's Terms of Service may expose us to cease-and-desist or litigation
- 🟡 **Reputational:** If detected, Sahibinden may publicly call out our practices
- 🟡 **Technical:** Proxy providers can be blocked; requires ongoing maintenance
- 🟡 **Cost Escalation:** If Sahibinden hardens defenses, proxy costs may 2–3× within 6 months
- 🟢 **Controllable:** We can pause/resume based on monitoring

**Value:**
- ✅ Full access to Sahibinden's 500K+ active listings
- ✅ Real-time updates (hourly or daily crawls)
- ✅ Competitive data advantage (pricing trends, inventory levels)
- ✅ Enables downstream product features (price alerts, market analytics)

---

### Option 2: Negotiate Direct Access (Business Partnership)

**Description:**  
Approach Sahibinden with a commercial partnership proposal: pay for API access or bulk data export in exchange for proper attribution and traffic referrals.

**What We'd Do:**
- Identify Sahibinden's business development contact
- Prepare partnership pitch deck (value exchange, use case, compliance)
- Offer revenue share or referral fee structure
- Negotiate rate limits, data freshness, and pricing
- Integrate official API if granted access

**Timeline:** 3–6 months (negotiation cycles are slow)

**Costs:**
- Partnership fee: $10,000–$50,000/year (estimated; depends on negotiation)
- Revenue share: 5–15% of transactions originating from our platform
- Legal/contract negotiation: $10,000–$15,000
- API integration: 2 weeks engineering time
- **Total Year 1:** ~$20,000–$80,000

**Risks:**
- 🔴 **Rejection:** Sahibinden may refuse (they profit from exclusive traffic)
- 🟡 **Dependency:** If they revoke access, we lose primary data source
- 🟡 **Pricing Power:** They can raise fees arbitrarily; we have no leverage
- 🟢 **Legal Safety:** Official partnership eliminates scraping liability
- 🟢 **Reputation:** Positions us as ethical, compliant market participant

**Value:**
- ✅ Legal certainty (no ToS violations)
- ✅ Structured data (API is cleaner than HTML scraping)
- ✅ Official relationship (may unlock co-marketing opportunities)
- ✅ Stable access (no cat-and-mouse with anti-bot tech)
- ❌ **Lower margins** (partnership fees reduce profitability)

---

### Option 3: Pivot to Alternative Data Sources (Diversify)

**Description:**  
Accept that Sahibinden is inaccessible and focus on other Turkish property platforms (Hepsiemlak, Emlakjet, Zingat) plus public datasets (title registry, census).

**What We'd Do:**
- Test pilot crawls on 3–5 alternative platforms
- Identify which allow crawling (if any)
- Build parsers for accessible platforms only
- Supplement with public data (government APIs, open datasets)
- Position product as "multi-source aggregation" (not Sahibinden-dependent)

**Timeline:** 2–3 weeks for alternative pilots

**Costs:**
- Engineering: 1 week per new platform parser
- Infrastructure: Existing (no new costs)
- Data quality analysis: 1 week
- **Total:** ~$5,000–$10,000 (mostly engineering time)

**Risks:**
- 🟡 **Coverage Gap:** Sahibinden holds ~60% market share; alternatives may have limited inventory
- 🟡 **Same Problem:** Other platforms may also block (unknown until tested)
- 🟢 **Diversification:** Less vulnerable to single-platform policy changes
- 🟢 **Lower Cost:** No ongoing proxy or partnership fees

**Value:**
- ✅ Moderate coverage (40% market share across alternatives)
- ✅ Low ongoing costs
- ✅ Compliant (only crawl platforms that permit it)
- ❌ **Incomplete market view** (missing majority of listings)

---

### Option 4: Pause Crawling, Focus on User-Generated Data (Pivot Product Strategy)

**Description:**  
Abandon automated crawling entirely. Instead, build tools for property owners/agents to manually submit listings to our platform, positioning as a "direct from seller" marketplace.

**What We'd Do:**
- Build listing submission forms (seller dashboard)
- Offer free/freemium tools (property valuation, market analytics)
- Incentivize direct listings (premium placement, zero commission)
- Market to property agents as lead generation channel
- Shift value prop: "No middleman fees" vs. "Data aggregator"

**Timeline:** 8–12 weeks to MVP

**Costs:**
- Product redesign: 4 weeks (PM + Designer)
- Engineering: 6 weeks (frontend + backend)
- Marketing campaign: $20,000–$50,000 (user acquisition)
- **Total Year 1:** ~$50,000–$100,000

**Risks:**
- 🔴 **Market Position:** We become a competitor to Sahibinden, not a complementary service
- 🔴 **Network Effects:** Sahibinden has millions of users; we start at zero
- 🟡 **Revenue Delay:** User-generated platforms take 12–18 months to reach critical mass
- 🟡 **Unit Economics:** May need to offer paid acquisition incentives (unsustainable)

**Value:**
- ✅ Differentiated positioning (direct listings, lower fees)
- ✅ No legal/scraping risk
- ✅ Own the data (not dependent on external sources)
- ❌ **Unproven market fit** (requires significant user acquisition)
- ❌ **Long payback period** (18–24 months to profitability)

---

## 4. Cost / Risk / Value Comparison

### Summary Table

| Option | One-Time Cost | Recurring Cost (Annual) | Legal Risk | Technical Risk | Time to Value | Market Coverage | Strategic Fit |
|--------|--------------|------------------------|-----------|---------------|---------------|-----------------|---------------|
| **1. Proxy Infrastructure** | $20K | $8K–$26K | 🔴 High | 🟡 Medium | 6 weeks | 100% (Sahibinden) | Data aggregator |
| **2. Negotiate Access** | $25K | $20K–$80K | 🟢 Low | 🟢 Low | 3–6 months | 100% (Sahibinden) | Strategic partner |
| **3. Alternative Platforms** | $10K | $0 | 🟢 Low | 🟡 Medium | 3 weeks | 40% (other platforms) | Data aggregator |
| **4. User-Generated Pivot** | $100K | $50K+ (marketing) | 🟢 Low | 🟢 Low | 12+ months | 0% → 10% (Year 1) | Marketplace |

### Decision Matrix

| Criteria | Proxy | Partnership | Alternatives | Pivot |
|----------|-------|------------|--------------|-------|
| **Speed to Market** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| **Cost Efficiency** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Legal Safety** | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Market Coverage** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| **Scalability** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Defensibility** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 5. Recommendation Paths

### Path A: Proceed to STEP 16 (Proxy Infrastructure)

**When to Choose:**
- We need Sahibinden data **urgently** (within 2 months)
- We have risk tolerance for ToS violations
- We have $30K–$50K budget (Year 1 all-in)
- We're willing to play "cat and mouse" with anti-bot tech
- Legal has reviewed and accepted residual risk

**Next Steps:**
1. Legal sign-off on risk assessment (required before proceeding)
2. STEP 16: Design proxy rotation architecture
3. STEP 17: Implement automated crawling with proxies
4. STEP 18: Monitor block rates; optimize proxy pool
5. Continuous: Legal monitoring (watch for Sahibinden policy changes)

**Success Metrics (6 months):**
- 90%+ fetch success rate with proxies
- <5% block rate sustained over time
- Cost per listing < $0.10
- No legal action from Sahibinden

**Abort Criteria:**
- Block rate >20% despite proxy rotation
- Proxy costs exceed $3,000/month
- Sahibinden issues cease-and-desist
- Legal risk exceeds acceptable threshold

---

### Path B: Negotiate Access (Partnership-First)

**When to Choose:**
- We prioritize legal certainty over speed
- We have 3–6 month runway before needing data
- We can afford $20K–$80K/year partnership fee
- We value Sahibinden relationship over independence
- We want to position as compliant, ethical player

**Next Steps:**
1. Research Sahibinden's business development team (LinkedIn, press contacts)
2. Prepare partnership pitch deck (value prop, use case, revenue model)
3. Engage legal to draft partnership terms
4. Schedule introductory call with Sahibinden BD
5. Negotiate: data access, pricing, attribution, exclusivity

**Success Metrics (6 months):**
- Signed partnership agreement
- API access granted with acceptable rate limits
- Cost per listing < $0.05 (better than proxy route)
- Co-marketing opportunity explored

**Abort Criteria:**
- Sahibinden rejects partnership outright
- Partnership fee >$100K/year (uneconomical)
- Negotiation stalls >9 months
- Terms require exclusivity (blocks our other data sources)

---

### Path C: Diversify to Alternatives (Pragmatic Hedge)

**When to Choose:**
- We want to test market viability before heavy investment
- We can accept 40% market coverage (vs. 100%)
- We prioritize cost efficiency over completeness
- We're uncertain if Sahibinden access is even achievable
- We want to learn before committing to A or B

**Next Steps:**
1. Run pilot crawls on Hepsiemlak, Emlakjet, Zingat (next 2 weeks)
2. Measure block rates on each platform
3. Build parsers for accessible platforms only
4. Launch beta product with partial coverage
5. Revisit Sahibinden decision in 3 months (once we have traction data)

**Success Metrics (3 months):**
- 2–3 alternative platforms accessible (0% block rate)
- 50K+ listings in database (40% market coverage)
- User feedback: Is partial coverage acceptable?
- Product metrics: Engagement, retention, conversion

**Abort Criteria:**
- All alternatives also block us (same problem as Sahibinden)
- User research shows 40% coverage is insufficient
- Competitors launch with full Sahibinden coverage (we're at disadvantage)

---

### Path D: Pause Crawling (Preserve Optionality)

**When to Choose:**
- We lack budget for proxy/partnership ($30K+)
- Legal risk is unacceptable (conservative org culture)
- Product-market fit is unproven (we don't know if anyone wants this)
- We have other revenue priorities (crawling is deprioritized)
- We want to wait for regulatory clarity (e.g., EU DSA, Turkish data laws)

**Next Steps:**
1. Document current system state (STEP 1–15) for future reference
2. Archive codebase with clear README for future teams
3. Redirect engineering resources to other initiatives
4. Monitor market: Watch if competitors solve this, or if regulations change
5. Revisit decision in 6–12 months

**Success Metrics (12 months):**
- Zero ongoing costs (no wasted budget)
- Team redeployed to revenue-generating projects
- Market intelligence: Did competitors crack this? How?
- Regulatory landscape: Any favorable changes?

**Resume Criteria:**
- Competitor successfully launches Sahibinden-powered product (proof of demand)
- Regulatory change makes scraping legal/permissible
- Budget becomes available ($50K+ for partnership or proxy)
- New technical approach emerges (e.g., AI-based unblocking)

---

## 6. Decision Criteria (What Would Change Our Mind)

### Legal Clarity

**Current State:** Ambiguous. Scraping violates Sahibinden's ToS, but Turkish courts have limited precedent.

**What Would Change Our Decision:**

| Event | Impact | Recommended Response |
|-------|--------|---------------------|
| **Sahibinden sends cease-and-desist** | 🔴 High legal risk | Immediately halt crawling; pivot to Path B or D |
| **Turkish court rules scraping illegal** | 🔴 Regulatory barrier | Pause all crawling; wait for legislative clarity |
| **EU DSA requires data portability** | 🟢 Legal tailwind | Accelerate Path B (Sahibinden may be forced to provide API) |
| **Competitor successfully crawls without issue** | 🟡 Market precedent | Re-evaluate Path A risk (may be acceptable) |

### Market Validation

**Current State:** Unknown if users care about comprehensive coverage vs. partial coverage.

**What Would Change Our Decision:**

| Evidence | Impact | Recommended Response |
|----------|--------|---------------------|
| **User research: 90%+ say "need Sahibinden"** | High demand | Justify Path A or B investment |
| **User research: 40% coverage is acceptable** | Lower demand | Path C is sufficient (save budget) |
| **Competitor launches with full Sahibinden data** | Competitive pressure | Accelerate Path A or B to match |
| **Beta users churn due to missing listings** | Product-market fit issue | Prioritize Path B (quality over speed) |

### Technical Feasibility

**Current State:** Sahibinden blocks 100% of requests; unknown if proxies/CAPTCHAs solve this.

**What Would Change Our Decision:**

| Discovery | Impact | Recommended Response |
|-----------|--------|---------------------|
| **Proxy test: 95%+ success rate** | High confidence | Proceed with Path A |
| **Proxy test: <70% success rate** | Low confidence | Proxy cost/benefit unfavorable; pivot to Path B or C |
| **Alternative platforms allow crawling** | Viable workaround | Path C becomes primary strategy |
| **Sahibinden hardens defenses (fingerprinting, ML)** | Arms race escalation | Reconsider cost/benefit; may favor Path B or D |

### Budget Constraints

**Current State:** Budget not yet allocated; decision pending product prioritization.

**What Would Change Our Decision:**

| Budget Scenario | Impact | Recommended Response |
|-----------------|--------|---------------------|
| **$10K available (Year 1)** | Constrained | Path C only (alternatives + free sources) |
| **$30K–$50K available** | Moderate | Path A feasible (proxy route) |
| **$80K+ available** | Well-funded | Path B feasible (partnership route) |
| **Zero budget** | Blocked | Path D (pause until budget allocated) |

### Competitive Intelligence

**Current State:** Unknown how competitors source Sahibinden data (if at all).

**What Would Change Our Decision:**

| Competitor Action | Impact | Recommended Response |
|-------------------|--------|---------------------|
| **Competitor X has Sahibinden data** | Competitive gap | Urgently pursue Path A or B |
| **Competitor Y uses manual data entry** | No scraping advantage | Path D acceptable (level playing field) |
| **Competitor Z partners with Sahibinden** | Partnership precedent | Accelerate Path B (Sahibinden is willing to deal) |
| **All competitors blocked (same as us)** | Industry-wide issue | Path C or D acceptable (no disadvantage) |

---

## 7. Recommended Decision Process

### Step 1: Immediate (This Week)

**Decision Owner:** Product Leadership

**Questions to Answer:**
1. Is Sahibinden coverage a **must-have** or **nice-to-have** for product-market fit?
2. What is our risk tolerance for ToS violations (legal, reputational)?
3. What budget is available for Year 1 data sourcing?

**Required Input:**
- User research: Survey beta users on coverage expectations
- Legal review: Risk assessment of proxy-based scraping
- Finance: Budget allocation for data acquisition

### Step 2: Short-Term (2 Weeks)

**Decision Owner:** Engineering + Product

**Action:**
- Run pilot crawls on 3 alternative platforms (Hepsiemlak, Emlakjet, Zingat)
- Measure block rates, data quality, coverage
- Estimate: Can we launch with 40% coverage? Or is 100% required?

**Deliverable:**
- Feasibility report: Which platforms are accessible, which block us?

### Step 3: Decision Point (Week 3)

**Decision Matrix:**

```
IF (user_research == "Sahibinden required" AND budget >= $30K):
    IF (legal_risk_tolerance == "high"):
        → Path A (Proxy Infrastructure)
    ELSE:
        → Path B (Negotiate Partnership)

ELSE IF (alternative_platforms_accessible >= 2 AND user_research == "40% coverage OK"):
    → Path C (Diversify to Alternatives)

ELSE:
    → Path D (Pause Crawling)
```

### Step 4: Execution (Week 4+)

**Once path is chosen:**
1. Assign engineering resources
2. Set success metrics (6-month goals)
3. Define abort criteria (when to pivot)
4. Schedule quarterly review (reassess decision)

---

## 8. Summary & Next Steps

### What We Know

✅ **Technical:** Crawler system is production-ready  
✅ **Market:** Sahibinden blocks automated access (expected)  
✅ **Options:** Four viable strategic paths identified  
❓ **User Demand:** Unknown if Sahibinden coverage is critical  
❓ **Legal Risk:** Ambiguous; requires counsel review  
❓ **Budget:** Not yet allocated  

### What We Need to Decide

**This Week:**
1. Is Sahibinden access a strategic priority? (Product leadership)
2. What is our legal risk tolerance? (Legal + Exec team)
3. What budget is available? (Finance)

**Next 2 Weeks:**
4. Test alternative platforms (Engineering)
5. Survey beta users on coverage needs (Product)
6. Review legal risk assessment (Legal)

**Week 3:**
7. **Make GO/NO-GO decision** on Path A, B, C, or D

### Recommendation

**Start with Path C (Alternatives) as a low-risk test:**

- ✅ Low cost ($10K)
- ✅ Fast (2–3 weeks)
- ✅ Legally safe
- ✅ Provides real market feedback

**Then decide:**
- If users demand Sahibinden → escalate to Path A or B
- If 40% coverage is acceptable → continue with Path C
- If no traction → Path D (pause)

**This preserves optionality while minimizing wasted investment.**

---

## 9. Appendix: Reference Documents

- **STEP 14:** Live Crawling Policy (technical safeguards)
- **STEP 15:** Manual Live Pilot (execution plan + post-mortem template)
- **STEP15_live_pilot.json:** Pilot run report (actual results)
- **REFACTORING_SUMMARY.md:** System architecture overview

---

**Document Owner:** [Product Leadership]  
**Last Updated:** February 2, 2026  
**Next Review:** [Decision deadline date]

---

*End of STEP15_PRODUCT_DECISION.md*
