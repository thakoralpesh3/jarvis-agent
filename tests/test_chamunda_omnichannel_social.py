"""
Automated Test Suite for Chamunda Automobile 360° Omnichannel Social & Business Media Engine.
Validates automated management across:
- WhatsApp (24/7 AI Bot +91 78747 19139, wa.me/917874719139)
- Instagram (@chamunda_automobile_re, Reels & Post Studio)
- Facebook (Page Feed, RE Club Community)
- Google Business Profile (4.9★ Local SEO & Review AI Auto-Responder)
- YouTube (@ChamundaAutomobileRE, Shorts Pipeline & SEO Metadata)
"""

import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

RE_DIR = Path("/home/alpesh/chamunda_re_enterprise")
JARVIS_DIR = Path("/home/alpesh/jarvis-agent")

if str(RE_DIR) not in sys.path:
    sys.path.insert(0, str(RE_DIR))
if str(JARVIS_DIR) not in sys.path:
    sys.path.insert(0, str(JARVIS_DIR))

from omnichannel_social_engine import (
    ChamundaOmnichannelSocialEngine,
    WHATSAPP_OFFICIAL_NUMBER,
    WHATSAPP_CHAT_LINK
)
from marketing_engine import ChamundaMarketingEngine
from tools.chamunda_ceo_tools import (
    chamunda_get_social_telemetry,
    chamunda_generate_social_campaign,
    chamunda_publish_social_post,
    chamunda_manage_social_inbox,
    chamunda_manage_google_business_reviews
)
from app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_channels_initialization():
    """Verify all 5 channels are configured with accurate metadata."""
    engine = ChamundaOmnichannelSocialEngine()
    channels = engine.get_channels_info()
    channel_ids = [c["id"] for c in channels]

    assert "whatsapp" in channel_ids
    assert "instagram" in channel_ids
    assert "facebook" in channel_ids
    assert "google_business" in channel_ids
    assert "youtube" in channel_ids

    wa = next(c for c in channels if c["id"] == "whatsapp")
    assert wa["handle"] == "+91 78747 19139"
    assert wa["url"] == "https://wa.me/917874719139"

    ig = next(c for c in channels if c["id"] == "instagram")
    assert ig["handle"] == "@chamunda_automobile_re"

    gbp = next(c for c in channels if c["id"] == "google_business")
    assert "4.9" in gbp["subscribers"]


def test_channel_telemetry():
    """Verify aggregated telemetry and metrics."""
    engine = ChamundaOmnichannelSocialEngine()
    telem = engine.get_channel_telemetry()
    assert telem["channels_count"] == 5
    assert telem["active_whatsapp_bot"] == "+91 78747 19139"
    assert telem["whatsapp_chat_link"] == "https://wa.me/917874719139"
    assert "4.9" in telem["google_review_score"]
    assert telem["status"] == "ALL_SYSTEMS_OPERATIONAL"


def test_generate_multi_platform_campaign():
    """Verify single topic generates native copies for all 5 platforms."""
    engine = ChamundaOmnichannelSocialEngine()
    camp = engine.generate_multi_platform_campaign(
        topic="Classic 350 Cold Start Tappet Noise Fix",
        campaign_type="Workshop Master Tip"
    )
    assert camp["topic"] == "Classic 350 Cold Start Tappet Noise Fix"
    ch = camp["channels_data"]

    # WhatsApp
    assert "+91 78747 19139" in ch["whatsapp"]["content"]
    assert "https://wa.me/917874719139" in ch["whatsapp"]["content"]

    # Instagram
    assert "#RoyalEnfield" in ch["instagram"]["hashtags"]
    assert "Classic 350" in ch["instagram"]["caption"]

    # Facebook
    assert "Chamunda Automobile" in ch["facebook"]["content"]

    # Google Business Profile
    assert "Ahmedabad" in ch["google_business"]["content"]
    assert "4.9 Star Rated" in ch["google_business"]["content"]

    # YouTube
    assert "Classic 350" in ch["youtube"]["title"]
    assert len(ch["youtube"]["tags"]) > 0
    assert "https://wa.me/917874719139" in ch["youtube"]["pinned_comment"]


def test_publish_to_channels():
    """Verify publishing to designated channels records post history."""
    engine = ChamundaOmnichannelSocialEngine()
    camp = engine.generate_multi_platform_campaign(topic="Monsoon 48-Point Waterproofing")
    res = engine.publish_to_channels(
        campaign_data=camp,
        target_channels=["whatsapp", "instagram", "google_business"]
    )
    assert res["success"] is True
    assert "POST-" in res["post_id"]
    assert len(res["published_channels"]) == 3

    history = engine.get_posts_history()
    assert any(p["post_id"] == res["post_id"] for p in history)


