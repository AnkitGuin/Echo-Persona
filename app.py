"""EchoPersona — localhost-only, consent-centered expressive voice synthesis demo."""
import json
import os
import platform
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
import streamlit as st
from echopersona.config import Settings
from echopersona.audio.validation import check_reference
from echopersona.storage.local_store import ProfileStore
from echopersona.services.context import extract_context,summarize
from echopersona.services.emotion import plan
from echopersona.services.generation import generate
from echopersona.backends.chatterbox_backend import ChatterboxBackend
from echopersona.backends.fake_backend import FakeBackend
from echopersona.models import CONSENT_PHRASE,DELIVERIES

st.set_page_config(page_title='EchoPersona · Private expressive speech',page_icon='🔊',layout='wide',initial_sidebar_state='expanded')
st.markdown('''<style>
.block-container {max-width:1180px;padding-top:2rem;} h1,h2,h3 {letter-spacing:-.03em;}
[data-testid="stSidebar"] {background:#f3f6fa;} .subtle {color:#54647a;font-size:0.96rem;}
.banner {padding:1rem 1.3rem; background:#f1f5fb;border:1px solid #e1e7f0;border-radius:12px;margin:1rem 0;}
</style>''',unsafe_allow_html=True)
try:
    settings=Settings.from_env()
    store=ProfileStore(settings.data_dir)
except Exception as exc:
    st.error(f'Cannot start EchoPersona: {type(exc).__name__}. Check .env values and local data directory permissions.')
    st.stop()

for key, default in {'mode':settings.mode,'active_profile':None,'context_summary':None,
                     'comparison':{},'ratings':[],'context_approved':False}.items():
    if key not in st.session_state: st.session_state[key]=default

PAGES=['Start here','Voice profiles','Conversation context','Speech studio','Compare & evaluate','Privacy & data']
with st.sidebar:
    st.title('EchoPersona')
    st.caption('Local • consent-first • experimental')
    page=st.radio('Navigation',PAGES,label_visibility='collapsed')
    available_modes=['demo','live_local']+(['test'] if settings.mode=='test' else [])
    mode=st.selectbox('Runtime mode',available_modes,index=available_modes.index(st.session_state['mode']) if st.session_state['mode'] in available_modes else 0,
                      help='Live loads Chatterbox only after you press Generate; test mode is a non-speech tone.')
    st.session_state['mode']=mode
    st.caption('Mode: '+{'demo':'Interface preview only','live_local':'Real local TTS (optional package & weights)','test':'Artificial test tone only'}[mode])
    st.divider()
    st.caption('Voice cloning requires the speaker’s permission. Generated speech is synthetic.')

profiles=store.list_profiles()
profile_choices={p['profile_id']:p['display_name']+' · '+p['profile_id'][:7] for p in profiles}
if st.session_state['active_profile'] not in profile_choices:
    st.session_state['active_profile']=next(iter(profile_choices),None)

def choose_profile():
    if not profile_choices: return None
    ids=list(profile_choices)
    pid=st.selectbox('Active voice profile',ids,index=ids.index(st.session_state['active_profile']),format_func=profile_choices.get)
    st.session_state['active_profile']=pid
    return pid

def notice():
    st.info('AI-generated speech: outputs are synthetic and may not reliably match a voice or emotion. Use only your own voice or an adult speaker’s explicitly authorized voice. No medical or identity-authentication claims.')

@st.cache_resource(show_spinner=False)
def cached_local_backend(device):
    # Local single-user cache avoids downloading/loading the large checkpoint twice in an A/B comparison.
    return ChatterboxBackend(device)

def check_upload(upload):
    return check_reference(upload.getvalue(),upload.name,settings.max_upload_mb,settings.max_reference_seconds)

