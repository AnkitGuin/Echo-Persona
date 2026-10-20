"""Explainable, conservative suggestions for intended speaking delivery."""
import re
from ..models import EmotionPlan, DELIVERIES
RULES = {
    'warm_reassuring': ('you can do this','i am here','we can work','you are not alone','take your time','proud of you'),
    'excited': ('congratulations','amazing news','so excited','can’t wait','cannot wait','woohoo'),
    'happy': ('happy','thank you','great job','wonderful','so glad','love this'),
    'concerned': ('are you okay','worried about','please be careful','is everything alright'),
    'sad_reflective': ('i miss','sorry for your loss','deeply sorry','heartbroken'),
    'calm': ('take a breath','slow down','one step at a time','stay calm'),
}

def plan(text: str, intensity=0.5, override=None, context=None) -> EmotionPlan:
    if not text.strip(): raise ValueError('Enter text to synthesize.')
    if not isinstance(intensity,(float,int)) or not 0<=intensity<=1:
        raise ValueError('Intensity must be between 0 and 1.')
    if override is not None:
        if override not in DELIVERIES: raise ValueError('Unsupported manual delivery')
        return EmotionPlan(override,float(intensity),'user selected','Manual delivery choice takes precedence; model delivery remains best-effort.')
    # Match whole phrases, not arbitrary substrings (for example, "hey" in
    # "they"). A small local negation check avoids treating "not happy" as a
    # positive cue. These remain lexical hints, not a sentiment classifier.
    lower=re.sub(r'\s+',' ',text.lower().replace('’', "'"))
    scores={k:sum(1 for phrase in phrases if _cue_is_present(lower, phrase))
            for k,phrases in RULES.items()}
    hits=sorted(scores,key=scores.get,reverse=True)
    if scores[hits[0]]==0:
        preferred = context.get('tone') if isinstance(context,dict) else None
        if preferred in DELIVERIES and preferred!='neutral':
            return EmotionPlan(preferred,float(intensity),'low',
                'No clear textual cue; using the delivery preference you explicitly approved. Please verify.')
        return EmotionPlan('neutral',float(intensity),'low','No reliable textual delivery cue. Context is not treated as proof of emotion.')
    if len(hits)>1 and scores[hits[0]]==scores[hits[1]]:
        return EmotionPlan('neutral',float(intensity),'low','Conflicting delivery cues; please choose the intended tone yourself.')
    return EmotionPlan(hits[0],float(intensity),'medium',f'Phrase-based cue suggests {hits[0].replace("_"," ")}; review this suggestion.')


_NEGATION = re.compile(r"\b(?:not|never|no|hardly|isn't|aren't|wasn't|weren't|don't|doesn't|didn't|won't|can't|cannot)\b(?:\W+\w+){0,2}\W*$")


def _cue_is_present(text: str, phrase: str) -> bool:
    normalized = phrase.replace('’', "'").lower()
    match = re.search(r'(?<!\w)' + re.escape(normalized) + r'(?!\w)', text)
    if not match:
        return False
    return not _NEGATION.search(text[:match.start()])