def test_social_inbox_and_reply():
    """Verify reading and replying to incoming messages."""
    engine = ChamundaOmnichannelSocialEngine()
    inbox = engine.get_social_inbox()
    assert len(inbox) > 0

    first_item = inbox[0]
    reply_res = engine.reply_to_inbox_item(
        item_id=first_item["item_id"],
        reply_text="Thank you for contacting Chamunda Automobile! Visit wa.me/917874719139."
    )
    assert reply_res["success"] is True

    filtered_ig = engine.get_social_inbox(filter_channel="instagram")
    assert all(it["channel"] == "instagram" for it in filtered_ig)


def test_google_reviews_and_reply():
    """Verify reading and replying to Google Business reviews."""
    engine = ChamundaOmnichannelSocialEngine()
    reviews = engine.get_google_reviews()
    assert len(reviews) > 0

    first_rev = reviews[0]
    reply_res = engine.reply_to_google_review(
        review_id=first_rev["review_id"],
        reply_text="Thank you for visiting Chamunda Automobile! - Alpesh Sir & Team"
    )
    assert reply_res["success"] is True


def test_marketing_engine_bridge():
    """Verify ChamundaMarketingEngine integration with social engine."""
    mkt = ChamundaMarketingEngine()
    res = mkt.launch_omnichannel_campaign(topic="Hunter 350 Throttle Smoothing")
    assert "campaign" in res
    assert "publication" in res
    assert res["publication"]["success"] is True


def test_ceo_social_tools():
    """Verify CEO tools for Aradhya AI agent."""
    telem_out = chamunda_get_social_telemetry()
    assert "360° Omnichannel Social" in telem_out
    assert "+91 78747 19139" in telem_out

    camp_out = chamunda_generate_social_campaign(topic="Classic 350 Thump Tuning")
    assert "WhatsApp Broadcast Copy" in camp_out
    assert "Instagram Reels" in camp_out
    assert "Google Business Profile" in camp_out
    assert "YouTube Video" in camp_out

    pub_out = chamunda_publish_social_post(topic="Classic 350 Thump Tuning")
    assert "Campaign Dispatched" in pub_out

    inbox_out = chamunda_manage_social_inbox()
    assert "Unified Social Inbox" in inbox_out

    rev_out = chamunda_manage_google_business_reviews()
    assert "Google Business Profile (4.9★)" in rev_out


def test_api_social_endpoints(client):
    """Verify all REST API endpoints for social management."""
    # 1. Telemetry
    r = client.get("/api/social/telemetry")
    assert r.status_code == 200
    assert r.json()["status"] == "ALL_SYSTEMS_OPERATIONAL"

    # 2. Channels
    r = client.get("/api/social/channels")
    assert r.status_code == 200
    assert len(r.json()) == 5

    # 3. Campaign Generate
    r = client.post("/api/social/campaign/generate", json={
        "topic": "Himalayan 450 Pre-Trip Check",
        "campaign_type": "Service Awareness"
    })
    assert r.status_code == 200
    data = r.json()
    assert "channels_data" in data
    assert "+91 78747 19139" in data["channels_data"]["whatsapp"]["content"]

    # 4. Publish
    r = client.post("/api/social/publish", json={
        "topic": "Himalayan 450 Pre-Trip Check",
        "campaign_type": "Service Awareness",
        "channels": ["whatsapp", "instagram"]
    })
    assert r.status_code == 200
    assert r.json()["success"] is True

    # 5. Inbox
    r = client.get("/api/social/inbox")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    # 6. Inbox Reply
    r = client.post("/api/social/inbox/reply", json={
        "item_id": "INB-WA-001",
        "reply_text": "Confirmed via REST API"
    })
    assert r.status_code == 200

    # 7. Reviews
    r = client.get("/api/social/reviews")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    # 8. Reviews Reply
    r = client.post("/api/social/reviews/reply", json={
        "review_id": "REV-GBP-001",
        "reply_text": "Thank you via API! - Alpesh Sir"
    })
    assert r.status_code == 200

    # 9. Calendar
    r = client.get("/api/social/calendar")
    assert r.status_code == 200

    # 10. Dashboard HTML Tab 11
    r = client.get("/")
    assert r.status_code == 200
    assert 'id="omnichannel-social"' in r.text
    assert "WhatsApp Business" in r.text
    assert "@chamunda_automobile_re" in r.text
    assert "fb.com/chamundaautomobile" in r.text
