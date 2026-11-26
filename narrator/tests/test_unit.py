from story_narrator.chunking import split_text
from story_narrator.filenames import content_disposition, download_name, title_stem


def test_split_keeps_every_character_and_respects_limit():
    text = ("The keeper climbed the stairs. " * 40 + "\n\n" + "风很大。灯塔还亮着！" * 30 +
            "\n\n" + "x" * 950)
    chunks = split_text(text, 200)
    assert all(len(c) <= 200 for c in chunks)
    squash = lambda s: "".join(s.split())
    assert squash("".join(chunks)) == squash(text)


def test_split_prefers_sentence_boundaries():
    chunks = split_text("One two three. Four five six. Seven eight nine.", 30)
    assert chunks == ["One two three. Four five six.", "Seven eight nine."]


def test_short_text_is_one_chunk_and_empty_is_none():
    assert split_text("  Hello there.  ", 4000) == ["Hello there."]
    assert split_text("   \n ", 10) == []


def test_filenames_are_descriptive_and_safe():
    assert title_stem("The Lighthouse Keeper: Part 2 / Draft?") == "The-Lighthouse-Keeper-Part-2-Draft"
    assert title_stem("   ") == "narration"
    assert title_stem("灯塔守护人") == "灯塔守护人"
    assert download_name("My Story", "2026-11-26T14:05:00+00:00", "mp3") == "My-Story_2026-11-26_1405.mp3"
    h = content_disposition("灯塔守护人_2026-11-26_1405.mp3")
    assert h.startswith('attachment; filename="narration_2026-11-26_1405.mp3"')
    assert "filename*=UTF-8''%E7%81%AF" in h
    assert content_disposition("a.wav", attachment=False).startswith("inline;")
