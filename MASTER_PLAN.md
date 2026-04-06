# MASTER_PLAN

This document is the long-term source of truth for the project. It defines the business logic, architecture direction, constraints, assumptions, risks, and phased roadmap for the first working system and for later expansion. Future implementation decisions should be checked against this document before code is written.

## 1. Main Goal

The project goal is to build a repeatable, low-cost, always-on content operations system for a solo operator.

The system is intended to do one thing well:

1. discover simple content formats that already perform well in the market,
2. transform that material into cleaner, easier-to-consume blog content,
3. transform the blog content into Facebook-ready distribution assets,
4. drive Facebook traffic to the blog,
5. monetize blog visits through ads,
6. later identify winners and scale them.

This is not a general AI content lab, not an autonomous publishing fantasy, and not a research-heavy editorial product. The project is a traffic and monetization machine built around source selection, formatting discipline, controlled reuse, and distribution execution.

The system should be understandable, maintainable, and affordable for one person to run. Every v1 decision should favor clarity, predictability, and operational usefulness over novelty.

## 2. Business Model

The business model is:

Facebook Attention -> Blog Click -> Ad Revenue

The system makes money by turning lightweight, curiosity-driven, broad-interest content into pageviews on a monetized blog. Those pageviews can later be monetized through ad programs such as AdSense first, and potentially higher-yield ad platforms later if traffic quality and scale improve.

### Why this content model works

This model works when three conditions are true:

1. the content topic is broadly interesting and easy to understand,
2. the formatting is optimized for fast consumption on mobile,
3. the distribution channel reliably generates clicks.

The project is not relying on deep originality as the main value driver. It is relying on packaging, accessibility, timing, format fit, and distribution. The system wins by making useful or interesting content easier to consume and easier to click into.

### Why distribution matters more than deep originality

For this business, reach matters more than literary depth. A perfectly original article with no distribution is economically weak. A well-packaged derivative article with strong distribution and clear formatting can be commercially valuable if it reliably produces pageviews without collapsing quality.

This does not mean quality is optional. It means the most important quality dimensions for this project are:

1. source quality,
2. structure quality,
3. mobile readability,
4. click-driving packaging,
5. consistency of execution.

### Why the blog exists

The blog exists as the monetization and conversion destination.

It is the place where content is:

1. formatted properly,
2. archived,
3. owned by the operator,
4. monetized with ads,
5. later measured and compared.

The blog is not just a place to store text. It is the revenue layer and content archive of the system.

### Why Facebook exists in the model

Facebook is the primary v1 attention engine. It is the place where short, curiosity-driven content packaging can generate attention cheaply. Facebook posts are not side outputs. They are critical top-of-funnel assets that must be designed with the same seriousness as the blog articles.

The Facebook Page is the first channel because it is simpler to control than broader multi-channel publishing and creates a manageable operational loop for v1.

### What role ads play

Ads are the initial monetization mechanism. The content system is not being built first for subscriptions, product sales, or affiliate funnels. It is being built for traffic monetization through ad-supported pageviews.

This matters architecturally because it means:

1. traffic volume matters,
2. consistency matters,
3. ad-friendly formatting matters,
4. low-cost content operations matter,
5. the system must avoid low-value patterns that threaten future monetization.

### Long-term expansion path

The long-term path is:

1. test content organically,
2. identify what gets clicks and what keeps getting reused successfully,
3. find winner patterns,
4. later consider paid amplification for proven winners.

Paid boosting is not part of v1. Organic testing is the validation layer. Paid amplification, if used later, should come after the system has enough tracking to identify which topics, sources, titles, and hooks consistently outperform.

## 3. Current Idea

The current idea is to build a small, disciplined content machine rather than a broad media platform.

In plain language, the system should:

1. find simple, high-potential food-related content from trusted or useful web sources,
2. clean and normalize the source material,
3. format it into short, mobile-friendly blog content using templates,
4. create Facebook-ready hooks, captions, and comment CTAs from that blog content,
5. publish through a scheduled queue with human approval,
6. maintain low operating costs,
7. later add decision intelligence once enough data exists.

The intended workflow is not "ask AI to write articles." The intended workflow is "retrieve, clean, structure, package, publish, and later learn."

## 4. Recommended Direction

The recommended architecture and build order is:

1. build the Source Engine first,
2. build the Content Engine second,
3. build the Social Packaging Engine and Distribution Engine third,
4. build the Tracking foundation next,
5. activate the full system in a real operator environment before more complexity is added,
6. improve bounded content quality with optional AI after activation is proven,
7. add the missing media and visual layer after the connected text system is stable,
8. lock the runtime operations and deployment model after the connected system is complete enough to run for real,
9. build the approval UI and operator console before the Decision layer so human review has a stable home,
10. build the Decision layer after the operational system is complete enough to generate meaningful history,
11. add approval automation only after the Decision layer proves that scoring can be trusted,
12. build the Scaling layer last.