def show_result(key, result):
    st.markdown(f'**{key} — {result.delivery.replace("_"," ").title()}**')
    st.audio(result.audio_bytes,format='audio/wav')
    st.download_button('Download '+key+' WAV',result.audio_bytes,file_name=f'echopersona_{key.lower()}.wav',mime='audio/wav',key=f'dl_{key}')
    st.download_button('Download '+key+' provenance JSON',json.dumps(result.metadata(),indent=2).encode(),file_name=f'echopersona_{key.lower()}_provenance.json',mime='application/json',key=f'meta_{key}')
    with st.expander('Generation details'):
        st.json(result.metadata())
    for warning in result.warnings: st.warning(warning)
    st.caption('AI-generated speech. Synthetic audio—review before sharing; never represent as an authentic recording.')

if page=='Start here':
    st.title('A voice, guided by your intent.')
    st.markdown('<p class="subtle">Private, local-first expressive speech synthesis using your own or explicitly authorized voice reference.</p>',unsafe_allow_html=True)
    notice()
    a,b,c=st.columns(3)
    a.metric('Saved voice profiles',len(profiles))
    b.metric('Current runtime',mode)
    c.metric('Local processing','No cloud calls')
    st.subheader('Three steps to a thoughtful message')
    a,b,c=st.columns(3)
    with a:
        st.markdown('#### 01 · Record')
        st.write('Confirm consent and upload 5–30 seconds of clean speech.')
    with b:
        st.markdown('#### 02 · Context')
        st.write('Review lightweight style observations from text you provide.')
    with c:
        st.markdown('#### 03 · Create')
        st.write('Accept or override a delivery suggestion, then compare neutral and conditioned speech in live mode.')
    st.divider()
    st.subheader('Runtime readiness')
    if mode=='demo':
        st.success('Demo mode is ready. Review profiles, summaries, tone choices, and the interface without model weights.')
        st.info('This build does not bundle a licensed/consented demonstration voice. Demo mode does not output speech. Switch to live_local to synthesize.')
    elif mode=='test': st.warning('Test mode emits an artificial test tone, never a human voice. Run as a test fixture only.')
    else:
        status=ChatterboxBackend(settings.device).health_check()
        st.info(status)
        st.caption('Live mode requires optional installed ML dependencies and may download large checkpoints on first use. Confirm before initiating inference.')
    st.caption('Data is stored in a local folder. Streamlit defaults to localhost when run with the supplied configuration; do not deploy publicly without new security controls.')

elif page=='Voice profiles':
    st.title('Voice profiles')
    notice()
    with st.expander('Create a new voice profile',expanded=not profiles):
        st.markdown('**Speaker consent is required.** Do not use minors’ voices or third-party recordings without explicit adult permission. A typed statement is an acknowledgement, **not identity verification**.')
        with st.form('create_form',clear_on_submit=False):
            name=st.text_input('Profile display name',max_chars=80,placeholder='My voice')
            consent=st.radio('Who is the recording from?',('Not selected','My own voice','An adult speaker who explicitly granted permission'))
            confirmation=st.text_input('Type the exact permission statement',placeholder=CONSENT_PHRASE)
            upload=st.file_uploader('Voice reference (WAV, FLAC, OGG, supported MP3; 1–30 seconds)',type=['wav','flac','ogg','mp3'])
            transcript=st.text_area('Reference transcript (optional, only if needed)',max_chars=400)
            submitted=st.form_submit_button('Validate and save voice profile',type='primary')
        if upload:
            st.audio(upload)
            st.caption('Preview your recording before saving. Level and silence checks cannot certify that intelligible speech is present.')
        if submitted:
            try:
                scope={'My own voice':'own_voice','An adult speaker who explicitly granted permission':'authorized_adult_voice'}.get(consent)
                if not scope or confirmation!=CONSENT_PHRASE: raise PermissionError('Choose an authorization statement and type the complete confirmation exactly.')
                if upload is None: raise ValueError('Choose a valid reference file first.')
                check=check_upload(upload)
                p=store.create(name,scope,confirmation,check.wav_bytes,check,transcript)
                st.session_state['active_profile']=p['profile_id']
                st.success('Profile saved locally. No audio was uploaded to a remote service.')
                for w in check.warnings: st.warning(w)
                st.rerun()
            except (ValueError,PermissionError,OSError) as exc: st.error(str(exc))
    if profiles:
        st.subheader('Manage a saved profile')
        pid=choose_profile()
        p=store.load(pid)
        st.write('**Consent scope:**',p['consent_scope'].replace('_',' '),' | **Created:**',p['created_at'][:10])
        with st.expander('Recording details and references',expanded=True):
            for label,ref in p['emotion_references'].items():
                st.markdown(f'**{label.replace("_"," ").title()}** · {ref["duration_seconds"]:.1f}s · {ref["sample_rate_hz"]}Hz')
                try:
                    f,_=store.reference(pid,label)
                    st.audio(Path(f).read_bytes(),format='audio/wav')
                except (OSError,ValueError): st.warning('Reference file is unavailable.')
                if label!='neutral' and st.button('Delete '+label+' reference',key='del_'+label):
                    try: store.remove_reference(pid,label); st.rerun()
                    except (OSError,ValueError) as exc: st.error(str(exc))
        with st.form('additional_clip'):
            label=st.selectbox('New emotional reference label',[e for e in DELIVERIES if e!='neutral'])
            add=st.file_uploader('Additional recording from same consenting speaker',type=['wav','flac','ogg','mp3'],key='extra_audio')
            ref_transcript=st.text_input('Reference transcript (optional)',max_chars=400)
            submit=st.form_submit_button('Save / replace this reference')
        if add: st.audio(add)
        if submit:
            try:
                if add is None: raise ValueError('Select the reference audio before saving.')
                checked=check_upload(add)
                store.add_reference(pid,label,checked.wav_bytes,checked,ref_transcript)
                st.success('Reference saved locally.'); st.rerun()
            except (OSError,ValueError) as exc: st.error(str(exc))

