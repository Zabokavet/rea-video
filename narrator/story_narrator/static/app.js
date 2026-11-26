"use strict";
const $ = (id) => document.getElementById(id);
const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* private mode: ignore */ } },
};

/* ---------- interface text: Kreyòl first, English second ---------- */
const STRINGS = {
  ht: {
    appTitle: "Rakontè Istwa",
    subtitle: "Kole yon istwa, chwazi yon vwa, epi koute l oswa telechaje l. Ou pa bezwen anrejistre vwa pa w: se yon vwa entèlijans atifisyèl (AI) ki li chak istwa.",
    newNarration: "Nouvo narasyon", storyTitle: "Tit istwa a", storyText: "Tèks istwa a",
    titlePlaceholder: "Ti Malis ak Bouki", textPlaceholder: "Te gen yon fwa…",
    language: "Lang narasyon an", provider: "Founisè vwa", voice: "Vwa", model: "Modèl",
    voicePlaceholder: "Chwazi oswa kole ID yon vwa", voiceListError: "Nou pa t ka jwenn lis vwa yo; kole ID vwa a",
    generate: "Kreye narasyon an", ready: "Narasyon an pare", preview: "▶ Koute l",
    downloadMp3: "⬇ Telechaje odyo a (MP3)", downloadWav: "⬇ Telechaje WAV",
    wavUnavailable: "WAV pa disponib ak founisè sa a oswa plan sa a",
    library: "Bibliyotèk odyo", search: "Chèche nan tit ak tèks",
    libraryEmpty: "Narasyon ou kreye yo ap parèt la a.",
    nowPlaying: "Kounye a:", player: "Jwè odyo", replay: "Rekòmanse depi nan kòmansman",
    back10: "Retounen 10 segonn", fwd10: "Avanse 10 segonn", seek: "Pozisyon", speed: "Vitès",
    play: "Jwe", pause: "Poz", resume: "Kontinye", playAgain: "Rejwe",
    playItem: "▶ Jwe", retry: "Eseye ankò", del: "Efase",
    chars: (n) => `${n} karaktè`,
    longStory: (n) => `istwa long: anviwon ${n} pati, ki pral mete ansanm nan yon sèl fichye`,
    queued: "Ap tann tou pa l…", generating: (a, b) => `Ap kreye pati ${a} sou ${b}…`,
    done: "Fini", failed: "Pa mache", genShort: (a, b) => `ap kreye ${a}/${b}`,
    native: "vwa natif", prompted: "kreyòl pa garanti",
    noProvider: "Pa gen okenn founisè vwa ki pare. Enstale vwa kreyòl lokal la (pip install -e '.[kreyol]') oswa mete OPENAI_API_KEY / ELEVENLABS_API_KEY nan fichye .env la, epi rekòmanse sèvè a.",
    noFfmpeg: "ffmpeg pa enstale sou sèvè a; li nesesè pou fè MP3.",
    noVoiceForLang: "Pa gen founisè ki gen vwa pou lang sa a.",
    serverDown: "Nou pa ka kontakte sèvè a:",
    confirmDelete: (t) => `Efase “${t}” nan bibliyotèk ou? Fichye odyo yo ap efase tou.`,
    wavMissing: "WAV pa disponib pou narasyon sa a",
    mmsNote: "Vwa sa a fèt pou kreyòl ayisyen. Li travay sou òdinatè w: li gratis, san limit. Premye fwa a, l ap telechaje modèl la (anviwon 145 MB).",
    promptedNote: "Vwa sa a pale plizyè lang. Li ka li kreyòl ak yon aksan etranje; koute l anvan ou pataje l.",
  },
  en: {
    appTitle: "Story Narrator",
    subtitle: "Paste a story, pick a voice, then listen or download. No recording needed: an AI voice reads every narration.",
    newNarration: "New narration", storyTitle: "Story title", storyText: "Story text",
    titlePlaceholder: "Ti Malis and Bouki", textPlaceholder: "Te gen yon fwa…",
    language: "Narration language", provider: "Voice provider", voice: "Voice", model: "Model",
    voicePlaceholder: "Choose or paste a voice ID", voiceListError: "Couldn't list voices; paste a voice ID",
    generate: "Generate narration", ready: "Narration ready", preview: "▶ Preview",
    downloadMp3: "⬇ Download Audio (MP3)", downloadWav: "⬇ Download WAV",
    wavUnavailable: "WAV isn’t available from this provider or plan",
    library: "Audio library", search: "Search titles and text",
    libraryEmpty: "Your generated narrations will appear here.",
    nowPlaying: "Now playing:", player: "Audio player", replay: "Replay from the start",
    back10: "Back 10 seconds", fwd10: "Forward 10 seconds", seek: "Seek", speed: "Speed",
    play: "Play", pause: "Pause", resume: "Resume", playAgain: "Play again",
    playItem: "▶ Play", retry: "Retry", del: "Delete",
    chars: (n) => `${n} characters`,
    longStory: (n) => `long story: about ${n} parts, joined into one file`,
    queued: "Waiting for a free worker…", generating: (a, b) => `Generating part ${a} of ${b}…`,
    done: "Done", failed: "Failed", genShort: (a, b) => `generating ${a}/${b}`,
    native: "native voice", prompted: "Creole not guaranteed",
    noProvider: "No voice provider is ready. Install the local Creole voice (pip install -e '.[kreyol]') or add OPENAI_API_KEY / ELEVENLABS_API_KEY to the .env file, then restart the server.",
    noFfmpeg: "ffmpeg is not installed on the server; it is required to export MP3.",
    noVoiceForLang: "No provider has a voice for this language.",
    serverDown: "Couldn't reach the server:",
    confirmDelete: (t) => `Delete “${t}” from your library? The audio files are removed too.`,
    wavMissing: "WAV isn't available for this narration",
    mmsNote: "This voice was trained on Haitian Creole. It runs on your computer: free and unlimited. The first use downloads the model (about 145 MB).",
    promptedNote: "This is a multilingual voice. It may read Creole with a foreign accent; listen before you share.",
  },
};
let uiLang = store.get("uiLang") || "ht";
const T = (key, ...args) => {
  const v = (STRINGS[uiLang] || STRINGS.ht)[key] ?? STRINGS.ht[key];
  return typeof v === "function" ? v(...args) : v;
};
function applyUiLang() {
  document.documentElement.lang = uiLang;
  document.title = T("appTitle");
  document.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = T(el.dataset.i18n); });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => { el.placeholder = T(el.dataset.i18nPlaceholder); });
  document.querySelectorAll("[data-i18n-aria]").forEach((el) => el.setAttribute("aria-label", T(el.dataset.i18nAria)));
  document.querySelectorAll("[data-i18n-title]").forEach((el) => { el.title = T(el.dataset.i18nTitle); });
  document.querySelectorAll("[data-ui-lang]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.uiLang === uiLang)));
  if (status) { renderBanner(); renderProviders(false); }
  updateTextMeta();
  renderLibrary();
  if (lastJob) renderJob(lastJob);
  player.sync();
}

