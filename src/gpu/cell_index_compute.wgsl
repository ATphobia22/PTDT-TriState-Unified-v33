// Rule 1: HEC-RAS WSE is absolute truth; depth is derived presentation.
// Rule 14: All vertical calculations represent NAVD88.

struct Params {
    map_size: vec2<u32>,
    nodata_cell: u32,
    nodata_wse_mm: i32,
}

@group(0) @binding(0) var dem_tex: texture_2d<f32>;
@group(0) @binding(1) var cell_index_map: texture_2d<u32>;
@group(0) @binding(2) var<storage, read> wse_mm: array<i32>;
@group(0) @binding(3) var depth_out: texture_storage_2d<r32float, write>;
@group(0) @binding(4) var<uniform> params: Params;

@compute @workgroup_size(16, 16, 1)
fn main(@builtin(global_invocation_id) gid: vec3<u32>) {
    if (gid.x >= params.map_size.x || gid.y >= params.map_size.y) {
        return;
    }
    let coord = vec2<i32>(i32(gid.x), i32(gid.y));
    let dem_val = textureLoad(dem_tex, coord, 0).r;
    let cell_val = textureLoad(cell_index_map, coord, 0).r;
    var depth: f32 = 0.0;
    if (cell_val != params.nodata_cell) {
        let mm = wse_mm[cell_val];
        if (mm > params.nodata_wse_mm) {
            let wse_ft = f32(mm) * 0.001;
            depth = max(wse_ft - dem_val, 0.0);
        }
    }
    textureStore(depth_out, coord, vec4<f32>(depth, 0.0, 0.0, 1.0));
}
