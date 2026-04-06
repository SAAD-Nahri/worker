# Active Source Registry Records V1

## Purpose

This file contains the day-one active source registry in a copy-ready record format aligned with the source registry spec.

It exists to reduce ambiguity when the registry is moved into the application.

## Record Format

Each record follows the v1 source registry fields defined in:

[SOURCE_REGISTRY_SPEC.md](C:/Users/Administrator/OneDrive/Documents/co_ma/docs/specs/SOURCE_REGISTRY_SPEC.md)

## Records

```yaml
- source_id: src_tasting_table
  source_name: Tasting Table
  domain: tastingtable.com
  source_family: food_editorial
  source_type: rss_plus_fetch
  primary_topic_fit: broad food curiosity, ingredient explainers, food culture
  active: true
  priority_level: tier_1
  rss_feed_url: https://www.tastingtable.com/feed/
  fetch_method: rss_discovery_plus_article_fetch
  body_extraction_required: true
  freshness_pattern: daily
  quality_notes: strong curiosity fit and useful range for Facebook-friendly food angles
  risk_notes: may drift into trend-heavy or glossy content that needs filtering

- source_id: src_food_republic
  source_name: Food Republic
  domain: foodrepublic.com
  source_family: food_editorial
  source_type: rss_plus_fetch
  primary_topic_fit: food culture, ingredient explainers, transformation-friendly editorial content
  active: true
  priority_level: tier_1
  rss_feed_url: https://www.foodrepublic.com/feed/
  fetch_method: rss_discovery_plus_article_fetch
  body_extraction_required: true
  freshness_pattern: daily
  quality_notes: strong mix of food knowledge and curiosity-friendly material
  risk_notes: quality consistency varies by item

- source_id: src_curious_cuisiniere
  source_name: Curious Cuisiniere
  domain: curiouscuisiniere.com
  source_family: ingredient_reference
  source_type: rss_plus_fetch
  primary_topic_fit: ingredient origins, cultural food explanations, structured factual content
  active: true
  priority_level: tier_1
  rss_feed_url: https://www.curiouscuisiniere.com/feed/
  fetch_method: rss_discovery_plus_article_fetch
  body_extraction_required: true
  freshness_pattern: irregular_to_weekly
  quality_notes: high-signal source for ingredient and origin-style content
  risk_notes: lower content volume than large editorial sites

- source_id: src_saveur
  source_name: Saveur
  domain: saveur.com
  source_family: food_editorial
  source_type: rss_plus_fetch
  primary_topic_fit: food history, food culture, high-trust explanatory food content
  active: true
  priority_level: tier_2
  rss_feed_url: https://www.saveur.com/feed/
  fetch_method: rss_discovery_plus_article_fetch
  body_extraction_required: true
  freshness_pattern: weekly
  quality_notes: good source for deeper background and culturally grounded food content
  risk_notes: some pieces may be too long-form or less direct for the first Facebook-driven batch

- source_id: src_bon_appetit
  source_name: Bon Appetit
  domain: bonappetit.com
  source_family: food_editorial
  source_type: rss_plus_fetch
  primary_topic_fit: selective food explainers and high-trust editorial food content
  active: true
  priority_level: tier_2
  rss_feed_url: https://www.bonappetit.com/feed/rss
  fetch_method: rss_discovery_plus_article_fetch
  body_extraction_required: true
  freshness_pattern: daily
  quality_notes: strong editorial brand and selective trust-building source
  risk_notes: recipe-heavy feed mix requires strict filtering

- source_id: src_mashed
  source_name: Mashed
  domain: mashed.com
  source_family: curiosity_editorial
  source_type: rss_plus_fetch
  primary_topic_fit: curiosity-driven food angles and click-oriented consumer-interest topics
  active: true
  priority_level: tier_3
  rss_feed_url: https://www.mashed.com/feed/
  fetch_method: rss_discovery_plus_article_fetch
  body_extraction_required: true
  freshness_pattern: daily
  quality_notes: useful for testing strong hook potential against more editorial sources
  risk_notes: higher low-value and sensational-risk profile; should remain selective
```

## Usage Rule

When the application source registry is first created, these records should be used as the initial import set unless there is a documented reason to change them.