elif page=='Conversation context':
    st.title('Conversation context')
    st.caption('Review approximate writing-style observations. This is not psychological or emotional-state profiling.')
    st.warning('Import only text you have permission to use. Raw conversation history stays in this browser session and is not saved to a voice profile by default.')
    source=st.radio('Choose context input',('Paste text','Upload .txt','Upload .json'),horizontal=True)
    payload=''; kind='manual'
    if source=='Paste text': payload=st.text_area('Conversation excerpt',height=180,placeholder='Hello! Thanks for checking in. Please take your time…')
    else:
        file=st.file_uploader('Conversation export',type=['txt'] if source=='Upload .txt' else ['json'])
        kind='txt' if source=='Upload .txt' else 'json'
        if file:
            try:
                # JSON may escape each non-ASCII source character as six
                # bytes (\uXXXX), so leave room for encoding overhead while
                # keeping the pre-decode allocation bounded.
                if file.size > 800_000:
                    raise ValueError('Context upload exceeds the 100,000-character limit.')
                payload=file.getvalue().decode('utf-8-sig')
            except UnicodeDecodeError: st.error('File must be UTF-8 encoded.')
            except ValueError as exc: st.error(str(exc))
    if st.button('Analyze this context',type='primary',disabled=not bool(payload.strip())):
        try:
            extracted=extract_context(payload,kind)
            st.session_state['context_summary']=summarize(extracted)
            st.session_state['context_approved']=False
            st.success('Generated a local heuristic summary. Review and edit before using.')
        except ValueError as exc: st.error(str(exc))
    if st.session_state['context_summary']:
        st.subheader('Review and edit observations')
        current=st.session_state['context_summary']
        with st.form('edit_context'):
            edited={k:st.text_input(k.replace('_',' ').title(),value=str(current.get(k,'')),key='context_edit_'+k) for k in ('language','sentence_length','formality','punctuation','greetings')}
            tone=st.selectbox('My preferred delivery (explicit user preference)',DELIVERIES,index=DELIVERIES.index(current['tone']) if current.get('tone') in DELIVERIES else 0,format_func=lambda x:x.replace('_',' ').title())
            edited['tone']=tone
            accept=st.form_submit_button('Approve summary for this session')
        if accept:
            st.session_state['context_summary']=edited
            st.session_state['context_approved']=True
            st.success('Approved for this session; you can choose whether to save it to a profile.')
        if profiles:
            pid=choose_profile()
            if st.button('Save only this approved summary to selected profile',disabled=not st.session_state['context_approved']):
                store.save_preferences(pid,st.session_state['context_summary'])
                st.success('Saved compact summary only. Original conversation messages were not stored.')
        if st.button('Clear context from this session'):
            st.session_state['context_summary']=None
            st.session_state['context_approved']=False
            st.success('Context summary cleared. Clear input widgets or refresh to clear pasted text.')