const api = async (path, opts = {}) => {
  const r = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts });
  if (r.status === 204) return null;
  const body = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail || body));
  return body;
};
const fmtTime = (s) => {
  if (!isFinite(s)) return "0:00";
  s = Math.floor(s);
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = String(s % 60).padStart(2, "0");
  return h ? `${h}:${String(m).padStart(2, "0")}:${sec}` : `${m}:${sec}`;
};
const audioUrl = (n, ext, download) => `/api/narrations/${n.id}/audio.${ext}${download ? "?download=1" : ""}`;
const setLink = (a, href) => {
  if (href) { a.href = href; a.removeAttribute("aria-disabled"); a.tabIndex = 0; }
  else { a.removeAttribute("href"); a.setAttribute("aria-disabled", "true"); a.tabIndex = -1; }
};
const option = (value, text) => { const o = document.createElement("option"); o.value = value; o.textContent = text; return o; };

/* ---------- languages, providers & form ---------- */
let status = null;
async function loadStatus() {
  status = await api("/api/status");
  const sel = $("language");
  sel.innerHTML = "";
  for (const l of status.languages) sel.appendChild(option(l.code, l.name === l.english ? l.name : `${l.name} (${l.english})`));
  const savedLang = store.get("language");
  sel.value = status.languages.some((l) => l.code === savedLang) ? savedLang : status.default_language;
  renderBanner();
  await renderProviders(true);
}
function renderBanner() {
  const msgs = [];
  if (!status.providers.length) msgs.push(T("noProvider"));
  if (!status.ffmpeg) msgs.push(T("noFfmpeg"));
  $("banner").hidden = !msgs.length;
  $("banner").textContent = msgs.join(" ");
}
// Providers that can speak the chosen language, native voices first.
function providersFor(lang) {
  return status.providers.filter((p) => p.languages[lang])
    .sort((a, b) => (a.languages[lang] === "native" ? 0 : 1) - (b.languages[lang] === "native" ? 0 : 1));
}
async function renderProviders(reloadVoices) {
  const lang = $("language").value;
  const list = providersFor(lang);
  const sel = $("provider");
  const prev = sel.value || store.get(`provider:${lang}`);
  sel.innerHTML = "";
  for (const p of list) {
    const kind = p.languages[lang];
    sel.appendChild(option(p.id, `${p.label} — ${kind === "native" ? T("native") : (lang === "ht" ? T("prompted") : "AI")}`));
  }
  if (list.some((p) => p.id === prev)) sel.value = prev;
  $("gen-btn").disabled = !list.length || !status.ffmpeg;
  if (status.providers.length && !list.length) { $("banner").hidden = false; $("banner").textContent = T("noVoiceForLang"); }
  if (reloadVoices || sel.value !== prev) await onProviderChange();
  else renderProviderNote();
}
function renderProviderNote() {
  const p = status.providers.find((x) => x.id === $("provider").value);
  const kind = p && p.languages[$("language").value];
  $("provider-note").textContent = !p ? "" : p.id === "mms" ? T("mmsNote") : kind === "prompted" && $("language").value === "ht" ? T("promptedNote") : "";
}
async function onProviderChange() {
  const p = status.providers.find((x) => x.id === $("provider").value);
  $("model").innerHTML = "";
  $("voice-list").innerHTML = "";
  renderProviderNote();
  if (!p) { $("voice").value = ""; return; }
  store.set(`provider:${$("language").value}`, p.id);
  for (const m of p.models) $("model").appendChild(option(m, m));
  $("model").value = p.default_model;
  $("model").closest("label").hidden = p.models.length < 2;
  updateTextMeta();
  const v = await api(`/api/providers/${p.id}/voices`).catch((e) => ({ voices: [], error: e.message }));
  for (const voice of v.voices) { const o = option(voice.id, ""); o.label = voice.name; $("voice-list").appendChild(o); }
  const savedVoice = store.get(`voice:${p.id}`);
  $("voice").value = v.voices.some((x) => x.id === savedVoice) || (savedVoice && !v.voices.length) ? savedVoice
    : (v.voices[0] ? v.voices[0].id : "");
  $("voice").placeholder = v.error ? T("voiceListError") : T("voicePlaceholder");
}
function updateTextMeta() {
  const n = $("text").value.length;
  const p = status && status.providers.find((x) => x.id === $("provider").value);
  const parts = p ? Math.max(1, Math.ceil(n / p.chunk_chars)) : 1;
  $("text-meta").textContent = T("chars", n.toLocaleString()) + (p && n > p.chunk_chars ? ` · ${T("longStory", parts)}` : "");
}