### Why this order is the cleanest and safest

This order is recommended because the project's leverage comes from the inputs first, not from orchestration magic.

If the Source Engine is weak, everything downstream becomes low-value. If the Content Engine is weak, distribution assets become weak. If the Distribution Engine exists before stable content formatting exists, the system just scales inconsistency. If intelligence is added before data exists, the system becomes expensive and speculative.

This order preserves the project principles:

1. simplicity over complexity,
2. source quality over model quality,
3. formatting over unconstrained generation,
4. data before intelligence,
5. deterministic systems before orchestration.

It also reduces the chance of building an impressive-looking but commercially fragile system.

It also forces one more important decision before Decision Layer work begins:

1. how the system actually runs every day after build,
2. where the worker lives,
3. how recurring jobs fire,
4. how data is backed up,
5. how the solo operator recovers from failure without improvising.

## 5. System Split / Subprojects

The project should be treated as a set of related engines rather than one giant monolith. Each engine should have a clear contract, limited responsibilities, and clean inputs and outputs.

### 5.1 Source Engine

**Purpose**

The Source Engine is responsible for finding and normalizing candidate content items.

**Key responsibilities**

1. manage the curated source registry,
2. fetch source items through RSS first and scraping only when necessary,
3. normalize raw source records,
4. classify source material at a basic topic/template-fit level,
5. detect duplicates or near-duplicates before content work starts.

**Inputs**

1. source registry entries,
2. RSS feeds,
3. selective scraping targets,
4. source metadata and configuration.

**Outputs**

1. normalized source items,
2. cleaned extraction-ready content candidates,
3. classification metadata,
4. dedupe flags,
5. source-level audit records.

**Why it exists separately**

Source selection is the highest-leverage and hardest part of the system. It deserves its own engine because content quality and distribution outcomes are downstream consequences of source quality.

### 5.2 Content Engine

**Purpose**

The Content Engine turns normalized source material into structured blog drafts.

**Key responsibilities**

1. clean extracted content,
2. apply blog templates,
3. generate controlled micro-enhancements,
4. produce standardized draft articles,
5. run quality checks before draft approval.

**Inputs**

1. normalized source item,
2. cleaned source body,
3. selected template,
4. AI skills for small enhancements,
5. quality rules.

**Outputs**

1. blog draft content,
2. draft title options,
3. excerpt,
4. tags and category suggestions,
5. review status and quality flags.

**Why it exists separately**

This engine is about deterministic formatting and controlled enhancement. It should not be entangled with source retrieval or social publishing logic.

### 5.3 Social Packaging Engine

**Purpose**

The Social Packaging Engine derives Facebook-specific assets from the approved blog draft.

**Key responsibilities**

1. create hook variants,
2. create short captions,
3. create soft CTA options,
4. create comment CTA lines,
5. map each social package back to the underlying blog post.

**Inputs**

1. approved or near-approved blog draft,
2. packaging templates,
3. lightweight AI enhancement skills,
4. distribution rules.

**Outputs**

1. Facebook-ready post text variants,
2. comment CTA variants,
3. mapping records to the blog post and source item,
4. packaging metadata for scheduling.

**Why it exists separately**

Facebook packaging is a first-class business function, not a side effect of article generation. It needs separate templates, tone control, and performance tracking.

### 5.4 Distribution Engine

**Purpose**

The Distribution Engine publishes approved content to WordPress and manages Facebook scheduling.

**Key responsibilities**

1. maintain the publishing queue,
2. support human approval,
3. publish to WordPress,
4. schedule or publish Facebook Page content,
5. record publish events and IDs.

**Inputs**

1. approved blog content,
2. approved Facebook packaging,
3. scheduling metadata,
4. queue state.

**Outputs**

1. published WordPress post IDs,
2. Facebook post mappings,
3. queue transitions,
4. publish history.

**Why it exists separately**

Publishing concerns are operational concerns. They should not contaminate content logic with platform-specific rules, retries, scheduling state, or approval workflows.

### 5.5 Tracking / Decision Engine

**Purpose**

The Tracking / Decision Engine stores the minimum data required to understand what was published and later determines which content patterns are worth repeating or promoting.

**Key responsibilities**

1. store publication records,
2. maintain source-to-blog-to-social mappings,
3. capture variant references where relevant,
4. later evaluate simple winner signals,
5. later prioritize future sourcing, formatting, and packaging choices.

