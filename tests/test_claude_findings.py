"""D1-D7 and Windows junction regressions. All approval/recovery fixtures are synthetic."""
from __future__ import annotations

import copy
import io
import json
import os
import subprocess
import urllib.error
from pathlib import Path

import pytest

from granthstudio.comfy import ComfyBackend
from granthstudio.config import load_models, load_yaml
from granthstudio.episodes import compile_episode
from granthstudio.errors import ConfigError, GateFailure, JobPending, SchemaError, TaskFailed
from granthstudio.ffmpeg import Probe, assemble, audio_video_tolerance, probe, validate_video
from granthstudio.integrity import atomic_write_json, contained_path, read_json, sha256_file, sha256_obj
from granthstudio.pipeline import load_bundle, production_problems, snapshot
from granthstudio.research import approve, load_research, require_approved
from granthstudio.scheduler import Scheduler, Task
from granthstudio.timelines import srt_text
from tests.conftest import FIXED_TIME, have_tool


def prepare_current_pilot(project):
    """Real compiler contract for a synthetic chapter-1 pilot and separate chapter-2 release."""
    research = load_yaml(project.research_dir / 'adhyay_01' / 'research.yaml')
    manifest = load_yaml(project.episodes_dir / 'adhyay_01' / 'manifest.yaml')
    timelines = {lang: load_yaml(project.episodes_dir / 'adhyay_01' / f'{lang}.yaml') for lang in ('mr', 'hi')}
    r2, m2 = copy.deepcopy(research), copy.deepcopy(manifest)
    r2['adhyay'] = m2['adhyay'] = 2
    m2['episode_id'] = 'ep02'
    r2['scenes'][0]['scene_id'] = 'a02_s01'
    m2['scenes'][0].update(scene_id='a02_s01', research_scene='a02_s01')
    for shot in m2['scenes'][0]['shots']:
        shot['shot_id'] = shot['shot_id'].replace('a01_', 'a02_')
        shot.pop('pilot_shot', None)
    atomic_write_json(project.research_dir / 'adhyay_02' / 'research.yaml', r2)
    approve(project, 2, 'synthetic-test-only', FIXED_TIME)
    atomic_write_json(project.episodes_dir / 'adhyay_02' / 'manifest.yaml', m2)
    for lang, timeline in timelines.items():
        t2 = copy.deepcopy(timeline); t2['adhyay'] = 2
        for entry in t2['entries']: entry['shot_id'] = entry['shot_id'].replace('a01_', 'a02_')
        atomic_write_json(project.episodes_dir / 'adhyay_02' / f'{lang}.yaml', t2)

    original = research['scenes'][0]
    first_line, second_line = copy.deepcopy(original['dialogue'])
    original['dialogue'] = [first_line]
    night = copy.deepcopy(original)
    night.update(scene_id='a01_s02', dialogue=[second_line])
    night['actions'][0]['id'] = 'night_turn'
    research['scenes'].append(night)
    atomic_write_json(project.research_dir / 'adhyay_01' / 'research.yaml', research)
    receipt = approve(project, 1, 'synthetic-test-only', FIXED_TIME)
    manifest['research_version'] = receipt['version']
    scene = manifest['scenes'][0]
    visuals = manifest['visuals'][0]['visual_id']
    shots = []
    for index, label in enumerate('ABCDF', start=1):
        tier = {'A': 0, 'B': 1, 'C': 2, 'D': 1, 'F': 0}[label]
        shot = {'shot_id': f'a01_s01_sh{index:02d}', 'tier': tier, 'visual_id': visuals,
                'duration_s': 0.5 if tier == 0 else 49/24, 'dialogue_ids': ['d_0001'] if label == 'D' else [],
                'pilot_shot': label}
        if tier: shot.update(frames=49, action_ids=['action_turn'])
        if tier == 2: shot['end_visual_id'] = visuals
        shots.append(shot)
    scene['shots'] = shots
    night_manifest = copy.deepcopy(scene)
    night_manifest.update(scene_id='a01_s02', research_scene='a01_s02', lighting='night', shots=[{
        'shot_id':'a01_s02_sh01','tier':1,'visual_id':visuals,'duration_s':49/24,'frames':49,
        'action_ids':['night_turn'],'dialogue_ids':['d_0002'],'pilot_shot':'E'}])
    manifest['scenes'].append(night_manifest)
    atomic_write_json(project.episodes_dir / 'adhyay_01' / 'manifest.yaml', manifest)
    for lang, timeline in timelines.items():
        timeline['entries'][0]['shot_id'] = 'a01_s01_sh04'
        timeline['entries'][1]['shot_id'] = 'a01_s02_sh01'
        atomic_write_json(project.episodes_dir / 'adhyay_01' / f'{lang}.yaml', timeline)
    models = load_models(project)
    models['ltx']['capabilities']['flf'] = 'disabled'
    atomic_write_json(project.root / 'config' / 'models.yaml', models)
    return load_bundle(project, models, 2)


