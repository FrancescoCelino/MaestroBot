"""
Usage example
-------------
```bash
python app/process_telegram_export.py \
       --input gozomaxxing_json/result.json \
       --output dataset.jsonl \
       --author-id user357010412 \
       --idle-cutoff-min 30 \
       --keep-newlines --debug
```

su powershell
python app\\process_telegram_export.py `
  --input gozomaxxing_json\\result.json `
  --output dataset.jsonl `
  --author-id user357010412 `
  --idle-cutoff-min 30 `
  --keep-newlines `
  --debug
"""

import argparse # used to parse command line arguments
import json
import logging # used for debug prints
import re # regular expressions
import html # decodes HTML entities
from collections import Counter 
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse # used to get the domain from an URL

# Matches http:// or https:// plus everything until a space or closing paren
url_regex = re.compile(r"https?://[^\s)\"]+", re.IGNORECASE)
# any kind of blank space (space, tab, newline and so on)
whitespace_regex = re.compile(r"\s+", re.MULTILINE)
# Matches a single space or tab, but not newlines
inline_whitespace_regex = re.compile(r"[ \t\x0b\f\r]+")

def parse_cli_arguments(): 
    ap = argparse.ArgumentParser(description="Telegram → JSONL exporter")
    # mandatory arguments
    ap.add_argument("--input", required=True, help="Telegram chat export in .json format")
    ap.add_argument("--output", required=True, help="Output file in .jsonl format")
    ap.add_argument("--author-id", required=True, help="filter messages according to 'from_id' filter")

    # Optional arguments (if not specified in the CLI keep the same default as before)

    ap.add_argument("--top-domains",  type=int, default=50,
                    help="How many frequent domains get their own <URL:domain> token")
    ap.add_argument("--thread-cap",   type=int, default=6,
                    help="Max hops walked up in a reply‑to chain")
    ap.add_argument("--window-size",  type=int, default=3,
                    help="Fallback rolling window size if no explicit reply context")
    ap.add_argument("--min-tokens",   type=int, default=4,
                    help="Drop completions shorter than this many tokens")
    ap.add_argument("--max-tokens",   type=int, default=256,
                    help="Drop completions longer than this many tokens")
    ap.add_argument("--time-gap-hours", type=int, default=6,
                    help="Ignore parent if older than this gap (in hours)")
    ap.add_argument("--keep-newlines", action="store_true",
                    help="Preserve original newlines inside messages")
    ap.add_argument("--idle-cutoff-min", type=int, default=0,
                    help="If >0, treat a non‑reply message as standalone when the previous "
                         "message is older than this many minutes.")

    # debug
    ap.add_argument("--debug", action="store_true",
                    help="Print verbose debugging information")
    return ap.parse_args()

def read_exported_chat_json(path: Path) -> dict: 
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def entity_to_text(entity):
    """
    flattens telegram 'text' field. If it's already a string, leave as-is
    """
    if isinstance(entity, str):
        return entity
    return "".join(part.get("text", str(part)) if isinstance(part, dict) else str(part)
                   for part in entity)