elif page=='Speech studio':
    st.title('Speech studio')
    notice()
    pid=choose_profile()
    if not pid:
        st.warning('Create a consenting voice profile first in Voice profiles.')
    current_profile=store.load(pid) if pid else None
    text=st.text_area('Message to speak',height=145,max_chars=settings.max_text_chars,placeholder='You worked hard on this. Let’s celebrate your progress.')
    st.caption(f'{len(text)} / {settings.max_text_chars} characters · English for Chatterbox original')
    session_summary=(st.session_state.get('context_summary')
                     if st.session_state.get('context_approved') else None)
    saved_preferences=(current_profile or {}).get('communication_preferences') or None
    summary=session_summary or saved_preferences
    use_context=st.checkbox('Use my approved communication preferences',value=False,disabled=not bool(summary))
    if use_context and summary: st.caption('Approved context is used for a fallback delivery preference; it is not sent to the model as a prompt.')
    suggested=None
    if text.strip():
        try:
            suggested=plan(text,context=summary if use_context else None)
            st.info('Suggested delivery: **'+suggested.label.replace('_',' ').title()+'** · '+suggested.confidence+' confidence. '+suggested.explanation)
        except ValueError as exc: st.error(str(exc))
    manual=st.checkbox('Override the suggested delivery',value=False)
    choices=list(DELIVERIES)
    manual_selection=st.selectbox('Chosen delivery',choices,format_func=lambda x:x.replace('_',' ').title(),disabled=not manual)
    intended=manual_selection if manual else suggested.label if suggested else 'neutral'
    intensity=st.slider('Expressiveness preference (not guaranteed emotion strength)',0.0,1.0,0.5,0.05)
    st.caption('Chatterbox original exposes an expressiveness/exaggeration parameter, not reliable categorical emotion control. Matched reference clips are used when available.')
    if mode=='demo': st.info('Demo mode: speech synthesis is disabled. No licensed demo speaker assets were bundled. Choose live_local to generate with your own recorded voice.')
    elif mode=='test': st.warning('Test mode generates only artificial tones, not speech. Use to verify orchestration.')
    else:
        live_status=ChatterboxBackend(settings.device).health_check()
        if 'not installed' in live_status:
            st.error(live_status+' Install the optional backend with `pip install -r requirements-live.txt`.')
        else:
            st.warning('First generation may download significant model weights. Live inference requires an appropriate Python/PyTorch setup, hardware, and internet for first-time model download. No reference recordings are sent to a hosted TTS service.')
    live_missing=(mode=='live_local' and 'not installed' in ChatterboxBackend(settings.device).health_check())
    disabled=not pid or not text.strip() or mode=='demo' or live_missing
    a,b,c=st.columns(3)
    def do_generate(which):
        try:
            backend=FakeBackend() if mode=='test' else cached_local_backend(settings.device)
            with st.spinner('Loading local model and synthesizing…' if mode=='live_local' else 'Generating test tone…'):
                out=generate(store,backend,pid,text,which,intensity,mode,settings.max_text_chars)
            return out
        except Exception as exc:
            st.error(f'Generation unavailable: {str(exc)}')
            return None
    if a.button('Generate neutral',disabled=disabled,use_container_width=True):
        x=do_generate('neutral')
        if x: st.session_state['comparison']={'text':text,'profile_id':pid,'A':x}
    if b.button('Generate context-aware',disabled=disabled,use_container_width=True):
        x=do_generate(intended)
        if x: st.session_state['comparison']={'text':text,'profile_id':pid,'B':x}
    if c.button('Compare both',disabled=disabled,use_container_width=True,type='primary'):
        x=do_generate('neutral')
        if x:
            y=do_generate(intended)
            if y: st.session_state['comparison']={'text':text,'profile_id':pid,'A':x,'B':y}
    history=st.session_state.get('comparison',{})
    if history.get('text')==text and history.get('profile_id')==pid:
        for key in ('A','B'):
            if key in history:
                st.divider(); show_result(key,history[key])
    elif history: st.caption('Prior result belongs to a different text or profile; open Compare & evaluate to review it.')