def recovery_tasks(interrupt=None, variant='pilot'):
    """Synthetic assembly tasks; policy tests check provenance and hashes, not media or GPU results."""
    tasks = []
    for language in ('mr', 'hi'):
        def run(work, language=language):
            if language == interrupt:
                raise TaskFailed('synthetic interruption')
            (work / f'{language}.mp4').write_bytes(f'SYNTHETIC POLICY ARTIFACT {language}'.encode())
            return {'video': f'{language}.mp4'}
        tasks.append(Task('assembly', f'assemble_{language}', {'language': language, 'variant': variant}, 'synthetic', run))
    return tasks


def recovery_outputs(project, store, tasks):
    scheduler = Scheduler(store)
    return {f"{t.inputs['language']}_video": {
        'path': (scheduler.task_dir(t) / f"{t.inputs['language']}.mp4").relative_to(project.artifacts_dir).as_posix(),
        'sha256': sha256_file(scheduler.task_dir(t) / f"{t.inputs['language']}.mp4")} for t in tasks}


def synthetic_recovery(project, pilot_hash):
    """Real scheduler runs: one clean, one interrupted then resumed in a separate store."""
    clean, resumed = project.artifacts_dir / 'recovery' / 'clean', project.artifacts_dir / 'recovery' / 'resumed'
    assert all(r.status == 'complete' for r in Scheduler(clean).run(recovery_tasks()))
    assert [r.status for r in Scheduler(resumed).run(recovery_tasks(interrupt='hi'))] == ['complete', 'failed']
    assert [r.status for r in Scheduler(resumed).run(recovery_tasks())] == ['resumed', 'complete']
    return {'schema_version':1,'passed':True,'reviewed_by':'synthetic-test-only','pilot_plan_sha256':pilot_hash,
            'clean_outputs':recovery_outputs(project, clean, recovery_tasks()),
            'resumed_outputs':recovery_outputs(project, resumed, recovery_tasks())}


