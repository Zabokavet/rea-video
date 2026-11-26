import importlib.util
import os
import wave

import pytest

from story_narrator.kreyol import expand_numbers, number_to_words
from story_narrator.local_mms import fold_for_model


@pytest.mark.parametrize("n,words", [
    (1, "en"), (12, "douz"), (21, "venteyen"), (25, "vennsenk"), (28, "ventuit"), (70, "swasanndis"),
    (71, "swasanteonz"), (80, "katreven"), (95, "katrevenkenz"), (100, "san"), (250, "de san senkant"),
    (1804, "mil uit san kat"), (2026, "de mil vennsis"), (1_000_000, "en milyon"),
])
def test_numbers_in_creole(n, words):
    assert number_to_words(n) == words


def test_expand_numbers_in_text():
    assert expand_numbers("3 ti kochon, 25 goud, 50% ak 1,000 pye bwa; 2,5 kilo.") == \
        "twa ti kochon, vennsenk goud, senkant pousan ak mil pye bwa; de pwen senk kilo."


def test_fold_keeps_creole_letters_and_maps_others():
    vocab = set(" '-abcdefghijklmnoprstuvwyzàèò")
    assert fold_for_model("Bonjou! Lanmè a bèl, m’ap rete. Café Ç", vocab) == "bonjou lanmè a bèl m'ap rete cafe s"


needs_mms = pytest.mark.skipif(
    not (importlib.util.find_spec("torch") and importlib.util.find_spec("transformers")) or os.environ.get("NARRATOR_SKIP_MODEL_TESTS"),
    reason="optional [kreyol] dependencies not installed")


@needs_mms
def test_real_creole_voice_speaks(tmp_path):
    from conftest import settings
    from story_narrator.local_mms import MMSProvider
    out = MMSProvider(settings(tmp_path)).synthesize("Bonjou zanmi m. Te gen 3 ti kochon.", "default", "", True, "ht")
    assert out.kind == "pcm" and out.sample_rate == 16000
    seconds = len(out.data) / 2 / out.sample_rate
    assert 2 < seconds < 10