elif page=='Compare & evaluate':
    st.title('Compare & evaluate')
    history=st.session_state.get('comparison',{})
    if not history:
        st.info('No results yet. Generate the neutral baseline and the selected delivery in Speech studio.')
    else:
        st.write('**Text used for this comparison:**',history['text'])
        left,right=st.columns(2)
        for col,key in ((left,'A'),(right,'B')):
            with col:
                if key in history: show_result(key,history[key])
                else: st.caption('Generate this variant in Speech studio to complete the comparison.')
        if 'A' in history and 'B' in history:
            st.subheader('Your own listening ratings')
            st.caption('Exploratory self-report only, never a fabricated model benchmark or proof of speaker identity.')
            with st.form('ratings'):
                values={}
                for metric in ('Intelligibility','Naturalness','Voice resemblance','Match to intended tone','Overall preference'):
                    values[metric]=st.slider(metric+' (1–5)',1,5,3)
                comment=st.text_input('Optional note',max_chars=300)
                if st.form_submit_button('Save session-only rating'):
                    st.session_state['ratings'].append({'ratings':values,'note':comment,'mode':mode})
                    st.success('Rating saved in current session only.')
            st.caption(f'Session rating entries: {len(st.session_state["ratings"])}')

elif page=='Privacy & data':
    st.title('Privacy & data controls')
    notice()
    st.write('**Storage location:**',str(settings.data_dir))
    st.write('**Cloud TTS/text providers:** None configured. Chatterbox may contact model-hosting servers to download weights on first setup. No user text or reference audio is intentionally sent to a hosted inference API.')
    st.write('**Profiles stored:**',len(profiles))
    st.write('**Conversation:** raw uploads are not persisted by the backend; approved compact preferences are saved only when you press the save button.')
    st.write('**Generation audio:** current session only. No saved generation history in this MVP, regardless of SAVE_GENERATION_HISTORY.')
    if st.button('Clear imported context summary'):
        st.session_state['context_summary']=None
        st.session_state['context_approved']=False
        st.success('Session summary cleared. Clear page inputs if you also want to remove pasted text from session widgets.')
    if st.button('Clear session generations & ratings'):
        st.session_state['comparison']={}; st.session_state['ratings']=[]
        st.success('Session generations and ratings cleared.')
    if profiles:
        pid=choose_profile()
        typed=st.text_input('Type DELETE to confirm deletion of the selected profile')
        if st.button('Delete selected voice profile',disabled=typed!='DELETE'):
            try:
                store.delete(pid)
                st.session_state['active_profile']=None
                st.session_state['comparison']={}
                st.success('Deleted selected profile and its references.'); st.rerun()
            except OSError: st.error('Deletion failed due to file permissions. Check local storage.')
        confirm_all=st.text_input('Type DELETE ALL to remove every saved profile')
        if st.button('Delete all local project profiles',disabled=confirm_all!='DELETE ALL'):
            try:
                store.delete_all()
                st.session_state['active_profile']=None; st.session_state['comparison']={}
                st.session_state['context_summary']=None; st.session_state['ratings']=[]
                st.success('All app profile files removed.'); st.rerun()
            except OSError: st.error('Some files could not be removed. Check local storage.')
    with st.expander('Local runtime diagnostics'):
        st.write('Python:',platform.python_version())
        st.write('OS:',platform.system())
        st.write('Mode:',mode)
        st.write('Backend:',ChatterboxBackend(settings.device).health_check())
        st.write('Configured device:',settings.device)
    st.caption('App deletion is not a forensic secure erase of SSD blocks, system backups, temporary operating-system caches, or copies saved elsewhere. Run only on a trusted device. Do not expose this unauthenticated prototype publicly.')