def policy_fixture(project, monkeypatch):
    from types import SimpleNamespace
    import granthstudio.pipeline as pipeline
    current = prepare_current_pilot(project)
    monkeypatch.setattr(pipeline, '_ltx_preflight', lambda *_: SimpleNamespace(version='synthetic-graph'))
    monkeypatch.setattr(pipeline, 'require_capability', lambda *_: {'runtime_sha256':'a'*64})
    pilot_path = project.benchmarks_dir / 'synthetic-pilot.json'
    atomic_write_json(pilot_path, load_bundle(project, current.models, 1).compiled)
    refs=[]
    for label, capability in zip('ABCDEF', ('tier0','i2v','flf','i2v','i2v','assembly')):
        record={'schema_version':1,'capability':capability,'shot':label,'checkpoint_sha256':None,
            'workflow_version':'synthetic-graph','runtime_sha256':'a'*64,'gpu':'T4','gpu_count':1,
            'gpu_seconds_total':60,'attempts':1,'video_seconds':2,'accepted':label!='C',
            'outcome':'fail' if label=='C' else 'pass','recorded_at':FIXED_TIME,
            'pilot_plan_sha256':sha256_file(pilot_path)}
        path=project.benchmarks_dir / f'synthetic-{label}.json'; atomic_write_json(path,record)
        refs.append({'path':path.name,'sha256':sha256_file(path)})
    recovery_path=project.benchmarks_dir / 'synthetic-recovery.json'
    atomic_write_json(recovery_path,synthetic_recovery(project,sha256_file(pilot_path)))
    approval={'schema_version':1,'adhyay':2,'approved':True,'reviewed_by':'synthetic-test-only',
        'input_sha256':sha256_obj(snapshot(current)),'pilot_receipts':refs,
        'pilot_plan':{'path':pilot_path.name,'sha256':sha256_file(pilot_path)},
        'recovery_evidence':{'path':recovery_path.name,'sha256':sha256_file(recovery_path)},
        'minimum_accepted_sec_per_gpu_hour':1,'flf_decision':'no_go'}
    approval_path=project.root / 'approvals' / 'adhyay_02.json'
    atomic_write_json(approval_path,approval)
    assert production_problems(current)==[]
    return current,approval,approval_path,recovery_path,pilot_path


@pytest.mark.parametrize('status',[400,401,422])
def test_d1_http_4xx_rejection_is_definitive_and_journal_retryable(tmp_path,monkeypatch,status):
    import granthstudio.comfy as comfy
    backend=ComfyBackend('http://synthetic.invalid')
    journal=tmp_path/'job.json'
    calls=[]
    def reject(request,**kwargs):
        calls.append(request.method)
        raise urllib.error.HTTPError(request.full_url,status,'definitive rejection',None,io.BytesIO(b'bad graph'))
    monkeypatch.setattr(comfy.urllib.request,'urlopen',reject)
    with pytest.raises(TaskFailed,match=f'HTTP {status}'):
        backend.execute({},journal)
    assert read_json(journal)['state']=='failed'
    monkeypatch.setattr(comfy.urllib.request,'urlopen',lambda *a,**k: io.BytesIO(b'{"prompt_id":"retried"}'))
    monkeypatch.setattr(backend,'wait',lambda prompt: {'prompt_id':prompt})
    assert backend.execute({},journal)=={'prompt_id':'retried'}
    assert read_json(journal)['prompt_id']=='retried'


@pytest.mark.parametrize('error',[TimeoutError('timeout'),urllib.error.URLError('transport'),
    urllib.error.HTTPError('http://synthetic.invalid/prompt',500,'server failure',None,None)])
def test_d1_transport_timeout_and_server_error_remain_ambiguous(tmp_path,monkeypatch,error):
    import granthstudio.comfy as comfy
    backend=ComfyBackend('http://synthetic.invalid'); calls=[]
    def fail(*a,**k): calls.append(1); raise error
    monkeypatch.setattr(comfy.urllib.request,'urlopen',fail)
    for _ in range(2):
        with pytest.raises(JobPending): backend.execute({},tmp_path/'job.json')
    assert len(calls)==1
    assert read_json(tmp_path/'job.json')['state']=='submitting'


def fake_comfy(monkeypatch, poll_status):
    """POST /prompt is accepted; /history answers poll_status (an HTTP error code) or the finished entry."""
    import granthstudio.comfy as comfy
    calls={'POST':0,'GET':0,'poll':poll_status}
    def urlopen(request,**kwargs):
        calls[request.method]+=1
        if request.method=='POST':
            return io.BytesIO(b'{"prompt_id":"original"}')
        if calls['poll'] is not None:
            raise urllib.error.HTTPError(request.full_url,calls['poll'],'proxy status',None,io.BytesIO(b''))
        return io.BytesIO(b'{"original":{"status":{"status_str":"success"},"outputs":{}}}')
    monkeypatch.setattr(comfy.urllib.request,'urlopen',urlopen)
    return calls


