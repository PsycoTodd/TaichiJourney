import taichi as ti
import math

# ti.init(debug=True, arch=ti.cpu)
ti.init(arch=ti.opengl)

def vec(*xs):
  return ti.Vector(list(xs))

def mix(x, y, a):
    return x * (1.0 - a) + y * a

GUI_TITLE = "Fire"
w, h = wh = (640, 480) # GUI size
pixels = ti.Vector(3, dt=ti.f32, shape=wh)
iResolution = vec(w, h)

@ti.func
def noise(p):
    i = ti.floor(p)
    a = i.dot(vec(1.0, 57.0, 21.0)) + vec(0.0, 57.0, 21.0, 78.0)
    f = ti.cos((p - i) * math.acos(-1.0)) * (-0.5) + 0.5
    a = mix(ti.sin(ti.cos(a) * a), ti.sin(ti.cos(1.0 + a) * (1.0 + a)), f[0])
    a[0] = mix(a[0], a[1], f[1])
    a[1] = mix(a[2], a[3], f[1])
    return mix(a[0], a[1], f[2]) 

@ti.func
def sphere(p, spr):
    spr_xyz = vec(spr[0], spr[1], spr[2])
    w = spr[3]
    return (spr_xyz - p).norm() - w

@ti.func
def flame(p, t):
    d = sphere(p * vec(1.0, 0.5, 1.0), vec(0.0, -1.0, 0.0, 1.0))
    return d + (noise(p + vec(0.0, t * 2.0, 0.0)) + noise(p * 3.0) * 0.5) * 0.25 * (p[1])

@ti.func
def scene(p, t):
    return min(100.0 - p.norm(), abs(flame(p, t)))

@ti.func
def raymarch(org, dir, t):
    d = 0.0
    glow = 0.0
    eps = 0.02
    p = org
    glowed = False
    for i in range(64):
        d = scene(p, t) + eps
        p += d * dir
        if( d > eps):
            if(flame(p, t) < 0.0):
                glowed = True
            if(glowed):
                glow = float(i) / 64.0
    return vec(p[0], p[1], p[2], glow)

@ti.func
def mainImage(iTime, i, j):
    fragCoord = vec(i, j)

    # Normalized pixel coordinates (from 0 to 1)
    uv = fragCoord / iResolution

    v = -1.0 + 2.0 * uv
    
    org = vec(0.0, -2.0, 4.0)
    dir = vec(v[0] * 1.6, -v[1], -1.5)
    dir /= dir.norm()

    p = raymarch(org, dir, iTime)
    glow = p[3]
    
    col = mix(vec(1.0, 0.5, 0.1, 1.0), vec(0.1, 0.5, 1.0, 1.0), p[1] * 0.02 + 0.4)

    # Output to screen
    fragColor = mix(vec(0.0, 0.0, 0.0, 0.0), col, pow(glow * 2.0, 4.0))
    return fragColor

@ti.kernel
def render(t: ti.f32):
    "render ??????? mainImage ????"
    for i, j in pixels:
        col4 = mainImage(t, i, j)
        pixels[i, j] = vec(col4[0], col4[1], col4[2])

    return

def main(output_img=False):
    "output_img: ??????"
    gui = ti.GUI(GUI_TITLE, res=wh)
    for ts in range(1000000):
        if gui.get_event(ti.GUI.ESCAPE):
            exit()
        
        render(ts * 0.03)
        gui.set_image(pixels.to_numpy())
        if output_img:
          
            gui.show(f'{ts:04d}.png')
        else:
            gui.show()

if __name__ == '__main__':
    main(output_img=False)