/* ---------- generation ---------- */
let currentJob = null, lastJob = null;
async function onGenerate(ev) {
  ev.preventDefault();
  const body = {
    title: $("title").value.trim(), text: $("text").value, language: $("language").value,
    provider: $("provider").value, voice: $("voice").value.trim(), model: $("model").value,
  };
  store.set(`voice:${body.provider}`, body.voice);
  $("gen-btn").disabled = true;
  try {
    const rec = await api("/api/narrations", { method: "POST", body: JSON.stringify(body) });
    currentJob = rec.id;
    renderJob(rec);
    schedulePoll();
  } catch (e) {
    $("job").hidden = false;
    $("job-error").hidden = false;
    $("job-error").textContent = e.message;
  } finally {
    $("gen-btn").disabled = false;
  }
}
function renderJob(n) {
  lastJob = n;
  $("job").hidden = false;
  $("job-title").textContent = n.title;
  const labels = { queued: T("queued"), generating: T("generating", Math.min(n.chunks_done + 1, n.chunks_total || 1), n.chunks_total || "?"), ready: T("done"), failed: T("failed") };
  $("job-status").textContent = labels[n.status] || n.status;
  const prog = $("job-progress");
  prog.hidden = n.status === "ready" || n.status === "failed";
  prog.max = n.chunks_total || 1;
  prog.value = n.chunks_done;
  $("job-error").hidden = n.status !== "failed";
  $("job-error").textContent = n.error || "";
  $("job-result").hidden = n.status !== "ready";
  if (n.status === "ready") {
    $("job-duration").textContent = n.duration ? `(${fmtTime(n.duration)})` : "";
    setLink($("job-mp3"), n.has_mp3 && audioUrl(n, "mp3", true));
    setLink($("job-wav"), n.has_wav && audioUrl(n, "wav", true));
    $("job-wav").hidden = !n.has_wav;
    $("job-wav-note").hidden = n.has_wav;
    $("job-preview").onclick = () => player.load(n, true);
  }
}