@pytest.mark.parametrize('status',[403,404,429])
def test_h1_status_poll_4xx_never_resubmits(tmp_path,monkeypatch,status):
    calls=fake_comfy(monkeypatch,status)
    backend=ComfyBackend('http://synthetic.invalid'); journal=tmp_path/'job.json'
    for _ in range(2):
        with pytest.raises(JobPending): backend.execute({},journal)
    state=read_json(journal)
    assert calls['POST']==1 and state['state']=='submitted' and state['prompt_id']=='original'
    calls['poll']=None  # proxy recovers: resume polling the original prompt
    assert backend.execute({},journal)['status']['status_str']=='success'
    assert calls['POST']==1


@pytest.mark.parametrize('status',[404,429])
def test_h1_scheduler_retries_cannot_duplicate_gpu_submission(tmp_path,monkeypatch,status):
    calls=fake_comfy(monkeypatch,status)
    journal=tmp_path/'job.json'
    def run(work):
        ComfyBackend('http://synthetic.invalid').execute({},journal)
        (work/'clip.mp4').write_bytes(b'synthetic'); return {'clip':'clip.mp4'}
    task=Task('tier1','shot',{},'v',run,max_attempts=3)
    first=Scheduler(tmp_path/'store').run([task])
    assert first[0].status=='pending' and first[0].attempts==1
    assert calls['POST']==1 and read_json(journal)['prompt_id']=='original'
    calls['poll']=None
    assert Scheduler(tmp_path/'store').run([task])[0].status=='complete'
    assert calls['POST']==1


def test_d2_srt_point_one_point_two_five_point_one_rounding():
    entries=[{'dialogue_id':'d_0001','text':'one','start_s':0,'measured_duration_s':0.1},
             {'dialogue_id':'d_0002','text':'two','start_s':0.3-0.2,'measured_duration_s':0.25},
             {'dialogue_id':'d_0003','text':'three','start_s':0.35,'measured_duration_s':0.1}]
    result=srt_text(entries)
    assert '00:00:00,000 --> 00:00:00,100' in result
    assert '00:00:00,100 --> 00:00:00,350' in result
    assert '00:00:00,350 --> 00:00:00,450' in result


def test_d2_real_microsecond_subtitle_overlap_is_rejected():
    entries=[{'dialogue_id':'d_0001','text':'one','measured_duration_s':0.1},
             {'dialogue_id':'d_0002','text':'two','start_s':0.1-1e-6,'measured_duration_s':0.25}]
    with pytest.raises(GateFailure,match='overlap'): srt_text(entries)


@pytest.mark.parametrize('change',['shot_id','labels'])
def test_d3_valid_file_hash_cannot_hide_different_current_pilot_assignments(approved_project,monkeypatch,change):
    from granthstudio.pilot import plan_pilot
    current,approval,approval_path,recovery_path,pilot_path=policy_fixture(approved_project,monkeypatch)
    plan=read_json(pilot_path)
    if change=='shot_id': plan['shots'][1]['shot_id']='a01_s01_sh99'
    else:
        a=next(s for s in plan['shots'] if s['pilot_shot']=='A')
        f=next(s for s in plan['shots'] if s['pilot_shot']=='F')
        a['pilot_shot'],f['pilot_shot']='F','A'
    plan['pilot']=plan_pilot(plan)
    atomic_write_json(pilot_path,plan)
    approval['pilot_plan']['sha256']=sha256_file(pilot_path)
    # Re-pin every file hash so rejection must come from current-manifest binding.
    for ref in approval['pilot_receipts']:
        path=approved_project.benchmarks_dir/ref['path']; record=read_json(path)
        record['pilot_plan_sha256']=sha256_file(pilot_path); atomic_write_json(path,record)
        ref['sha256']=sha256_file(path)
    recovery=read_json(recovery_path); recovery['pilot_plan_sha256']=sha256_file(pilot_path)
    atomic_write_json(recovery_path,recovery)
    approval['recovery_evidence']['sha256']=sha256_file(recovery_path)
    atomic_write_json(approval_path,approval)
    assert any('current compiled pilot manifest' in p for p in production_problems(current))


