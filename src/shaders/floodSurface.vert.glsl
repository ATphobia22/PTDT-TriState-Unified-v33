#version 300 es
in vec2 a_pos;
uniform mat4 u_matrix;
uniform float u_time;
uniform float u_depthScale;
uniform sampler2D u_depthTex;
out float v_depth;
out vec2 v_uv;
void main() {
  v_uv = a_pos * 0.5 + 0.5;
  float wave = sin(a_pos.x * 12.0 + u_time * 1.8) * 0.015 + cos(a_pos.y * 9.0 + u_time * 1.3) * 0.012;
  float depth = texture(u_depthTex, v_uv).r * u_depthScale;
  v_depth = depth;
  vec4 pos = vec4(a_pos, wave * depth, 1.0);
  gl_Position = u_matrix * pos;
}