def normalize_one_message(text: str, domain_tokens: Dict[str, str], *, keep_newlines: bool=False) -> str: 

    if not text:
        return "" # so far, we can't deal with empty, non-text messages
    
    text = html.unescape(text) # e.g. "&amp;" → "&"

    def replace_url_with_domain_tokens(match): # URLs need to be converted in something simpler, for NLP tasks
        url = match.group(0)
        domain = urlparse(url).netloc.lower()
        return domain_tokens.get(domain, "<URL:OTHER>")

    text = url_regex.sub(replace_url_with_domain_tokens, text)

    if keep_newlines: 
        text = text.replace("\r\n", "\n")
        text = inline_whitespace_regex.sub(" ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
    else:
        text = whitespace_regex.sub(" ", text)
    return text.strip()

def collect_domains_and_their_frequency(messages) -> Counter:
    """
    returns a counter mapping from domain to num of occurrences
    """
    ctr = Counter()
    for m in messages:
        txt = entity_to_text(m.get("text", ""))
        for url in url_regex.findall(txt):
            ctr[urlparse(url).netloc.lower()] += 1
    return ctr

def is_parent_message_recent_enough(parent_ts: str, child_ts: str, max_gap_hours: int) -> bool: 
    """True if (child - parent) ≤ max_gap_hours. If parsing fails, keep the parent message just to be sure."""
    try: 
        p = datetime.fromisoformat(parent_ts.replace("Z", ""))
        c = datetime.fromisoformat(child_ts.replace("Z", ""))
        return ( c - p ) <= timedelta(hours=max_gap_hours)
    except Exception: 
        print(f"Exception when parsing {child_ts} and its parent {parent_ts}")
        return True
    
# TODO: any smarter way to tokenize each message?
def tokenize_length(text: str) -> int:
    return len(text.split()) 



def main():
    args = parse_cli_arguments()
    # determines level of debugging detail to be printed according to the --debug flag
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format="%(levelname)s: %(message)s")
    
    data = read_exported_chat_json(Path(args.input))
    messages = data.get("messages", [])

    message_by_id = {m["id"]: m for m in messages}
    index_by_id = {m["id"]: idx for idx, m in enumerate(messages)} # id → list index

    domain_freq = collect_domains_and_their_frequency(messages).most_common(args.top_domains)
    domain_tokens = {d: f"<URL:{d}>" for d, _ in domain_freq}

    prompt_response_pairs: List[dict] = [] 
    already_processed_ids: set = set() # so we don’t visit self‑reply msgs twice

    idle_delta = timedelta(minutes=args.idle_cutoff_min) if args.idle_cutoff_min else None

    for m in messages: 
        if m.get("from_id") != args.author_id: 
            continue
        if m["id"] in already_processed_ids: 
            continue

        ### self-reply chains ###
        self_chain = []
        cur = m
        while cur and cur.get("from_id") == args.author_id: 
            self_chain.append(cur)  # Corretto 'appen' in 'append'
            already_processed_ids.add(cur["id"]) 
            parent_id = cur.get("reply_to_message_id")
            parent = message_by_id.get(parent_id) if parent_id else None
            cur = parent if (parent and parent.get("from_id") == args.author_id) else None
        self_chain.reverse() # reverses order so that oldest message is first
        
        ### completion text ###
        completion_pieces = [
            normalize_one_message(entity_to_text(s.get("text", "")),
                    domain_tokens,
                    keep_newlines=args.keep_newlines)
            for s in self_chain
        ]
        completion = "\n".join(filter(None, completion_pieces)).strip()

        if not completion:
            logging.debug("Skipped msg %s — empty completion after cleansing", m["id"])
            continue
        if not (args.min_tokens <= tokenize_length(completion) <= args.max_tokens):
            logging.debug("Skipped msg %s — completion length outside [%s,%s]", m["id"],
                          args.min_tokens, args.max_tokens)
            continue

        ### prompt text ###
        root = self_chain[0]
        prompt_parts: List[str] = []
        
        # Inizializza context_type in base alla presenza di reply_to_message_id
        if root.get("reply_to_message_id"):
            context_type = "reply"
        else:
            context_type = "none"  # Messaggio standalone di default se non è una risposta
            logging.debug("Msg %s is not a reply, marking as standalone initially", root["id"])

        parent_id = root.get("reply_to_message_id")
        hops = 0
        while parent_id and hops < args.thread_cap: 
            parent = message_by_id.get(parent_id)
            if not parent: 
                break
            if not is_parent_message_recent_enough(parent.get("date"), root.get("date"), args.time_gap_hours): 
                break
            prompt_text = normalize_one_message(entity_to_text(parent.get("text", "")),
                                                domain_tokens,
                                                keep_newlines=args.keep_newlines)
            if prompt_text and parent.get("from_id") != args.author_id: 
                prompt_parts.append(prompt_text)
            parent_id = parent.get("reply_to_message_id")
            hops += 1
        prompt_parts.reverse()

        # if the response is not explicitly quoting another message, use a rolling window as context
        if not prompt_parts:
            idx  = index_by_id[root["id"]] - 1
            back = 0
            while idx >= 0 and back < args.window_size:
                prev = messages[idx]
                idx -= 1
                if prev.get("from_id") == args.author_id:
                    continue  # don't include your own previous lines # TODO: try to understand if this strategy is correct
                prompt_text = normalize_one_message(entity_to_text(prev.get("text", "")),
                                domain_tokens,
                                keep_newlines=args.keep_newlines)
                if prompt_text:
                    prompt_parts.append(prompt_text)
                    back += 1
            prompt_parts.reverse()
            
            # Se abbiamo trovato prompt_parts usando la finestra mobile, 
            # questo non è più un messaggio standalone
            if prompt_parts:
                context_type = "window"  # Un nuovo tipo per chiarire che stiamo usando context window
            
            if idle_delta and prompt_parts:
                try:
                    last_prev_ts = datetime.fromisoformat(messages[idx + 1]["date"].replace("Z", ""))
                    root_ts      = datetime.fromisoformat(root["date"].replace("Z", ""))
                    if root_ts - last_prev_ts >= idle_delta: # variando idle_delta, discriminiamo i messaggi "stand-alone" da quelli che rispondono a qualcun altro
                        prompt_parts = []  # treat as stand‑alone
                        context_type = "none"
                        logging.debug("Msg %s marked standalone (idle gap)", root["id"])
                except Exception:
                    pass  # be lenient if date parsing fails

        prompt = "\n".join(prompt_parts).strip()

        if (not prompt or prompt == completion) and context_type != "none":
            logging.debug("Skipped msg %s — prompt empty or identical to completion", m["id"])
            continue

        prompt_response_pairs.append({
            "prompt": prompt,
            "completion": completion,
            "standalone": context_type == "none"
        })

    with Path(args.output).open("w", encoding="utf-8") as fout:
        for pair in prompt_response_pairs:
            json.dump(pair, fout, ensure_ascii=False)
            fout.write("\n")

    logging.info("✅ Wrote %s pairs → %s", len(prompt_response_pairs), args.output)
    logging.info("Top domain tokens (first 10):")
    for d in list(domain_tokens)[:10]:
        logging.info("  %s → %s", d, domain_tokens[d])
    if len(domain_tokens) < args.top_domains:
        logging.info("(Only %s unique domains found.)", len(domain_tokens))




if __name__ == "__main__":
    main()