**Inputs**

1. publish history,
2. source metadata,
3. draft metadata,
4. social packaging metadata,
5. later performance metrics.

**Outputs**

1. reporting-ready records,
2. candidate winner lists,
3. source and template feedback signals,
4. promotion candidates in later phases.

**Why it exists separately**

Tracking should begin simple, but it will eventually become the intelligence substrate. Keeping it separate now makes later scaling and analysis cleaner.

## 6. Content Strategy

The first niche is **food facts**.

### Why food facts were chosen

Food facts are a practical v1 niche because they are:

1. broad-interest,
2. easy to understand quickly,
3. well suited to curiosity packaging,
4. relatively easy to format for mobile reading,
5. less operationally risky than stronger claim-heavy categories,
6. suitable for repeated templating without needing deep original reporting.

Food facts also fit the Facebook attention model well. A small fact, contrast, habit, origin story, preparation note, or surprising comparison can become a blog article and also produce multiple short social hooks.

### Content characteristics for v1

The initial content style should be:

1. simple,
2. broad-interest,
3. curiosity-driven,
4. fast to scan,
5. visually and structurally mobile-friendly,
6. appropriate for a Facebook-first traffic loop.

The blog content should read like a cleaned and structured explanation, not like an essay. Paragraphs should be short. Sectioning should be obvious. Titles should be curiosity-oriented but not misleading.

### Why we are not starting with stronger health claims

Health-heavy content creates higher risk around credibility, policy sensitivity, tone, and quality control. It is too easy for the system to drift into exaggerated or weakly supported claims, especially in a derivative content model. Food facts allow useful breadth without anchoring the system in a high-risk claims category too early.

### Why we are not starting with general curiosity

General curiosity is too broad as a first niche. It weakens source selection, template discipline, and category focus. Food facts are broad enough to support volume but narrow enough to support consistent sourcing and formatting.

### Why we are not starting with SEO-first content

V1 is not an SEO-first editorial system. The initial traffic engine is Facebook. The goal is to create a repeatable content and packaging loop, not to build long-tail SEO depth from day one. SEO can benefit later from the content archive, but it is not the primary operating assumption for the first build.

## 7. Content Production System

The content production system is:

Retrieval -> Cleaning -> Template Formatting -> Light AI Enhancement

This is the central production model of the project.

The following statements are mandatory and non-negotiable for v1:

1. the system does not generate full articles from scratch,
2. it repackages source material into a more consumable format,
3. structure is more important than creativity,
4. templates are mandatory infrastructure,
5. AI is tightly constrained and subordinate to the formatting system.

### 7.1 Retrieval

Retrieval is the process of obtaining candidate content from the curated source registry.

Retrieval rules for v1:

1. use a curated source registry,
2. prefer RSS-based intake first,
3. use selective scraping where RSS is unavailable or insufficient,
4. add sources manually over time,
5. do not build a broad crawler-first architecture for v1.

The retrieval layer should focus on collecting stable candidate inputs, not on "discovering the internet." Good source curation beats broad noisy scraping.

### 7.2 Cleaning

Cleaning prepares raw source material for deterministic formatting.

Cleaning tasks include:

1. removing junk and extraction noise,
2. removing repeated blocks,
3. removing irrelevant navigation or boilerplate fragments,
4. normalizing whitespace and section structure,
5. preparing the material for classification and templating.

The cleaning stage should reduce ambiguity before any AI enhancement is applied. Clean inputs are cheaper to work with and produce more stable outputs.

### 7.3 Template Formatting

Template formatting is the core content transformation mechanism.

Templates are fixed output structures used to standardize the presentation of content. They determine the shape of the output and define what content slots must exist.

Templates improve:

1. consistency,
2. low-cost production,
3. automation readiness,
4. reviewability,
5. scalability,
6. quality control.

Without templates, the system becomes prompt-driven and inconsistent. With templates, the system becomes predictable and extensible.

Template formatting in practice should also include a deterministic content-fit and anchor-quality check. Not every valid source item is automatically a clean fit for the current short explainer templates. The system should explicitly detect noisy boilerplate, recipe-heavy context, and weak anchor terms before trusting the draft shape. This is a foundation concern, not a later polish step.

#### Example blog template categories

**Food fact article**

Typical structure:

1. curiosity headline,
2. short intro,
3. key fact or answer,
4. supporting explanation,
5. simple bullets or sections,
6. closing summary,
7. soft read-more or related-content bridge.

**Food benefit article**

Typical structure:

1. benefit-oriented headline,
2. short context-setting intro,
3. simple explanation of the food and its relevance,
4. a structured list of practical points,
5. a caution against overstating claims,
6. soft conclusion.

