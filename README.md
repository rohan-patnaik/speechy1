# speechy1

Headless English dictation for Linux: hold **Ctrl+Super**, speak, release, and insert cleaned text into the focused field.

**Groq Whisper Large V3 → Qwen3.8 27B**, with reasoning disabled for cleanup latency. Runs on demand, with no local model downloads and no persistent speechy1 daemon. MIT licensed.

## Setup

Requirements: Python 3.10+, PipeWire (`pw-record`), `wl-clipboard`, and a Wayland desktop. The included shortcut/paste adapter is tested on **Omarchy with Lua Hyprland 0.56.2**. Other desktops need their own global shortcut and paste adapter; they are not yet verified.

```sh
git clone https://github.com/rohan-patnaik/speechy1.git
cd speechy1
sh install.sh
~/.local/bin/speechy1 setup
```

Create your own API key in [Groq Console](https://console.groq.com/keys). Keep the account on **Free**; no paid plan or card is needed for that tier. Setup asks for the key privately and stores it in `~/.config/speechy1/api-key` with mode 0600. Each user supplies their own key; there is no shared proxy/account cycling.

For Omarchy's Lua Hyprland, copy `hyprland-omarchy.lua` to `~/.config/hypr/speechy1.lua`, add this line to `~/.config/hypr/bindings.lua`, and run `hyprctl reload` followed by `hyprctl configerrors`:

```lua
dofile(os.getenv("HOME") .. "/.config/hypr/speechy1.lua")
```

Stop/disable another app using the same chord first. No app autostart is needed: the compositor shortcut launches a worker for each take. Hold Ctrl and either Super key in either order. Release either to stop capture; insertion waits until both modifiers are released. Maximum take length is three minutes.

```sh
speechy1 doctor        # local prerequisite/configuration check
speechy1 start         # manual capture; speechy1 stop ends it
speechy1 cancel        # discard an active take
speechy1 stats         # numeric UTC-day counters, no transcripts
```

## Cleanup and dictionary

The pipeline does all three: simple whitespace/punctuation normalization, exact alias replacement, and optional-style LLM formatting (enabled by default). Qwen removes filler/false starts, applies spoken self-corrections, and uses paragraphs or lists when appropriate. It edits dictation instead of answering it. As with any generative cleanup, verify important names/numbers before sending.

Edit the private `~/.config/speechy1/config.json`:

```json
{
  "asr_model": "whisper-large-v3",
  "cleanup_model": "qwen/qwen3.8-27b",
  "aliases": {"omarchi": "Omarchy Linux"},
  "preferred_words": ["Omarchy", "Hyprland"],
  "snippets": {"my signature": "Your verbatim signature"},
  "paste_command": null
}
```

Aliases match whole phrases, ignoring case, with longest match first. They do not cascade or duplicate canonical phrases. Snippets use protected placeholders through cleanup and expand verbatim afterwards. Preferred words are sent as Whisper vocabulary hints; they cannot guarantee recognition.

For another desktop, `paste_command` can be an argument array for an installed paste tool. Automatic focus guarding currently uses Hyprland; outside it, completed text goes to the clipboard. No shell string execution is used. Cloud model IDs are editable, so upgrades need no rebuild. They stay pinned until you select and test a replacement; there is no automatic upgrade or paid fallback.

## Free-tier capacity

Checked 13 October 2026 against [Groq's published Free limits](https://console.groq.com/docs/rate-limits) and authenticated response headers:

| Model | Requests/min | Requests/day | Other ceilings |
| --- | ---: | ---: | --- |
| Whisper Large V3 | 20 | 2,000 | 120 audio min/hour; 480 min/day; Free upload 25 MB |
| Qwen3.8 27B | 30 | 1,000 | 8,000 tokens/min; 200,000 tokens/day |

Short ASR requests have a ten-second minimum billable duration. Local audio counters conservatively reflect that minimum. Account quotas can be shared with other apps and changed by Groq; a UTC-day local counter is not the provider's rolling quota/reset clock. Rate-limit headers retain the last successful response's remaining values, not live balances.

At 150 spoken words/minute the raw audio ceiling is about **72,000 words/day**. Cleanup generally limits first. A conservative planning allowance is **20,000–30,000 words/day for roughly 50-word takes**; very short takes can hit the 1,000-request cap much earlier. Prompt length, tokenizer, output formatting and minute/hour bursts matter. The initial public 25-word sample used 192 cleanup tokens, implying roughly 35,000–40,000 words/day at 50-word takes if similar overhead holds; this is an estimate, not an entitlement.

The app stops on 429, never upgrades billing, and has local daily safety ceilings. Only your Groq account's Free status guarantees no paid requests; app settings cannot verify/override future account billing changes. Keep the account Free. Cloud/internet availability is required.

## Privacy and resources

- Audio and working text stay in memory locally; no recordings, transcript history or text logs are written. Audio goes to Groq for ASR and text goes to Groq for cleanup, so this is **not an offline/private-local inference app**. Review [Groq's data policy](https://console.groq.com/docs/your-data) and account data controls.
- Only numeric counters, stage/error labels and rate-limit headers persist. Credentials and personal vocabulary stay outside the repo. Text remains in the destination and system clipboard; desktop clipboard history, cloud retention, swapping and crash dumps are outside this app's guarantees.
- No persistent Python worker at idle. A clipboard owner can remain while the desktop needs its selection, plus the existing compositor/bar. Recording measured about **26 MB worker + 9 MB PipeWire client** on the initial machine; processing memory grows with take length. Three-minute mono 16 kHz PCM is 5.76 MB. No GPU inference or local model storage.
- Existing Python/PipeWire/clipboard/compositor dependencies are shared system software. No new Python packages are installed. Source/installation sizes and timings are recorded in the local verification report.
- If focus moves to another window while processing, text is copied and a notification asks you to paste. Same-window caret changes are not detected. Supported ordinary text fields insert via Ctrl+V; known terminal classes use Shift+Insert. Secure fields or apps that block clipboard injection may require manual paste.

## Compared with alternatives

| | speechy1 | Handy | Inlay | Wispr Flow |
| --- | --- | --- | --- | --- |
| Tested desktop here | Omarchy/Lua Hyprland | Linux app available | Native macOS client; Linux inference server | User's adapted Linux runtime |
| Inference | Groq cloud + cloud | Primarily local STT; configurable post-processing | Local defaults | Cloud service |
| Idle approach | No dictation daemon/models | App/model unload settings matter | Depends on client/server setup | Background app |
| Exact aliases/snippets | Configurable, deterministic | Check current dictionary/post-processing behavior | Custom development may be needed | User dictionary |
| Offline dictation | No | Yes with local models | Local setup | No |
| Accuracy/speed verdict | Needs your speech trials | Needs same audio/model test | Needs same audio/model test | Needs same audio test |

This project is inspired by the dictation workflows of [Handy](https://github.com/cjpais/Handy) and Inlay. It is a new small Linux client, **not a Handy fork or a port of Inlay's Swift client**. No claim of beating them or Wispr on accuracy is based on the single smoke test.

## Basic verification

```sh
python3 -B -m unittest discover -s tests -v
```

Tests cover alias canonicalization and protected snippet failure behavior. Initial machine checks also exercised both Ctrl/Super orders, real PipeWire capture/cancel, authenticated ASR+cleanup on a public speech fixture, and insertion into a disposable Chrome field. One 11-second sample completed the two cloud calls in 0.55 seconds; this is a smoke measurement, not a general latency benchmark.