def rewrite_recovery(project,approval,approval_path,recovery_path,evidence):
    atomic_write_json(recovery_path,evidence)
    approval['recovery_evidence']['sha256']=sha256_file(recovery_path)
    atomic_write_json(approval_path,approval)


@pytest.mark.parametrize('change,reason',[('flag_only','recovery_evidence'),('wrong_hash','hash mismatch: mr_video'),
    ('different_outputs','hashes differ: mr_video'),('tampered_output','mr_video is not recorded by its task receipt'),
    ('missing_file','No such file|cannot find'),
    ('other_pilot','another pilot plan')])
def test_d4_recovery_requires_actual_matching_output_files(approved_project,monkeypatch,change,reason):
    import re
    current,approval,approval_path,recovery_path,_=policy_fixture(approved_project,monkeypatch)
    evidence=read_json(recovery_path)
    if change=='flag_only': evidence={'passed':True,'reviewed_by':'synthetic-test-only'}
    elif change=='wrong_hash': evidence['clean_outputs']['mr_video']['sha256']='0'*64
    elif change in ('different_outputs','tampered_output'):
        ref=evidence['resumed_outputs']['mr_video']; path=approved_project.artifacts_dir/ref['path']
        path.write_bytes(b'different actual output'); ref['sha256']=sha256_file(path)
        if change=='different_outputs':  # the resumed task really sealed different bytes
            receipt=read_json(path.parent/'task_receipt.json'); receipt['outputs']['video']['sha256']=ref['sha256']
            atomic_write_json(path.parent/'task_receipt.json',receipt)
    elif change=='missing_file':
        path=approved_project.artifacts_dir/evidence['resumed_outputs']['hi_video']['path']; path.unlink()
    else: evidence['pilot_plan_sha256']='d'*64
    rewrite_recovery(approved_project,approval,approval_path,recovery_path,evidence)
    problems=production_problems(current)
    assert len(problems)==1 and re.search(reason,problems[0]),problems


@pytest.mark.parametrize('alias',['clean_is_resumed','marathi_is_hindi','case_variant','hard_link'])
def test_m1_one_file_cannot_prove_two_recovery_outputs(approved_project,monkeypatch,alias):
    current,approval,approval_path,recovery_path,_=policy_fixture(approved_project,monkeypatch)
    evidence=read_json(recovery_path)
    clean,resumed=evidence['clean_outputs'],evidence['resumed_outputs']
    if alias=='clean_is_resumed':
        resumed['mr_video']=dict(clean['mr_video'])
    elif alias=='marathi_is_hindi':
        # Same bytes for both languages in both runs, so only identity can reject it.
        for run in (clean,resumed): run['hi_video']=dict(run['mr_video'])
        resumed['hi_video']=dict(clean['mr_video'])
    elif alias=='case_variant':
        if os.name!='nt': pytest.skip('case-insensitive paths are a Windows property')
        resumed['mr_video']={'path':clean['mr_video']['path'].upper(),'sha256':clean['mr_video']['sha256']}
    else:
        target=approved_project.artifacts_dir/resumed['mr_video']['path']; target.unlink()
        try: os.link(approved_project.artifacts_dir/clean['mr_video']['path'],target)
        except OSError as exc: pytest.skip(f'hard links unsupported here: {exc}')
    rewrite_recovery(approved_project,approval,approval_path,recovery_path,evidence)
    problems=production_problems(current)
    assert len(problems)==1 and 'alias one file' in problems[0],problems