**Curiosity article**

Typical structure:

1. surprising question headline,
2. fast answer,
3. short explanatory sections,
4. one or more supporting examples,
5. concise close.

#### Example Facebook template categories

**Curiosity hook post**

Structure:

1. open loop,
2. short fact tease,
3. click invitation.

**Short caption post**

Structure:

1. single sharp observation,
2. brief framing line,
3. soft CTA.

**Soft CTA post**

Structure:

1. curiosity or utility hook,
2. one-line benefit of clicking,
3. non-aggressive CTA.

#### Example comment CTA templates

**Link placement line**

Example purpose:

1. place the article link naturally in comments,
2. reinforce that the full explanation is on the blog,
3. avoid hard-sell language.

**Short curiosity reinforcement**

Example purpose:

1. keep the open loop alive,
2. nudge interested readers,
3. support clickthrough without sounding spammy.

**Non-spammy prompt to read more**

Example purpose:

1. invite readers to continue,
2. clarify that the blog has the full details,
3. avoid exaggerated claims or engagement bait.

### 7.4 Light AI Enhancement

AI is permitted only for narrow, controlled, slot-based tasks.

Allowed uses:

1. titles,
2. short intros,
3. Facebook hooks,
4. CTA wording,
5. short rewrites for flow,
6. excerpt generation,
7. minor tone normalization.

Disallowed use in v1:

1. generating full articles from scratch,
2. inventing unsupported claims,
3. free-form long-form editorial writing,
4. replacing the template layer with prompting,
5. deciding business strategy autonomously.

Full-article generation is disallowed because it increases cost, reduces consistency, raises derivative and quality risks, and weakens the deterministic architecture the project depends on.

## 8. Content Skills

In this project, "skills" are small reusable transformations with narrow scope and predictable inputs and outputs. A skill is not a free-form chat interaction. A skill is a controlled operation that can be called inside the content pipeline.

### Blog skills

**generate_headline_variants**

Create a small set of title options based on the selected template and cleaned source material.

**generate_short_intro**

Produce a short introduction paragraph that matches the article type and makes the structure feel complete.

**format_article_sections**

Convert normalized facts or extracted points into the expected blog template structure.

**generate_excerpt**

Create a short summary or excerpt for WordPress usage and archive readability.

**assign_tags_and_category**

Assign the article to a standard category and suggest tags from a controlled taxonomy.

### Facebook skills

**generate_hook_variants**

Produce several short hook options suitable for Facebook testing.

**generate_curiosity_caption**

Create a concise caption that supports click intent without revealing everything.

**generate_comment_cta**

Create one or more comment lines for link placement or soft click prompts.

### Quality skills

**check_readability**

Ensure the article is easy to scan, sentence length is reasonable, and sectioning is clear.

**check_structure_complete**

Ensure the selected template was fully populated and no required sections are missing.

**check_derivative_risk**

Look for signals that the output is too close to source phrasing or too thinly transformed.

**check_mobile_friendly_formatting**

Ensure paragraphs, bullets, and section lengths are suitable for mobile reading.

These skills are controlled utilities. They exist to enforce repeatability, not to replace the system with general-purpose AI generation.

## 9. Platform and Delivery Strategy

The chosen v1 platform and delivery strategy is:

1. Facebook Page first,
2. WordPress for the blog,
3. Facebook Groups deferred,
4. paid boosts deferred,
5. scheduled queue with human approval.

### Facebook Page first

This is the right v1 choice because it gives the operator a manageable, consistent publishing surface. It reduces coordination overhead and keeps the system focused on one primary social feedback loop instead of fragmenting effort too early.

### WordPress first

WordPress is the right v1 choice because it is mature, widely supported, operationally practical, and well suited to ad-supported publishing. It avoids wasting time on custom CMS work and allows the project to focus on content operations rather than platform construction.

### Facebook Groups deferred

Groups are deferred because they introduce extra operational and policy complexity. They may become useful later for reach expansion, but they are not necessary to prove the core traffic loop.

### Paid boosts deferred

Paid boosts are deferred because the project first needs organic validation. Spending money before understanding which topics, sources, titles, and hooks work would add cost before the system has learned anything reliable.

### Scheduled queue with human approval

A scheduled queue with human approval is the right v1 mode because it keeps control in the operator's hands while still enabling throughput. It also prevents low-quality automation from slipping straight into public channels.

### Practical role of the blog

The blog is:

1. the destination for traffic,
2. the place where content is formatted properly,
3. the monetization layer,
4. the content archive,
5. the eventual data source for winner analysis.

## 10. Source Strategy

Source selection is the highest-leverage part of the project.

