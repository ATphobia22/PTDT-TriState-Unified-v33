#version 300 es
precision highp float;
in float v_depth;
in vec2 v_uv;
uniform float u_time;
out vec4 fragColor;
void main() {
  float d = v_depth;
  if (d < 0.01) discard;
  vec3 shallow = vec3(0.22, 0.74, 0.97);
  vec3 deep = vec3(0.07, 0.25, 0.55);
  vec3 col = mix(shallow, deep, smoothstep(0.0, 3.0, d));
  float foam = pow(1.0 - smoothstep(0.0, 0.4, d), 2.0);
  col = mix(col, vec3(0.95, 0.98, 1.0), foam * 0.6);
  float sparkle = sin(v_uv.x * 40.0 + u_time * 3.0) * cos(v_uv.y * 35.0 + u_time * 2.5) * 0.08;
  col += sparkle * (1.0 - foam);
  fragColor = vec4(col, smoothstep(0.0, 0.3, d) * 0.85);
}
