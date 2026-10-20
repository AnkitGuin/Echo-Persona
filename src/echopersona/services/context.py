"""Bounded, deterministic language-style observations; no personality inference."""
import json
import re

MAX_CONTEXT_CHARS = 100_000

def extract_context(payload: str, kind: str='manual') -> str:
    if len(payload) > MAX_CONTEXT_CHARS: raise ValueError('Context is too large (100,000 character limit).')
    if kind in {'manual','txt'}: value=payload
    elif kind=='json':
        try: raw=json.loads(payload)
        except json.JSONDecodeError as exc: raise ValueError('Malformed JSON context.') from exc
        if isinstance(raw,dict) and isinstance(raw.get('messages'),list): raw=raw['messages']
        if not isinstance(raw,list): raise ValueError('JSON must be a list of messages, or {"messages": [...]}')
        contents=[]
        for item in raw:
            if not isinstance(item,dict) or not isinstance(item.get('content'),str) or not isinstance(item.get('role'),str):
                raise ValueError('Each JSON message needs string "role" and "content" keys.')
            if item['role'] not in {'user','assistant','system','other'}: raise ValueError('Unsupported message role.')
            contents.append(item['content'])
        value='\n'.join(contents)
    else: raise ValueError('Choose manual, txt, or json context input.')
    return re.sub(r'[\x00-\x08\x0b-\x1f\x7f]', ' ', value).strip()


def summarize(text: str):
    text=extract_context(text)
    if not text: raise ValueError('Add some context to analyze.')
    sentences=[s.strip() for s in re.split(r'[.!?]+',text) if s.strip()]
    words=re.findall(r"\b[\w']+\b",text,flags=re.UNICODE)
    avg=round(len(words)/max(len(sentences),1),1)
    lower=text.lower()
    polite=sum(lower.count(w) for w in ('please','thank you','thanks','kindly'))
    informal=sum(lower.count(w) for w in ('hey','yeah','lol','btw','gonna'))
    formality='somewhat formal' if polite>informal+1 else 'somewhat casual' if informal>polite+1 else 'unclear / mixed'
    greetings=', '.join(s for s in ('hello','hi','hey','good morning') if re.search(r'\b'+re.escape(s)+r'\b',lower)) or 'none detected'
    return {'language':'not inferred; TTS backend currently targets English',
            'sentence_length':f'~{avg} words per sentence',
            'formality':formality,'punctuation':f'{text.count("!")} exclamation marks; {text.count("?")} questions',
            'greetings':greetings, 'tone':'not inferred; select manually'}