If the source layer is weak, the content layer becomes thin, the packaging layer becomes forced, and the monetization layer becomes unstable. The first serious implementation priority is therefore not AI orchestration or distribution automation. It is a reliable and discriminating source system.

### Source registry

The source registry is the controlled list of approved intake sources for the system.

Each source registry entry should eventually support metadata such as:

1. source ID,
2. source name,
3. domain,
4. source family,
5. RSS feed URLs if available,
6. fallback extraction method,
7. topical fit,
8. estimated freshness cadence,
9. extraction notes,
10. trust or quality notes,
11. active or inactive status.

The registry is essential because it keeps sourcing deliberate. It prevents the project from drifting into random scraping.

### Source metadata

Source metadata should support both operations and later evaluation. At minimum, the system should be able to record enough information to answer:

1. where the content came from,
2. what type of source it was,
3. how it was fetched,
4. when it was last checked,
5. whether it tends to produce usable items.

### Source quality standards

Good sources for v1 should have most of the following:

1. stable structure,
2. clear factual or explanatory content,
3. broad-interest relevance to food facts,
4. manageable extraction complexity,
5. low boilerplate noise,
6. usable freshness cadence,
7. reasonable trustworthiness for informational reuse.

Weak sources include those that are highly noisy, overly sensational, structurally inconsistent, or too dependent on aggressive health-style claims.

### Source freshness considerations

Freshness matters, but freshness alone is not enough.

For this project, freshness should be treated as one factor among several:

1. some content benefits from recency,
2. some food facts are evergreen,
3. some source families may perform well repeatedly even if not strictly news-like.

The system should therefore support both fresh content intake and reuse of evergreen structures where appropriate.

### Source diversification

Source diversification is important because single-source dependence is dangerous.

Single-source dependence creates several problems:

1. extraction fragility if the source changes structure,
2. content sameness,
3. limited topic range,
4. business fragility if a single source becomes unavailable,
5. weak long-term learning because source comparison becomes impossible.

The project should be designed to compare source families over time, even if v1 starts with a small curated list.

### Why RSS-first is preferred for v1

RSS-first is preferred because it is cheap, structured, and operationally simple. It reduces complexity at intake time and supports predictable fetching behavior. It also aligns with the principle that deterministic systems should come before complex automation.

### Where scraping fits

Scraping is secondary and selective in v1.

It should be used when:

1. a valuable source has no usable RSS,
2. the feed exists but does not contain enough structured content,
3. the article body requires extraction from page HTML.

Scraping should not become the default intake model early because it is more fragile, more maintenance-heavy, and more likely to create operational noise.

### Why "finding viral content" should not be framed as magic prediction

The system should not assume it can predict virality in advance with high confidence. Instead, it should treat source and topic performance as a scoring and repeated-testing problem.

The correct framing is:

1. source good candidates,
2. package consistently,
3. test repeatedly,
4. record outcomes,
5. learn which patterns win.

### Future source scoring ideas

Later scoring can consider:

1. source reliability,
2. topic fit,
3. title pattern fit,
4. freshness,
5. prior performance of similar content,
6. source family performance,
7. extraction cleanliness,
8. downstream publish success rate.

These are future decision-layer features, not v1 prerequisites.

## 11. Workflow States and Data Flow

Each content item should move through explicit workflow states. The state model is important because it keeps the system auditable and predictable.

Suggested lifecycle states:

1. **sourced**: item retrieved from a registered source.
2. **cleaned**: raw extraction normalized and noise removed.
3. **classified**: item assigned a likely template category or content type.
4. **deduped**: item checked against prior items and marked unique or duplicate-like.
5. **drafted**: blog draft generated through template formatting and limited AI enhancement.
6. **reviewed**: draft checked by human or quality layer for acceptance.
7. **queued**: accepted for scheduled publishing.
8. **published**: live on WordPress.
9. **socially_packaged**: Facebook assets created and mapped.
10. **mapped to Facebook post**: blog post connected to one or more Facebook posts.
11. **archived or promoted**: retained as normal historical content or elevated later for scaling.

### End-to-end flow

The intended end-to-end flow is:

1. source registry defines where content may come from,
2. fetcher retrieves new items,
3. cleaner normalizes raw text,
4. classifier assigns a likely content type,
5. deduper prevents repetitive output,
6. content engine formats the item into a blog draft,
7. quality checks verify structure and readability,
8. human review approves or rejects,
9. approved items enter the publish queue,
10. WordPress publisher posts the article,
11. Social Packaging Engine creates Facebook variants,
12. Distribution Engine maps and schedules Facebook assets,
13. publish history records the source-to-blog-to-Facebook relationship,
14. later tracking uses those records to identify winners.