def test_d5_gate_failure_stops_first_attempt_and_blocks_dependents(tmp_path):
    calls=[]
    def fail(work):
        calls.append(1); (work/'partial.bin').write_bytes(b'partial')
        raise GateFailure('permanent gate refusal')
    first=Task('tier0','gate',{},'v',fail,max_attempts=3)
    second=Task('assembly','after',{},'v',lambda _: pytest.fail('dependent executed'),depends_on=(first.task_id(),))
    scheduler=Scheduler(tmp_path)
    result=scheduler.run([first,second])
    assert len(calls)==1 and result[0].status=='failed' and result[0].attempts==1
    assert result[1].status=='blocked'
    assert not scheduler.task_dir(first).exists() and not list((tmp_path/'tier0').glob('.work-*'))


@pytest.mark.parametrize('sample_difference',[1,3])
def test_d6_audio_video_tolerance_uses_samples_not_a_frame(tmp_path,monkeypatch,sample_difference):
    import granthstudio.ffmpeg as media
    audio=tmp_path/'voice.wav'; clip=tmp_path/'clip.mp4'
    video_info=Probe(0.5,'h264',320,240,False,video_duration_s=0.5)
    duration=0.5+sample_difference/48000
    audio_info=Probe(duration,None,None,None,True,audio_duration_s=duration,audio_sample_rate=48000)
    monkeypatch.setattr(media,'probe',lambda path: audio_info if path==audio else video_info)
    monkeypatch.setattr(media,'validate_audio',lambda _: duration)
    monkeypatch.setattr(media,'_tool',lambda name:name)
    calls=[]; monkeypatch.setattr(media,'_run',lambda command:calls.append(command))
    assert audio_video_tolerance(audio_info,[video_info])==2/48000
    if sample_difference==1:
        assemble([clip],tmp_path/'out.mp4',audio)
        assert calls and '-shortest' not in calls[0]
    else:
        with pytest.raises(TaskFailed,match='refusing speech truncation'):
            assemble([clip],tmp_path/'out.mp4',audio)
        assert not calls


def test_d6_container_rounding_does_not_override_measured_stream_timing(tmp_path,monkeypatch):
    import granthstudio.ffmpeg as media
    path=tmp_path/'mux.mp4'; path.write_bytes(b'synthetic media metadata test')
    monkeypatch.setattr(media,'probe',lambda _:Probe(1.024,'h264',320,240,True,
        video_duration_s=1.0,audio_duration_s=1.0,audio_sample_rate=48000))
    decoded=[]; monkeypatch.setattr(media,'decode',lambda path:decoded.append(path))
    assert validate_video(path,1.0,require_audio=True)==[] and decoded==[path]


@pytest.mark.skipif(not (have_tool('ffmpeg') and have_tool('ffprobe')),reason='media tools unavailable')
def test_d6_real_aac_mux_preserves_measured_complete_audio(tmp_path):
    clip=tmp_path/'clip.mp4'; audio=tmp_path/'speech.wav'; output=tmp_path/'release.mp4'
    subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i','color=c=blue:s=160x120:r=24:d=0.5',
        '-c:v','libx264','-threads','1','-pix_fmt','yuv420p',str(clip)],check=True,timeout=20)
    subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i','sine=sample_rate=48000:duration=0.5',
        '-c:a','pcm_s16le',str(audio)],check=True,timeout=20)
    assemble([clip],output,audio)
    info=probe(output)
    assert info.video_duration_s==0.5 and info.audio_duration_s==0.5
    assert validate_video(output,0.5,require_audio=True)==[]


@pytest.mark.parametrize('reviewer',['   ','\t\n'])
def test_d7_whitespace_only_coverage_reviewer_is_rejected(approved_project,reviewer):
    path=approved_project.episodes_dir/'adhyay_01'/'manifest.yaml'
    manifest=load_yaml(path)
    manifest['scenes'][0]['shots'][0]['coverage']={'mode':'hold_final_frame','reviewed_by':reviewer}
    atomic_write_json(path,manifest)
    with pytest.raises(SchemaError,match='reviewed_by'):
        compile_episode(approved_project,load_models(approved_project),load_bundle(approved_project,load_models(approved_project),1).canon,
            1,load_research(approved_project,1),require_approved(approved_project,1))