/* ---------- library ---------- */
let items = [];
let pollTimer = null;
async function refreshLibrary() {
  const q = $("search").value.trim();
  const data = await api(`/api/narrations${q ? `?q=${encodeURIComponent(q)}` : ""}`);
  items = data.narrations;
  renderLibrary();
  if (currentJob) {
    const job = items.find((n) => n.id === currentJob) || await api(`/api/narrations/${currentJob}`).catch(() => null);
    if (job) {
      const wasReady = lastJob && lastJob.id === job.id && lastJob.status === "ready";
      renderJob(job);
      if (job.status === "ready" && !wasReady) player.load(job, false); // ready to preview, no autoplay
    }
  }
  return items.some((n) => n.status === "queued" || n.status === "generating");
}
function renderLibrary() {
  const ul = $("library");
  ul.innerHTML = "";
  $("library-empty").hidden = items.length > 0;
  const langName = (code) => ((status && status.languages.find((l) => l.code === code)) || { name: code }).name;
  for (const n of items) {
    const li = $("item-tpl").content.firstElementChild.cloneNode(true);
    li.dataset.id = n.id;
    li.classList.toggle("playing", Boolean(player.current && player.current.id === n.id));
    li.querySelector(".item-title").textContent = n.title;
    const when = new Date(n.created_at).toLocaleString(uiLang === "ht" ? "fr-HT" : undefined);
    const state = n.status === "ready" ? (n.duration ? fmtTime(n.duration) : "")
      : n.status === "generating" ? T("genShort", n.chunks_done, n.chunks_total)
      : n.status === "queued" ? T("queued") : T("failed");
    li.querySelector(".item-meta").textContent = [when, state, langName(n.language), `${n.provider} · ${n.voice}`,
      n.has_wav ? "MP3 + WAV" : n.has_mp3 ? "MP3" : ""].filter(Boolean).join(" · ");
    li.querySelector(".item-excerpt").textContent = n.excerpt;
    const err = li.querySelector(".item-error");
    err.hidden = n.status !== "failed";
    err.textContent = n.error || "";
    const ready = n.status === "ready";
    const play = li.querySelector(".item-play");
    play.textContent = T("playItem");
    play.disabled = !ready;
    play.onclick = () => player.load(n, true);
    setLink(li.querySelector(".item-mp3"), ready && n.has_mp3 && audioUrl(n, "mp3", true));
    const wav = li.querySelector(".item-wav");
    setLink(wav, ready && n.has_wav && audioUrl(n, "wav", true));
    wav.title = n.has_wav ? "" : T("wavMissing");
    const retry = li.querySelector(".item-retry");
    retry.textContent = T("retry");
    retry.hidden = n.status !== "failed";
    retry.onclick = async () => {
      await api(`/api/narrations/${n.id}/retry`, { method: "POST" }).catch((e) => alert(e.message));
      schedulePoll();
    };
    const del = li.querySelector(".item-delete");
    del.textContent = T("del");
    del.onclick = async () => {
      if (!confirm(T("confirmDelete", n.title))) return;
      await api(`/api/narrations/${n.id}`, { method: "DELETE" }).catch((e) => alert(e.message));
      if (player.current && player.current.id === n.id) player.close();
      if (currentJob === n.id) { currentJob = null; lastJob = null; $("job").hidden = true; }
      refreshLibrary();
    };
    ul.appendChild(li);
  }
}
function schedulePoll() {
  clearTimeout(pollTimer);
  pollTimer = setTimeout(async () => {
    const pending = await refreshLibrary().catch(() => true);
    if (pending) schedulePoll();
  }, 1500);
}