This lifecycle should be preserved even if implementation details change.

## 12. Tracking and Data Strategy

V1 tracking should be intentionally limited but structurally useful.

### What needs to be stored in v1

At minimum, the system should store:

1. source ID,
2. source URL or source item reference,
3. normalized source title,
4. title used for the blog post,
5. selected template category,
6. assigned category or tags,
7. draft and publish timestamps,
8. blog post ID,
9. Facebook post ID,
10. variant identifier where relevant,
11. queue state,
12. mapping between source item, blog post, and Facebook output.

This is enough to support operational history and later analysis without overbuilding analytics too early.

### What deeper tracking can come later

Later phases may add:

1. click counts,
2. CTR,
3. source family performance,
4. hook performance,
5. winner detection,
6. promotion candidate scoring,
7. content-type performance,
8. timing and schedule effects.

### Design principle for tracking

V1 should not try to become a full analytics platform. It should capture enough identifiers and relationships that deeper analysis becomes possible later. The schema should be forward-compatible even if the first implementation is simple.

## 13. Constraints and Risks

### Business constraints

1. the system must remain affordable for a solo operator,
2. maintainability matters more than feature breadth,
3. the first niche is intentionally narrow,
4. the business depends on repeatable traffic, not one-off standout posts,
5. overbuilding too early would consume time without improving revenue.

### Technical risks

1. source extraction may be brittle,
2. poorly defined states may create publishing confusion,
3. weak deduplication may create repetitive output,
4. weak template discipline may produce inconsistent content,
5. publishing integrations may fail or drift,
6. the system may become too coupled if engines are not kept separate.

### Monetization risks

1. low-value content can weaken ad monetization viability,
2. clickbait without useful landing content can produce poor monetization outcomes,
3. ad revenue may remain low if traffic quality is weak,
4. overreliance on one traffic source can reduce business resilience,
5. high volume without quality may hurt long-term monetization opportunities.

### Platform/policy risks

1. spammy Facebook packaging can limit reach or create account risk,
2. misleading titles or exaggerated claims can hurt trust and performance,
3. health-adjacent overclaiming is risky and should be avoided,
4. low-value or thinly transformed content can create platform and monetization issues,
5. excessive automation without review can produce policy-fragile behavior.

This section is practical risk framing, not legal advice.

## 14. What Must Be Avoided

The following are project-killing or project-distorting mistakes and must be actively avoided:

1. full AI article generation for v1,
2. starting with agents or OpenClaw before the deterministic pipeline exists,
3. skipping templates,
4. treating source strategy as a secondary concern,
5. trying to build Page, Groups, paid ads, analytics, and agents all at once,
6. building around one source only,
7. optimizing before tracking exists,
8. treating Facebook packaging as an afterthought,
9. building a custom blog platform now,
10. going multilingual too early,
11. replacing structured workflows with giant prompts,
12. confusing automation quantity with business quality.

If future work starts violating these rules, the project is drifting away from its core operating logic.

## 15. Role of OpenClaw and agency-agents

### OpenClaw

OpenClaw is not needed for the first working version.

Its likely future role, if adopted later, is in reasoning-heavy orchestration such as:

1. decision-layer analysis,
2. winner selection,
3. source prioritization,
4. multi-step workflow coordination across engines.

It should not be treated as a phase-1 dependency, a foundation requirement, or the center of the architecture. The project must work without it first.

### agency-agents

agency-agents is not the architecture. It is a possible future role library.

Later adaptation candidates may include roles such as:

1. planner,
2. writer,
3. reviewer,
4. analyst,
5. social packager.

Even then, those roles should sit on top of a working deterministic system. They are future enhancement candidates, not a v1 dependency.

This section exists to make it difficult for future development to accidentally center the architecture around OpenClaw or agent orchestration too early.

## 16. Important Assumptions

The project currently assumes:

1. Facebook-driven traffic comes first,
2. English-only is sufficient for v1,
3. food facts are the first niche,
4. WordPress is the first blog platform,
5. v1 includes human approval before publishing,
6. low-cost operation matters materially,
7. a later intelligence layer is desirable but not urgent,
8. phased building is acceptable,
9. RSS-first sourcing is feasible for enough useful sources,
10. a solo operator can manage the initial review workflow.

These assumptions should remain visible during implementation and should only be changed deliberately.

## 17. Missing Information / Open Questions

The following unknowns still matter, but they do not justify expanding scope prematurely:

1. the exact first source domains,
2. the exact post frequency targets for blog and Facebook,
3. the exact WordPress theme and plugin choices,
4. the exact approval workflow interface beyond the current operator API plus WordPress-admin review shell baseline,
5. the exact Facebook publishing mechanics to adopt,
6. the exact title and tag taxonomy for the first niche,
7. the exact threshold for source acceptance or retirement.

These should be resolved during implementation planning for the relevant phase, not by turning phase 0 into endless design.

## 18. Component Map

The concrete v1 component map should include at least the following:

### source registry

Stores approved source definitions and metadata.

### fetcher

Retrieves candidate source items from RSS or selective scraping targets.

### cleaner

Normalizes extracted content and removes noise.

### classifier

Assigns likely content type or template family.

### deduper

Checks source items and drafts for repetition or near-duplication.

### template library

Stores the fixed blog, Facebook, and comment CTA templates that define output structure.

### formatting engine

Fills templates using cleaned source content and deterministic rules.

### AI skill layer

Provides small, controlled transformations such as titles, intros, hooks, and short rewrites.

### quality checks

Runs structure, readability, derivative-risk, and mobile-format checks.

### draft health reporter

Summarizes the latest draft and review state so the operator can see which drafts are blocked, pending review, revision-required, rejected, or ready for later handoff.

### WordPress publisher

Publishes approved blog content to WordPress and records resulting IDs.

### Facebook packaging layer

Generates Facebook-ready post variants and comment CTAs from the approved blog draft.

### queue/state manager

Tracks workflow states, review transitions, and scheduled publishing order.

### publish history

Stores the source-to-blog-to-Facebook record chain for later analysis.

### logs

Captures fetch, processing, publishing, and failure events for basic system observability.

## 19. Phased Roadmap

The phased roadmap is not only a build order. It is also a control system. A phase should not be treated as complete when code merely exists. It should only be treated as complete when its outputs, validation baseline, operator workflow, documentation updates, residual risks, and next-phase handoff are all explicit.

Each phase transition should leave behind:

1. a closeout review,
2. a next-phase entry checklist,
3. an updated execution checklist,
4. an updated open-questions list,
5. a current validation baseline.

### Phase 0: Foundation and Planning

**Objective**

Define the architecture, workflow states, template strategy, and implementation boundaries before coding.

**Deliverables**

1. authoritative master plan,
2. component boundaries,
3. workflow state model,
4. first template definitions,
5. implementation order and guardrails.

**Intentionally out of scope**

1. application code,
2. scaffolding,
3. tooling installation,
4. premature analytics systems,
5. orchestration layers.

### Phase 1: Source Engine

**Objective**

Build the source intake foundation that can produce usable, normalized candidate items.

**Deliverables**

1. curated source registry,
2. RSS-first fetching workflow,
3. selective scraping support where needed,
4. cleaner,
5. classifier,
6. dedupe baseline,
7. source audit trail.

**Intentionally out of scope**

1. autonomous publishing,
2. advanced AI reasoning,
3. paid amplification logic,
4. broad internet crawling.

### Phase 2: Content Engine

**Objective**

Turn normalized source items into structured blog drafts through templates and small enhancement skills.

**Deliverables**

1. template library for blog content,
2. formatting engine,
3. light AI skill layer,
4. quality checks,
5. review-ready draft output.

**Intentionally out of scope**

1. full AI article writing,
2. advanced social scheduling,
3. winner optimization logic,
4. multi-channel content expansion.

### Phase 3: Social Packaging + Distribution

**Objective**

Publish approved content to WordPress and derive Facebook Page assets from the approved blog content.

**Deliverables**

1. WordPress publishing path,
2. Facebook packaging templates,
3. hook and CTA generation skills,
4. scheduled queue,
5. human approval workflow,
6. blog-to-Facebook mapping records.

**Intentionally out of scope**

1. Facebook Groups rollout,
2. paid boosting,
3. deep analytics,
4. multi-platform expansion.

### Phase 4: Tracking Foundation

**Objective**

Create a minimal but durable data layer for publication records and future performance analysis.

**Deliverables**

1. publish history,
2. source-to-blog-to-Facebook mapping,
3. variant references,
4. basic reporting-ready records,
5. state and publish logs.

**Intentionally out of scope**

1. full BI dashboards,
2. predictive modeling,
3. advanced winner automation,
4. complex attribution systems.

### Phase 4.5: System Activation And Live Validation

**Objective**

Prove that the system can run as a real operator workflow with live local config, credential validation, and one controlled canary chain.

**Deliverables**

1. local secrets and transport-config policy,
2. execute-mode transport validation evidence,
3. one canary chain through the connected system,
4. operator activation runbook,
5. explicit acceptance evidence before more complexity is added.

**Intentionally out of scope**

