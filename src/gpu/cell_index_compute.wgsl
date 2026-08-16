// Rule 1: HEC-RAS WSE is absolute truth; depth is derived presentation.
// Rule 14: All vertical calculations represent NAVD88 (feet on DEM / WSE path).
// Optimizations: early outs, storage array bounds, finite DEM guard, coalesced loads.

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

fn is_finite_f32(v: f32) -> bool {
    // WGSL has no isNan/isInf; NaN != NaN; reject extreme magnitudes.
    return (v == v) && (abs(v) < 1e30);
}

@compute @workgroup_size(16, 16, 1)
fn main(@builtin(global_invocation_id) gid: vec3<u32>) {
    // Early discard outside grid (minimizes divergent texture stores).
    if (gid.x >= params.map_size.x || gid.y >= params.map_size.y) {
        return;
    }

    let coord = vec2<i32>(i32(gid.x), i32(gid.y));

    // Coalesced loads within 16x16 workgroup for adjacent pixels.
    let dem_val = textureLoad(dem_tex, coord, 0).r;
    let cell_val = textureLoad(cell_index_map, coord, 0).r;

    var depth: f32 = 0.0;

    // Nodata cell or non-finite DEM → dry (depth 0).
    if (cell_val != params.nodata_cell && is_finite_f32(dem_val)) {
        // Bounds-check unstructured WSE array (prevents OOB on bad rasterize).
        let n = arrayLength(&wse_mm);
        if (cell_val < n) {
            let mm = wse_mm[cell_val];
            // nodata_wse_mm is typically -9999; only positive/valid mm produce depth.
            if (mm > params.nodata_wse_mm) {
                let wse_ft = f32(mm) * 0.001;
                depth = max(wse_ft - dem_val, 0.0);
            }
        }
    }

    textureStore(depth_out, coord, vec4<f32>(depth, 0.0, 0.0, 1.0));
}
