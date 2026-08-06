#version 300 es

in vec2 a_pos;

uniform mat4 u_matrix;
uniform float u_time;
uniform float u_depthScale;
uniform sampler2D u_depthTex;

out float v_depth;
out vec2 v_uv;
out vec3 v_worldPos;

void main() {
  v_uv = a_pos * 0.5 + 0.5;

  float d = texture(u_depthTex, v_uv).r * u_depthScale;
  v_depth = d;

  float wave =
      sin(a_pos.x * 11.0 + u_time * 1.7) * 0.014 * d +
      cos(a_pos.y * 8.5  + u_time * 1.25) * 0.011 * d +
      sin((a_pos.x + a_pos.y) * 6.0 + u_time * 2.1) * 0.007 * d;

  vec4 world = vec4(a_pos.x, wave, a_pos.y, 1.0);
  v_worldPos = world.xyz;
  gl_Position = u_matrix * world;
}