1. new decision logic,
2. new channels,
3. broad automation,
4. full production launch assumptions.

### Phase 4.6: AI-Assisted Content Quality

**Objective**

Improve bounded text quality only after the connected system is proven to work.

**Deliverables**

1. optional provider-backed micro-skill architecture,
2. provider-secret handling policy,
3. prompt and output contracts for bounded skills,
4. deterministic fallback behavior,
5. review-safe quality improvements for selected text fields.

**Intentionally out of scope**

1. full AI article generation,
2. replacing the template layer,
3. making external AI a required dependency.

### Phase 4.7: Media And Asset Layer

**Objective**

Add the missing visual/media baseline for blog and Facebook outputs after the connected text system is stable.

**Deliverables**

1. media and visual-asset policy,
2. asset review workflow,
3. media record and linkage model,
4. first blog/Facebook asset handling baseline,
5. operator-usable visual workflow.

**Intentionally out of scope**

1. broad creative automation,
2. casual image scraping,
3. video-first production,
4. design-system expansion for its own sake.

### Phase 4.8: Runtime Operations And Deployment

**Objective**

Define the boring, repeatable production operating model so the system can run reliably after build without depending on ad hoc local execution.

**Deliverables**

1. runtime operating model,
2. deployment and scheduling policy,
3. backup and recovery policy,
4. daily and weekly operator runbook,
5. explicit recommendation for the first production host and scheduler.

**Intentionally out of scope**

1. cluster orchestration,
2. multi-region availability,
3. custom control panels,
4. infrastructure complexity that a solo operator does not need.

### Phase 4.9: Approval UI And Operator Console

**Objective**

Give human approval a stable operator-facing console before later scoring and autoapproval work begin.

**Deliverables**

1. internal operator API,
2. WordPress admin review plugin,
3. approval UI runbook,
4. approval-console validation baseline,
5. explicit disabled fast-lane placeholders for later phases.

**Intentionally out of scope**

1. full editorial CMS behavior,
2. mirrored workflow storage in WordPress,
3. autoapproval,
4. transport shortcuts that bypass the audited repo runtime.

### Phase 5: Decision Layer

**Objective**

Use accumulated data to improve source selection, template choice, and packaging decisions.

**Deliverables**

1. basic winner detection logic,
2. source scoring,
3. hook and template pattern comparison,
4. candidate promotion lists,
5. optional reasoning-layer experiments if justified.

**Intentionally out of scope**

1. making OpenClaw mandatory,
2. large multi-agent orchestration,
3. fully autonomous business decisions.

### Phase 5.5: Approval Automation And Autopilot

**Objective**

Move from advisory scoring to narrow, explainable automation of approvals only after the system has enough evidence to trust that move.

**Deliverables**

1. explicit autoapproval policy,
2. shadow-mode approval scoring,
3. narrow eligibility lanes for automatic approval,
4. rollback and kill-switch rules,
5. approval audit and override records.

**Intentionally out of scope**

1. broad fully autonomous publishing,
2. automatic approval for all content families,
3. hidden model-based decisions with no explanation,
4. removing the operator override path.

### Phase 6: Scaling Layer

**Objective**

Scale what has already been proven to work.

**Deliverables**

1. promotion candidate workflows,
2. selective paid amplification decisions,
3. possible source expansion,
4. possible channel expansion,
5. possible later-stage reasoning orchestration where data justifies it.

**Intentionally out of scope**

1. uncontrolled platform expansion,
2. multilingual expansion by default,
3. replacing the source-first architecture,
4. abandoning human oversight too early.

## 20. Final Guidance for Future Development

Future development should follow these rules:

1. respect the phased build order,
2. do not overbuild early,
3. preserve template-based content production,
4. preserve the source-first architecture,
5. keep AI tightly scoped,
6. treat Facebook packaging as core business infrastructure,
7. treat OpenClaw as a later optimization layer,
8. optimize for maintainability, clarity, and low operating cost,
9. prefer deterministic systems before orchestration,
10. change locked v1 decisions only with explicit justification,
11. do not close a phase until configuration readiness, operational readiness, and handoff readiness are documented clearly,
12. do not begin Decision Layer work until the runtime operating model is explicit enough that the finished system could be run by one person without guesswork,
13. do not introduce autoapproval until scoring, shadow-mode evidence, and rollback rules are explicit.

When there is uncertainty, the correct default is to simplify and preserve the operating logic of the business:

1. good sources,
2. clean formatting,
3. strong packaging,
4. disciplined publishing,
5. useful tracking,
6. later intelligence.

If future work starts drifting toward general AI experimentation, architecture sprawl, or broad platform expansion before the core loop works, it should be considered out of alignment with this plan.
