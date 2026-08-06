#version 300 es
precision highp float;

in float v_depth;
in vec2 v_uv;
in vec3 v_worldPos;

uniform float u_time;
uniform vec3 u_cameraPos;
uniform sampler2D u_depthTex;

out vec4 fragColor;

void main() {
  float d = v_depth;
  if (d < 0.02) discard;

  vec3 shallow = vec3(0.20, 0.72, 0.95);
  vec3 mid     = vec3(0.08, 0.38, 0.72);
  vec3 deep    = vec3(0.03, 0.14, 0.38);

  float t = smoothstep(0.0, 4.0, d);
  vec3 col = mix(shallow, mid, t);
  col = mix(col, deep, smoothstep(1.5, 5.0, d));

  float foam = pow(1.0 - smoothstep(0.0, 0.55, d), 2.2);
  col = mix(col, vec3(0.92, 0.97, 1.0), foam * 0.65);

  float sparkle =
      sin(v_uv.x * 48.0 + u_time * 3.2) *
      cos(v_uv.y * 41.0 + u_time * 2.7) * 0.09;
  col += sparkle * (1.0 - foam) * smoothstep(0.1, 1.0, d);

  vec3 viewDir = normalize(u_cameraPos - v_worldPos);
  float fresnel = pow(1.0 - max(dot(viewDir, vec3(0.0, 1.0, 0.0)), 0.0), 3.0);
  col = mix(col, vec3(0.7, 0.85, 1.0), fresnel * 0.25);

  float alpha = smoothstep(0.0, 0.35, d) * 0.82;
  fragColor = vec4(col, alpha);
}
