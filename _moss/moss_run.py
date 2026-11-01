import subprocess, sys, json, os, time
def sh(c): print(c, flush=True); subprocess.run(c, shell=True, check=True)
sh("pip install -q git+https://github.com/OpenMOSS/MOSS-TTS.git 2>&1 | tail -3 || true")
sh("git clone -q https://github.com/OpenMOSS/MOSS-TTS.git /tmp/MOSS-TTS && pip install -q -e /tmp/MOSS-TTS 2>&1 | tail -3")
sh("pip install -q transformers==5.0.0 safetensors==0.6.2 accelerate bitsandbytes 2>&1 | tail -2")
import torch, torchaudio
from transformers import AutoModel, AutoProcessor
repo = "OpenMOSS-Team/MOSS-SoundEffect"
prompts = json.loads('[["a1_bed_roadside_quiet", "soft wind and a faint, distant village on a dusty road"], ["a1_bed_courtyard_feast_murmur", "low murmur of a household feast, far off"], ["a1_bed_village_noon_heat", "hot still noon: faint wind, a far-off bird, nothing else"], ["a1_bed_village_morning", "soft early-day village ambience (unused so far; growth)"], ["a1_bed_interior_quiet", "quiet house interior (unused so far; growth)"], ["a1_bed_well_and_cattle", "a well-side place with cattle shuffling far off (unused so far; growth)"], ["a1_fx_leaf_plate_rustle", "dry leaf plates being moved"], ["a1_fx_footsteps_road_dust", "two people walking on a dusty road"], ["a1_fx_cloth_bow_rustle", "soft cloth rustle of a respectful bow"], ["a1_fx_plate_set_down", "a leaf plate set down on the ground"], ["a1_fx_birds_flutter_to_trees", "birds flutter and settle in trees"], ["a1_fx_door_wood_creak", "a wooden door opening, someone stepping in"], ["a1_fx_cattle_distant", "cattle drinking and shuffling at a trough"], ["a1_fx_water_trough_drink", "water lapping at a trough"], ["a1_fx_brass_pot_clink", "a brass pot (gadva) carried and set down"], ["a1_fx_wind_rush_run", "a rush of wind as someone runs away"], ["a1_fx_gourd_hollow_tap", "a dry gourd tapped (unused so far; growth)"], ["a1_fx_well_rope_bucket", "a rope and bucket at a well (unused so far; growth)"], ["a1_fx_distant_crowd_murmur", "a small distant crowd (unused so far; growth)"], ["a1_fx_wind_gust_soft", "a soft gust of wind (unused so far; growth)"], ["a1_fx_cow_bell_distant", "a distant cow bell (unused so far; growth)"], ["a1_fx_sandal_steps_stone", "sandals on a stone floor (unused so far; growth)"], ["a2_bed_S1_S1-L1", "A very subtle, low-frequency ambient drone with a faint temple bell resonance, creating a sacred atmosphere without melody."], ["a2_bed_S2_S2-L1", "Quiet Indian town morning: distant temple bells, birds, light footfalls on dusty road, no traffic"], ["a2_fx_S2_S2-L3", "Ethereal low drone with faint chant \'Gan Gan Ganat Bote\' barely audible, spatialized"], ["a2_bed_S2_S2-L5", "Walking on dirt lanes, occasional door creak, distant cow lowing, warm breeze"], ["a2_fx_S2_S2-L7", "Wooden door latch lift, heavy door swing, soft thud close"], ["a2_bed_S2_S2-L9", "Quiet room with faint oil lamp crackle, slow breathing"], ["a2_fx_S2_S2-L11", "Firm steps on stone threshold, fading into outdoor ambience"], ["a2_bed_S2_S2-L12", "Afternoon stillness, distant pigeon coo, rustle of dry leaves"], ["a2_fx_S2_S2-L14", "Soft resonant bell tone, single strike, reverberant"], ["a2_fx_S2_S2-L16", "Gentle inhale-exhale, subtle heartbeat"], ["a2_bed_S2_S2-L17", "Time-lapse soundscape: birds morning, cicadas noon, crickets evening, repeated four times"], ["a2_bed_S3_S3-L1", "Outdoor Hindu temple courtyard ambience: gentle breeze, distant birds, low murmur of devotees gathering, subtle temple bell"], ["a2_bed_S3_S3-L3", "Group of people walking on dirt path, shuffling feet, quiet chatter, anticipation"], ["a2_fx_S3_S3-L4", "Single person walking briskly on dry dirt path, light footfalls"], ["a2_fx_S3_S3-L6", "Soft musical sting or subtle chime to mark divine revelation"], ["a2_fx_S3_S3-L7", "Two pairs of feet running on stone pavement, urgent but not chaotic"], ["a2_fx_S3_S3-L10", "Quiet temple background, faint rustle of cloth"], ["a2_fx_S3_S3-L11", "Soft clink of metal bowl, rustle of flatbread, gentle contact of hands"], ["a2_bed_S4_S4-L1", "Gentle ambient sound of a Hindu temple courtyard: distant bells, faint chanting, light breeze."], ["a2_fx_S4_S4-L3", "A soft intake of breath, quiet rustle of cloth."], ["a2_fx_S4_S4-L5", "A low, resonant tone underscoring authority."], ["a2_bed_S4_S4-L6", "Gentle trickle of shallow water over stones, occasional bird call."], ["a2_fx_S4_S4-L8", "A gentle plop as a gourd touches water surface, small splash."], ["a2_fx_S4_S4-L9", "A mystical, rising hum as the stream bed deepens, water rushing into the hollow."]]')
proc = AutoProcessor.from_pretrained(repo, trust_remote_code=True)
t0 = time.time()
dm = {"emb_ext": 0, "lm_heads": 0, "language_model.embed_tokens": 0, "language_model.rotary_emb": 0, "language_model.norm": 0}
for i in range(36): dm[f"language_model.layers.{i}"] = 0 if i < 12 else 1
model = AutoModel.from_pretrained(repo, trust_remote_code=True, dtype=torch.float16, device_map=dm).eval()
dev = str(next(model.parameters()).device)
import traceback
proc.audio_tokenizer = proc.audio_tokenizer.to(dev)
print("load s", round(time.time()-t0), "gpus", torch.cuda.device_count(), flush=True)
os.makedirs("out", exist_ok=True)
log = []
for name, p in prompts:
    t = time.time()
    try:
        b = proc([[proc.build_user_message(ambient_sound=p, tokens=100)]], mode="generation")
        with torch.no_grad():
            o = model.generate(input_ids=b["input_ids"].to(dev), attention_mask=b["attention_mask"].to(dev), max_new_tokens=4096)
        a = proc.decode(o)[0].audio_codes_list[0]
        torchaudio.save(f"out/{name}.wav", a.unsqueeze(0).cpu().float(), proc.model_config.sampling_rate)
        log.append((name, round(time.time()-t, 1), "ok"))
    except Exception as e:
        if not any("ERR" in x[2] for x in log): traceback.print_exc()
        log.append((name, round(time.time()-t, 1), "ERR " + str(e)[:200]))
    print(log[-1], flush=True)
json.dump(log, open("out/log.json", "w"))
