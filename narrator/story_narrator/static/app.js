"use strict";
const $ = (id) => document.getElementById(id);
const api = async (path, opts = {}) => {
  const r = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts });
  if (r.status === 204) return null;
  const body = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail || body));
  return body;
};
const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* private mode: ignore */ } },
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

/* ---------- providers & form ---------- */
let providers = [];
async function loadStatus() {
  const s = await api("/api/status");
  providers = s.providers;
  const msgs = [];
  if (!providers.length) msgs.push("No AI voice provider is configured. Add OPENAI_API_KEY or ELEVENLABS_API_KEY to the server's .env file and restart.");
  if (!s.ffmpeg) msgs.push("ffmpeg is not installed on the server; it is required to export MP3.");
  $("banner").hidden = !msgs.length;
  $("banner").textContent = msgs.join(" ");
  $("gen-btn").disabled = !providers.length || !s.ffmpeg;
  $("provider").innerHTML = providers.map((p) => `<option value="${p.id}">${p.label}</option>`).join("");
  const saved = store.get("provider");
  if (providers.some((p) => p.id === saved)) $("provider").value = saved;
  await onProviderChange();
}
async function onProviderChange() {
  const p = providers.find((x) => x.id === $("provider").value);
  $("model").innerHTML = "";
  $("voice-list").innerHTML = "";
  if (!p) return;
  store.set("provider", p.id);
  $("model").innerHTML = p.models.map((m) => `<option>${m}</option>`).join("");
  $("model").value = p.default_model;
  updateTextMeta();
  const v = await api(`/api/providers/${p.id}/voices`).catch((e) => ({ voices: [], error: e.message }));
  const dl = $("voice-list");
  for (const voice of v.voices) {
    const o = document.createElement("option");
    o.value = voice.id;
    o.label = voice.name;
    dl.appendChild(o);
  }
  const savedVoice = store.get(`voice:${p.id}`);
  $("voice").value = v.voices.some((x) => x.id === savedVoice) || (savedVoice && !v.voices.length) ? savedVoice
    : (v.voices[0] ? v.voices[0].id : "");
  $("voice").placeholder = v.error ? "Couldn't list voices; paste a voice ID" : "Choose or paste a voice ID";
}
function updateTextMeta() {
  const n = $("text").value.length;
  const p = providers.find((x) => x.id === $("provider").value);
  const parts = p ? Math.max(1, Math.ceil(n / p.chunk_chars)) : 1;
  $("text-meta").textContent = `${n.toLocaleString()} characters` +
    (n > (p ? p.chunk_chars : Infinity) ? ` · long story: about ${parts} parts, joined into one file` : "");
}

/* ---------- generation ---------- */
let currentJob = null;
async function onGenerate(ev) {
  ev.preventDefault();
  const body = {
    title: $("title").value.trim(), text: $("text").value,
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
  $("job").hidden = false;
  $("job-title").textContent = n.title;
  const labels = { queued: "Waiting for a free worker…", generating: `Generating part ${Math.min(n.chunks_done + 1, n.chunks_total || 1)} of ${n.chunks_total || "?"}…`, ready: "Done", failed: "Failed" };
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
      const wasReady = $("job-status").textContent === "Done";
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
  for (const n of items) {
    const li = $("item-tpl").content.firstElementChild.cloneNode(true);
    li.dataset.id = n.id;
    li.classList.toggle("playing", player.current && player.current.id === n.id);
    li.querySelector(".item-title").textContent = n.title;
    const when = new Date(n.created_at).toLocaleString();
    const state = n.status === "ready" ? (n.duration ? fmtTime(n.duration) : "")
      : n.status === "generating" ? `generating ${n.chunks_done}/${n.chunks_total}` : n.status;
    li.querySelector(".item-meta").textContent = [when, state, `${n.provider} · ${n.voice}`,
      n.has_wav ? "MP3 + WAV" : n.has_mp3 ? "MP3" : ""].filter(Boolean).join(" · ");
    li.querySelector(".item-excerpt").textContent = n.excerpt;
    const err = li.querySelector(".item-error");
    err.hidden = n.status !== "failed";
    err.textContent = n.error || "";
    const ready = n.status === "ready";
    li.querySelector(".item-play").disabled = !ready;
    li.querySelector(".item-play").onclick = () => player.load(n, true);
    setLink(li.querySelector(".item-mp3"), ready && n.has_mp3 && audioUrl(n, "mp3", true));
    const wav = li.querySelector(".item-wav");
    setLink(wav, ready && n.has_wav && audioUrl(n, "wav", true));
    wav.title = n.has_wav ? "" : "WAV isn't available for this narration";
    const retry = li.querySelector(".item-retry");
    retry.hidden = n.status !== "failed";
    retry.onclick = async () => {
      await api(`/api/narrations/${n.id}/retry`, { method: "POST" }).catch((e) => alert(e.message));
      schedulePoll();
    };
    li.querySelector(".item-delete").onclick = async () => {
      if (!confirm(`Delete “${n.title}” from your library? The audio files are removed too.`)) return;
      await api(`/api/narrations/${n.id}`, { method: "DELETE" }).catch((e) => alert(e.message));
      if (player.current && player.current.id === n.id) player.close();
      if (currentJob === n.id) { currentJob = null; $("job").hidden = true; }
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
    const label = !a.paused ? "Pause" : a.ended ? "Play again" : a.currentTime > 0 ? "Resume" : "Play";
    $("p-toggle").textContent = label;
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
$("provider").addEventListener("change", onProviderChange);
$("text").addEventListener("input", updateTextMeta);
let searchTimer;
$("search").addEventListener("input", () => { clearTimeout(searchTimer); searchTimer = setTimeout(refreshLibrary, 250); });
loadStatus().catch((e) => { $("banner").hidden = false; $("banner").textContent = `Couldn't reach the server: ${e.message}`; });
refreshLibrary().then((pending) => pending && schedulePoll()).catch(() => {});