@pytest.mark.skipif(os.name!='nt',reason='Windows junctions require Windows')
def test_windows_junction_cannot_escape_artifact_root(tmp_path):
    root=tmp_path/'root'; outside=tmp_path/'outside'
    root.mkdir(); outside.mkdir(); (outside/'frame.png').write_bytes(b'untouched')
    junction=root/'escape'
    result=subprocess.run(['cmd.exe','/d','/c','mklink','/J',str(junction),str(outside)],
        capture_output=True,text=True,timeout=10)
    if result.returncode:
        pytest.skip('junction creation unsupported on this Windows filesystem: '+result.stderr.strip())
    try:
        assert junction.is_junction()
        with pytest.raises(ConfigError,match='escapes'):
            contained_path(root,'escape/frame.png')
        assert (outside/'frame.png').read_bytes()==b'untouched'
    finally:
        # Remove only the verified junction entry, never recursively traverse its target.
        assert junction.parent.resolve()==root.resolve() and junction.is_junction()
        os.rmdir(junction)
    assert (outside/'frame.png').is_file()


@pytest.mark.skipif(not (have_tool('ffmpeg') and have_tool('ffprobe')),reason='media tools unavailable')
def test_l1_off_frame_tier0_without_dialogue_assembles(approved_project):
    from granthstudio.pipeline import episode_store, plan_tasks
    from tests.test_review_regressions import make_cpu_project
    make_cpu_project(approved_project)
    path=approved_project.episodes_dir/'adhyay_01'/'manifest.yaml'; manifest=load_yaml(path)
    # Its 0.2 s speech is far shorter than the shot, so only frame rounding could demand coverage.
    silent=manifest['scenes'][0]['shots'][0]
    assert silent['tier']==0
    silent['duration_s']=1.3; silent.pop('coverage')  # 31.2 frames: used to render 31 and fail
    atomic_write_json(path,manifest)
    current=load_bundle(approved_project,load_models(approved_project),1)
    scheduler=Scheduler(episode_store(approved_project,1)); tasks=plan_tasks(current,scheduler)
    results=scheduler.run(tasks)
    assert all(r.status=='complete' for r in results),results
    plan=read_json(scheduler.task_dir(next(t for t in tasks if t.name=='assemble_mr'))/'edit_plan.json')
    shot=next(s for s in plan['shots'] if s['shot_id']==silent['shot_id'])
    assert shot['duration_s']==shot['primary_action_duration_s']==32/24


@pytest.mark.skipif(not (have_tool('ffmpeg') and have_tool('ffprobe')),reason='media tools unavailable')
def test_r1_resampled_44k_22k_speech_lands_on_timeline_without_truncation(tmp_path):
    import math
    from granthstudio.ffmpeg import assemble_audio, still_motion_clip, validate_audio
    from tests.conftest import make_still
    still=make_still(tmp_path/'still.png'); segments=[]; clips=[]; speech=0.0; total=0.0
    for i in range(12):  # realistic per-segment rounding: 22.05/44.1 kHz never divide into 24 kHz
        source=tmp_path/f'line_{i}.wav'
        subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i',
            f'sine=sample_rate={44100 if i%2 else 22050}:duration={0.3137+0.071*i}','-c:a','pcm_s16le',str(source)],
            check=True,timeout=20)
        measured=validate_audio(source); span=math.ceil(measured*24-1e-6)/24
        segments += [(source,measured),(None,span-measured)]; speech+=measured; total+=span
        clips.append(tmp_path/f'clip_{i}.mp4'); still_motion_clip(still,clips[-1],span,size=(160,120))
    voice=tmp_path/'voice.wav'; assemble_audio(segments,voice)
    voice_info=probe(voice)
    assert abs(validate_audio(voice)-total)<=audio_video_tolerance(voice_info)
    assert validate_audio(voice)>=speech
    out=tmp_path/'release.mp4'; assemble(clips,out,voice)  # refuses if speech would be truncated
    assert validate_video(out,total,tolerance_s=1/24,require_audio=True)==[]