/* ---------- player ---------- */
const player = {
  el: $("audio"),
  current: null,
  load(n, autoplay) {
    this.current = n;
    $("player").hidden = false;
    $("np-title").textContent = n.title;
    setLink($("p-mp3"), n.has_mp3 && audioUrl(n, "mp3", true));
    setLink($("p-wav"), n.has_wav && audioUrl(n, "wav", true));
    $("p-wav").hidden = !n.has_wav;
    // Play the lossless master when there is one; the MP3 otherwise.
    this.el.src = audioUrl(n, n.has_wav ? "wav" : "mp3", false);
    this.applySpeed();
    this.sync();
    if (autoplay) this.el.play().catch(() => {});
    document.querySelectorAll(".item").forEach((li) => li.classList.toggle("playing", li.dataset.id === n.id));
  },
  close() { this.el.pause(); this.el.removeAttribute("src"); this.el.load(); this.current = null; $("player").hidden = true; },
  applySpeed() {
    const rate = parseFloat($("p-speed").value) || 1;
    this.el.defaultPlaybackRate = rate;
    this.el.playbackRate = rate;
    this.el.preservesPitch = true;
  },
  toggle() {
    if (this.el.paused) { if (this.el.ended) this.el.currentTime = 0; this.el.play().catch(() => {}); }
    else this.el.pause();
  },
  sync() {
    const a = this.el;
    $("p-toggle").textContent = !a.paused ? T("pause") : a.ended ? T("playAgain") : a.currentTime > 0 ? T("resume") : T("play");
    $("p-seek").max = isFinite(a.duration) ? a.duration : 0;
    if (!this.seeking) $("p-seek").value = a.currentTime;
    $("p-time").textContent = `${fmtTime(a.currentTime)} / ${fmtTime(a.duration)}`;
  },
};
["play", "pause", "ended", "timeupdate", "loadedmetadata", "durationchange"].forEach((e) => player.el.addEventListener(e, () => player.sync()));
$("p-toggle").onclick = () => player.toggle();
$("p-replay").onclick = () => { player.el.currentTime = 0; player.el.play().catch(() => {}); };
$("p-back").onclick = () => { player.el.currentTime = Math.max(0, player.el.currentTime - 10); };
$("p-fwd").onclick = () => { player.el.currentTime = Math.min(player.el.duration || 0, player.el.currentTime + 10); };
$("p-seek").addEventListener("input", () => { player.seeking = true; $("p-time").textContent = `${fmtTime(+$("p-seek").value)} / ${fmtTime(player.el.duration)}`; });
$("p-seek").addEventListener("change", () => { player.el.currentTime = +$("p-seek").value; player.seeking = false; });
$("p-speed").value = store.get("speed") || "1";
$("p-speed").onchange = () => { store.set("speed", $("p-speed").value); player.applySpeed(); };
document.addEventListener("keydown", (e) => {
  if (e.code === "Space" && !$("player").hidden && !e.target.closest("input, textarea, select, button, a")) {
    e.preventDefault();
    player.toggle();
  }
});

/* ---------- boot ---------- */
$("gen-form").addEventListener("submit", onGenerate);
$("language").addEventListener("change", () => { store.set("language", $("language").value); renderProviders(true); });
$("provider").addEventListener("change", onProviderChange);
$("text").addEventListener("input", updateTextMeta);
document.querySelectorAll("[data-ui-lang]").forEach((b) => b.addEventListener("click", () => {
  uiLang = b.dataset.uiLang;
  store.set("uiLang", uiLang);
  applyUiLang();
}));
let searchTimer;
$("search").addEventListener("input", () => { clearTimeout(searchTimer); searchTimer = setTimeout(refreshLibrary, 250); });
applyUiLang();
loadStatus().catch((e) => { $("banner").hidden = false; $("banner").textContent = `${T("serverDown")} ${e.message}`; });
refreshLibrary().then((pending) => pending && schedulePoll()).catch(() => {});
