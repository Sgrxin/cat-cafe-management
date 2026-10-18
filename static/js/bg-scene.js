/* 喵屋猫咖 · WebGL 流动渐变背景（unicorn.studio 风格，本地实现，断网可用） */
(function () {
  var canvas = document.getElementById('bgScene');
  if (!canvas) return;
  var gl = canvas.getContext('webgl', { alpha: false, antialias: false, powerPreference: 'low-power' });
  if (!gl) { canvas.style.display = 'none'; return; } // 退回 CSS 光斑

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var VERT = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  var FRAG = [
    'precision mediump float;',
    'uniform vec2 uRes;uniform float uTime;uniform vec2 uMouse;',
    'float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
    'float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);',
    ' return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}',
    'float fbm(vec2 p){float v=0.,a=.5;',
    ' for(int i=0;i<4;i++){v+=a*noise(p);p=p*2.03+vec2(17.3,9.1);a*=.5;}return v;}',
    'void main(){',
    ' vec2 uv=gl_FragCoord.xy/uRes;',
    ' float asp=uRes.x/uRes.y;',
    ' vec2 p=uv*vec2(asp,1.);',
    ' float t=uTime*.045;',
    ' p+=(uMouse-.5)*vec2(.08,.05);', // 鼠标视差
    ' vec2 q=p+.38*vec2(fbm(p*1.35+t),fbm(p*1.35-t*.8));', // 域扭曲
    ' vec3 cream=vec3(.986,.968,.937);',
    ' vec3 rose =vec3(.937,.800,.773);',
    ' vec3 caramel=vec3(.914,.624,.322);',
    ' vec3 lav =vec3(.878,.839,.953);',
    ' float n1=fbm(q*1.7+vec2(t*.55,-t*.35));',
    ' float n2=fbm(q*2.5-vec2(t*.4,t*.6));',
    ' float n3=fbm(q*1.1+vec2(-t*.3,t*.5));',
    ' vec3 col=cream;',
    ' col=mix(col,rose,smoothstep(.36,.85,n1)*.7);',
    ' col=mix(col,caramel,smoothstep(.55,.95,n2)*.42);',
    ' col=mix(col,lav,smoothstep(.6,1.,n3)*.36);',
    ' float m=exp(-length((uv-uMouse)*vec2(1.5,1.))*2.4);', // 鼠标柔光
    ' col+=caramel*m*.10;',
    ' float vig=smoothstep(1.25,.35,length(uv-.5)*1.35);', // 暗角
    ' col*=mix(.94,1.,vig);',
    ' float g=hash(uv*uRes.xy+fract(uTime));', // 胶片颗粒
    ' col+=(g-.5)*.016;',
    ' gl_FragColor=vec4(col,1.);',
    '}'
  ].join('\n');

  function compile(type, src) {
    var s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) { canvas.style.display = 'none'; return null; }
    return s;
  }
  var vs = compile(gl.VERTEX_SHADER, VERT), fs = compile(gl.FRAGMENT_SHADER, FRAG);
  if (!vs || !fs) return;
  var prog = gl.createProgram();
  gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) { canvas.style.display = 'none'; return; }
  gl.useProgram(prog);
  var buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  var loc = gl.getAttribLocation(prog, 'p');
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  var uRes = gl.getUniformLocation(prog, 'uRes');
  var uTime = gl.getUniformLocation(prog, 'uTime');
  var uMouse = gl.getUniformLocation(prog, 'uMouse');

  var SCALE = 0.6; // 低分辨率渲染，渐变本来就柔和，省一半以上算力
  function resize() {
    var w = Math.max(2, Math.floor(innerWidth * SCALE));
    var h = Math.max(2, Math.floor(innerHeight * SCALE));
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w; canvas.height = h;
      gl.viewport(0, 0, w, h);
    }
    gl.uniform2f(uRes, w, h);
  }
  resize();
  addEventListener('resize', resize);

  var mx = 0.5, my = 0.45, tx = 0.5, ty = 0.45;
  addEventListener('pointermove', function (e) {
    tx = e.clientX / innerWidth;
    ty = 1 - e.clientY / innerHeight;
  }, { passive: true });

  var t0 = performance.now(), hidden = false;
  document.addEventListener('visibilitychange', function () {
    hidden = document.hidden;
  });

  function frame(now) {
    if (hidden) { requestAnimationFrame(frame); return; }
    mx += (tx - mx) * 0.04;
    my += (ty - my) * 0.04;
    gl.uniform1f(uTime, reduced ? 12.0 : (now - t0) / 1000);
    gl.uniform2f(uMouse, mx, my);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    if (!reduced) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