def test_d3_adhyay_one_release_binds_its_own_compiled_pilot(approved_project,monkeypatch):
    current,approval,_,recovery_path,pilot_path=policy_fixture(approved_project,monkeypatch)
    first=load_bundle(approved_project,current.models,1)
    receipt_path=approved_project.benchmarks_dir/'synthetic-C.json'; receipt=read_json(receipt_path)
    receipt.update(accepted=True,outcome='pass'); atomic_write_json(receipt_path,receipt)
    approval=copy.deepcopy(approval)
    approval.update(adhyay=1,flf_decision='go',input_sha256=sha256_obj(snapshot(first)))
    next(r for r in approval['pilot_receipts'] if r['path']==receipt_path.name)['sha256']=sha256_file(receipt_path)
    path=approved_project.root/'approvals'/'adhyay_01.json'; atomic_write_json(path,approval)
    assert production_problems(first)==[]
    plan=read_json(pilot_path); plan['title_note']='edited after approval'
    atomic_write_json(pilot_path,plan); approval['pilot_plan']['sha256']=sha256_file(pilot_path)
    atomic_write_json(path,approval)
    problems=production_problems(first)
    assert len(problems)==1 and 'current compiled pilot manifest' in problems[0],problems


@pytest.mark.parametrize('change,reason',[
    ('copied_outside_tasks','mr_video has no valid scheduler task receipt'),
    ('swapped_languages','hi_video is not the assemble_hi release'),
    ('same_store','must come from different scheduler stores'),
    ('never_resumed','resumed recovery store has no resumed task'),
    ('clean_reused_work','clean recovery store reused earlier work'),
    ('different_task','come from different tasks: hi_video')])
def test_m1_recovery_needs_distinct_real_scheduler_runs(approved_project,monkeypatch,change,reason):
    current,approval,approval_path,recovery_path,_=policy_fixture(approved_project,monkeypatch)
    evidence=read_json(recovery_path); artifacts=approved_project.artifacts_dir
    clean,resumed=evidence['clean_outputs'],evidence['resumed_outputs']
    if change=='copied_outside_tasks':
        # Byte-identical copies with correct hashes but no scheduler provenance.
        for run,record in (('clean',clean['mr_video']),('resumed',resumed['mr_video'])):
            target=artifacts/'copies'/run/'x'/'mr.mp4'; target.parent.mkdir(parents=True)
            target.write_bytes((artifacts/record['path']).read_bytes())
            record['path']=target.relative_to(artifacts).as_posix()
    elif change=='swapped_languages':
        for run in (clean,resumed): run['mr_video'],run['hi_video']=run['hi_video'],run['mr_video']
    elif change=='same_store':
        # Distinct files, but both "runs" sealed in the clean store.
        store=artifacts/'recovery'/'clean'; tasks=recovery_tasks(variant='second')
        Scheduler(store).run(tasks); evidence['resumed_outputs']=recovery_outputs(approved_project,store,tasks)
    elif change=='never_resumed':
        store=artifacts/'recovery'/'fresh'; Scheduler(store).run(recovery_tasks())
        evidence['resumed_outputs']=recovery_outputs(approved_project,store,recovery_tasks())
    elif change=='clean_reused_work':
        store=artifacts/'recovery'/'rerun'; Scheduler(store).run(recovery_tasks(interrupt='hi')); Scheduler(store).run(recovery_tasks())
        evidence['clean_outputs']=recovery_outputs(approved_project,store,recovery_tasks())
    else:
        store=artifacts/'recovery'/'other'; tasks=recovery_tasks(variant='other')
        Scheduler(store).run(tasks); Scheduler(store).run(tasks)
        evidence['resumed_outputs']=recovery_outputs(approved_project,store,tasks)
    rewrite_recovery(approved_project,approval,approval_path,recovery_path,evidence)
    problems=production_problems(current)
    assert len(problems)==1 and reason in problems[0],problems
