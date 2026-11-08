#!/usr/bin/env python3
"""
Git Koi - A 100% self-contained, malware-free generative pixel-art Koi for GitHub profiles.
Written in pure Python + Pillow. Zero untrusted dependencies, zero external binaries.
"""

import argparse
import json
import math
import os
import subprocess
import sys
import urllib.request
from PIL import Image, ImageDraw

# GitHub Official Language Color Palette
GITHUB_LANG_COLORS = {
    'go': '#00ADD8',
    'python': '#3572A5',
    'typescript': '#3178C6',
    'javascript': '#F1E05A',
    'rust': '#DEA584',
    'c++': '#F34B7D',
    'c': '#555555',
    'c#': '#178600',
    'java': '#B07219',
    'swift': '#F05138',
    'kotlin': '#A97BFF',
    'ruby': '#701516',
    'html': '#E34C26',
    'css': '#563D7C',
    'shell': '#89E051',
    'php': '#4F5D95',
    'dart': '#00B4AB',
    'vue': '#41B883',
}

# Authentic Japanese Nishikigoi Presets
THEMES = {
    'kohaku': {
        'name': 'Kohaku (Red on White)',
        'primary': '#E63946',
        'secondary': '#E63946',
        'accent': '#E63946',
    },
    'sanke': {
        'name': 'Taisho Sanke (White, Red & Sumi Black)',
        'primary': '#E63946',
        'secondary': '#E63946',
        'accent': '#1E2028',
    },
    'showa': {
        'name': 'Showa Sanshoku (Black Base with Red & White)',
        'primary': '#1E2028',
        'secondary': '#E63946',
        'accent': '#E63946',
    },
    'asagi': {
        'name': 'Asagi (Indigo/Cyan Scale with Red Belly)',
        'primary': '#00ADD8',
        'secondary': '#E63946',
        'accent': '#1E2028',
    },
    'yamabuki': {
        'name': 'Yamabuki Ogon (Golden Yellow)',
        'primary': '#F4A261',
        'secondary': '#E76F51',
        'accent': '#E9C46A',
    },
}

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def fetch_github_user_info(username):
    """
    Safely query GitHub public API or local `gh` CLI.
    Zero external tools or untrusted libraries.
    """
    languages = []
    
    # Try using authenticated `gh` CLI if available locally
    try:
        proc = subprocess.run(
            ['gh', 'api', 'user/repos', '--paginate', '--jq', '.[].language'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5
        )
        if proc.returncode == 0 and proc.stdout.strip():
            counts = {}
            for line in proc.stdout.strip().splitlines():
                line = line.strip()
                if line and line != 'null':
                    counts[line] = counts.get(line, 0) + 1
            if counts:
                languages = [k for k, _ in sorted(counts.items(), key=lambda x: x[1], reverse=True)]
    except Exception:
        pass
        
    # If gh not available or returned empty, use public unauthenticated API
    if not languages and username:
        try:
            url = f"https://api.github.com/users/{username}/repos?per_page=100"
            req = urllib.request.Request(url, headers={'User-Agent': 'Git-Koi-Custom'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                repos = json.loads(resp.read().decode())
                counts = {}
                for r in repos:
                    l = r.get('language')
                    if l:
                        counts[l] = counts.get(l, 0) + 1
                if counts:
                    languages = [k for k, _ in sorted(counts.items(), key=lambda x: x[1], reverse=True)]
        except Exception:
            pass
            
    if not languages:
        languages = ['Go', 'TypeScript', 'Swift']
        
    return languages

class GitKoiRenderer:
    def __init__(self, username="namanmdave", languages=None, streak_days=14,
                 theme="auto", primary_color=None, secondary_color=None,
                 show_badge=True, bg_mode="pond", scale=1):
        self.username = username
        self.languages = languages or ["Go", "TypeScript", "Swift"]
        self.streak_days = streak_days
        self.show_badge = show_badge
        self.bg_mode = bg_mode
        self.scale = max(1, int(scale))
        
        # Color resolution
        if theme in THEMES:
            t = THEMES[theme]
            self.primary_rgb = hex_to_rgb(t['primary'])
            self.secondary_rgb = hex_to_rgb(t['secondary'])
            self.sumi_black = hex_to_rgb(t['accent'])
        else:
            # Auto from languages
            l1 = self.languages[0].lower() if self.languages else 'go'
            l2 = self.languages[1].lower() if len(self.languages) > 1 else 'typescript'
            p_hex = primary_color or GITHUB_LANG_COLORS.get(l1, '#00ADD8')
            s_hex = secondary_color or GITHUB_LANG_COLORS.get(l2, '#3178C6')
            self.primary_rgb = hex_to_rgb(p_hex)
            self.secondary_rgb = hex_to_rgb(s_hex)
            self.sumi_black = (30, 32, 40)
            
        self.shiraji_white = (248, 250, 252) # Porcelain white body
        self.belly_shadow = (205, 215, 228)  # Subtle shadow
        self.fin_body = (235, 245, 255, 185) # Translucent fin
        self.fin_ray = (180, 205, 230, 220)  # Delicate fin rays
        self.outline = (18, 22, 30)

    def render_frame(self, frame_idx, total_frames=36, width=320, height=200):
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 1. Background
        if self.bg_mode == "pond":
            for y in range(height):
                prog = y / height
                r = int(8 + prog * 4)
                g = int(16 + prog * 8)
                b = int(26 + prog * 12)
                draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        elif self.bg_mode == "dark":
            draw.rectangle([(0, 0), (width, height)], fill=(13, 17, 23, 255))
        elif self.bg_mode == "light":
            draw.rectangle([(0, 0), (width, height)], fill=(246, 248, 250, 255))
            
        # 2. Ambient Pond Accents (Water Ripples, Lily Pad & Sakura Petals)
        t_norm = frame_idx / total_frames
        t_rad = t_norm * 2 * math.pi
        
        if self.bg_mode != "transparent":
            # Subtle expanding ripples
            ripples = [(70, 50, 0.0), (250, 150, 0.5)]
            for rx, ry, off in ripples:
                r_prog = (t_norm + off) % 1.0
                rad_x = int(8 + r_prog * 40)
                rad_y = int(4 + r_prog * 20)
                alpha = int(35 * (1.0 - r_prog))
                if alpha > 0:
                    draw.ellipse([(rx - rad_x, ry - rad_y), (rx + rad_x, ry + rad_y)],
                                 outline=(65, 110, 155, alpha), width=1)

            # Drifting Sakura Petals
            petals = [
                (45 + math.sin(t_rad) * 4, 30 + t_norm * 18),
                (280 + math.cos(t_rad) * 5, 95 + t_norm * 14),
            ]
            for px, py in petals:
                draw.ellipse([(px - 3, py - 2), (px + 3, py + 2)], fill=(255, 185, 200, 220))
                draw.point((int(px), int(py)), fill=(255, 235, 242, 255))

            # Floating Water Lily Pad
            lx, ly = 275, 40
            draw.pieslice([(lx - 18, ly - 11), (lx + 18, ly + 11)], start=40, end=330,
                          fill=(28, 65, 38, 235), outline=(16, 40, 24, 255))
            draw.line([(lx, ly), (lx + 14, ly - 6)], fill=(16, 40, 24, 255), width=1)
            draw.ellipse([(lx - 3, ly - 3), (lx + 3, ly + 3)], fill=(255, 180, 195, 240))

        # 3. Kinematic Circular Orbit Spine
        cx, cy = width // 2, height // 2 - 5
        R = 52.0             # Swimming orbit radius
        total_len = 84.0     # Fixed arc-length of fish
        num_joints = 70
        tail_beats = 3       # Strokes per orbit
        
        def get_radius(s):
            if s < 0.12:
                return 3.5 + 8.5 * math.sqrt(s / 0.12)
            elif s < 0.40:
                norm = (s - 0.12) / 0.28
                return 12.0 + 1.2 * math.sin(norm * math.pi)
            elif s < 0.82:
                norm = (s - 0.40) / 0.42
                return 12.5 - 9.0 * norm
            else:
                norm = (s - 0.82) / 0.18
                return 3.5 - 1.5 * norm

        head_theta = t_norm * 2 * math.pi
        spine = []
        tangent_angles = []
        
        for j in range(num_joints):
            s = j / (num_joints - 1)
            arc_dist = s * total_len
            theta_j = head_theta - (arc_dist / R)
            
            # Radial swimming undulation
            sway_phase = (tail_beats * 2 * math.pi * t_norm) - (s * 3.2 * math.pi)
            sway_amp = (s ** 1.35) * 8.0
            r_j = R + sway_amp * math.sin(sway_phase)
            
            jx = cx + r_j * math.cos(theta_j)
            jy = cy + r_j * math.sin(theta_j)
            spine.append((jx, jy))
            tangent_angles.append(theta_j + math.pi / 2)
            
        normals = []
        for i in range(num_joints):
            if i == 0:
                dx = spine[1][0] - spine[0][0]
                dy = spine[1][1] - spine[0][1]
            elif i == num_joints - 1:
                dx = spine[-1][0] - spine[-2][0]
                dy = spine[-1][1] - spine[-2][1]
            else:
                dx = spine[i+1][0] - spine[i-1][0]
                dy = spine[i+1][1] - spine[i-1][1]
            dist = math.hypot(dx, dy) or 1.0
            normals.append((-dy / dist, dx / dist))

        # 4. Translucent Paddle Pectoral Fins
        pec_idx = int(num_joints * 0.20)
        px, py = spine[pec_idx]
        p_nx, p_ny = normals[pec_idx]
        p_ang = tangent_angles[pec_idx]
        p_rad = get_radius(0.20)
        fin_beat = math.sin(tail_beats * 2 * math.pi * t_norm - 0.4) * 0.35

        for side in [-1, 1]:
            bx = px + p_nx * side * (p_rad - 1.0)
            by = py + p_ny * side * (p_rad - 1.0)
            base_dir = p_ang - math.pi + side * 1.05 + fin_beat * side
            fan_len = 19.0
            
            p_lead = (bx + math.cos(base_dir - side * 0.45) * (fan_len * 0.70),
                      by + math.sin(base_dir - side * 0.45) * (fan_len * 0.70))
            p_tip = (bx + math.cos(base_dir - side * 0.15) * fan_len,
                     by + math.sin(base_dir - side * 0.15) * fan_len)
            p_mid = (bx + math.cos(base_dir + side * 0.25) * (fan_len * 0.95),
                     by + math.sin(base_dir + side * 0.25) * (fan_len * 0.95))
            p_trail = (bx + math.cos(base_dir + side * 0.55) * (fan_len * 0.65),
                       by + math.sin(base_dir + side * 0.55) * (fan_len * 0.65))
                       
            paddle_poly = [(int(bx), int(by)), (int(p_lead[0]), int(p_lead[1])),
                           (int(p_tip[0]), int(p_tip[1])), (int(p_mid[0]), int(p_mid[1])),
                           (int(p_trail[0]), int(p_trail[1]))]
            draw.polygon(paddle_poly, fill=self.fin_body, outline=self.fin_ray)
            draw.line([(int(bx), int(by)), (int(p_tip[0]), int(p_tip[1]))], fill=self.fin_ray, width=1)
            draw.line([(int(bx), int(by)), (int(p_mid[0]), int(p_mid[1]))], fill=self.fin_ray, width=1)

        # 5. Translucent Double-Lobed Tail (Caudal) Fin
        tx, ty = spine[-1]
        tail_dir = math.atan2(spine[-1][1] - spine[-2][1], spine[-1][0] - spine[-2][0])
        t_nx, t_ny = normals[-1]
        t_flutter = math.sin(tail_beats * 2 * math.pi * t_norm - 2.8) * 3.0
        
        t_len = 26.0
        tip_u1 = (tx + math.cos(tail_dir) * (t_len * 0.85) + t_nx * (12 + t_flutter),
                  ty + math.sin(tail_dir) * (t_len * 0.85) + t_ny * (12 + t_flutter))
        tip_u2 = (tx + math.cos(tail_dir) * t_len + t_nx * (9 + t_flutter),
                  ty + math.sin(tail_dir) * t_len + t_nx * (9 + t_flutter))
        tip_notch = (tx + math.cos(tail_dir) * (t_len * 0.58) + t_nx * t_flutter * 0.5,
                     ty + math.sin(tail_dir) * (t_len * 0.58) + t_ny * t_flutter * 0.5)
        tip_d2 = (tx + math.cos(tail_dir) * t_len - t_nx * (9 - t_flutter),
                  ty + math.sin(tail_dir) * t_len - t_ny * (9 - t_flutter))
        tip_d1 = (tx + math.cos(tail_dir) * (t_len * 0.85) - t_nx * (12 - t_flutter),
                  ty + math.sin(tail_dir) * (t_len * 0.85) - t_ny * (12 - t_flutter))

        tail_poly = [(int(tx), int(ty)),
                     (int(tip_u1[0]), int(tip_u1[1])),
                     (int(tip_u2[0]), int(tip_u2[1])),
                     (int(tip_notch[0]), int(tip_notch[1])),
                     (int(tip_d2[0]), int(tip_d2[1])),
                     (int(tip_d1[0]), int(tip_d1[1]))]
        draw.polygon(tail_poly, fill=self.fin_body, outline=self.fin_ray)
        draw.line([(int(tx), int(ty)), (int(tip_u2[0]), int(tip_u2[1]))], fill=self.fin_ray, width=1)
        draw.line([(int(tx), int(ty)), (int(tip_notch[0]), int(tip_notch[1]))], fill=self.fin_ray, width=1)
        draw.line([(int(tx), int(ty)), (int(tip_d2[0]), int(tip_d2[1]))], fill=self.fin_ray, width=1)

        # 6. Solid Body Rendering
        # Outline
        for i in reversed(range(num_joints)):
            s = i / (num_joints - 1)
            r = get_radius(s)
            sx, sy = spine[i]
            draw.ellipse([sx - r - 1.0, sy - r - 1.0, sx + r + 1.0, sy + r + 1.0], fill=self.outline)

        # Porcelain White Base
        for i in reversed(range(num_joints)):
            s = i / (num_joints - 1)
            r = get_radius(s)
            sx, sy = spine[i]
            draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=self.shiraji_white)

        # Underbelly Shadow
        for i in reversed(range(num_joints)):
            s = i / (num_joints - 1)
            r = get_radius(s)
            sx, sy = spine[i]
            nx, ny = normals[i]
            draw.ellipse([sx - nx * 1.5 - r * 0.85, sy - ny * 1.5 - r * 0.85,
                          sx - nx * 1.5 + r * 0.85, sy - ny * 1.5 + r * 0.85],
                         fill=self.belly_shadow)

        # 7. Authentic Nishikigoi Pattern Patches
        # Patch 1: Head Crown
        for i in range(int(num_joints * 0.04), int(num_joints * 0.18)):
            s = i / (num_joints - 1)
            r = get_radius(s) * 0.72
            sx, sy = spine[i]
            draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=self.primary_rgb)

        # Patch 2: Mid-torso Island
        for i in range(int(num_joints * 0.25), int(num_joints * 0.44)):
            s = i / (num_joints - 1)
            r = get_radius(s) * 0.80
            sx, sy = spine[i]
            nx, ny = normals[i]
            draw.ellipse([sx + nx * 2 - r, sy + ny * 2 - r, sx + nx * 2 + r, sy + ny * 2 + r], fill=self.primary_rgb)

        # Patch 3: Accent Spot
        for i in range(int(num_joints * 0.35), int(num_joints * 0.52)):
            s = i / (num_joints - 1)
            r = get_radius(s) * 0.58
            sx, sy = spine[i]
            nx, ny = normals[i]
            draw.ellipse([sx - nx * 3 - r, sy - ny * 3 - r, sx - nx * 3 + r, sy - ny * 3 + r], fill=self.secondary_rgb)

        # Patch 4: Tail Step
        for i in range(int(num_joints * 0.60), int(num_joints * 0.74)):
            s = i / (num_joints - 1)
            r = get_radius(s) * 0.70
            sx, sy = spine[i]
            draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=self.primary_rgb)

        for i in range(int(num_joints * 0.70), int(num_joints * 0.82)):
            s = i / (num_joints - 1)
            r = get_radius(s) * 0.55
            sx, sy = spine[i]
            nx, ny = normals[i]
            draw.ellipse([sx + nx * 1.5 - r, sy + ny * 1.5 - r, sx + nx * 1.5 + r, sy + ny * 1.5 + r], fill=self.sumi_black)

        # Dorsal Ridge Pearls
        for i in range(int(num_joints * 0.16), int(num_joints * 0.78), 3):
            sx, sy = spine[i]
            draw.point((int(sx), int(sy)), fill=(255, 255, 255, 180))

        # Eyes
        eye_idx = int(num_joints * 0.08)
        ex, ey = spine[eye_idx]
        enx, eny = normals[eye_idx]
        er = get_radius(0.08) * 0.85
        for side in [-1, 1]:
            ecx = ex + enx * side * er
            ecy = ey + eny * side * er
            draw.ellipse([ecx - 2, ecy - 2, ecx + 2, ecy + 2], fill=(18, 22, 28))
            draw.point((int(ecx), int(ecy - 1)), fill=(255, 255, 255))

        # Snout Whiskers (Barbels)
        hx, hy = spine[0]
        hnx, hny = normals[0]
        hang = tangent_angles[0]
        for side in [-1, 1]:
            wbx = hx + hnx * side * 2.5
            wby = hy + hny * side * 2.5
            wtx = wbx + math.cos(hang) * 5.0 + hnx * side * 3.5
            wty = wby + math.sin(hang) * 5.0 + hny * side * 3.5
            draw.line([(int(wbx), int(wby)), (int(wtx), int(wty))], fill=(240, 245, 255, 220), width=1)

        # 8. Profile Stats Banner (Clean ASCII, No Missing Glyph Boxes)
        if self.show_badge and self.bg_mode != "transparent":
            banner_y = height - 24
            draw.rectangle([(8, banner_y), (width - 8, height - 6)],
                           fill=(13, 19, 30, 230), outline=(42, 54, 76, 220))
            
            lang_str = ", ".join(self.languages[:3])
            banner_text = f"@{self.username}  |  {lang_str}  |  {self.streak_days}d streak"
            draw.text((16, banner_y + 4), banner_text, fill=(185, 210, 235, 255))
            
            # Color Legend Dots
            draw.ellipse([width - 23, banner_y + 7, width - 17, banner_y + 13], fill=self.primary_rgb)
            draw.ellipse([width - 34, banner_y + 7, width - 28, banner_y + 13], fill=self.secondary_rgb)

        return img

    def generate(self, output_path, total_frames=36, fps=15):
        frames = []
        for t in range(total_frames):
            frame = self.render_frame(t, total_frames=total_frames)
            
            # Optional Retina scale
            if self.scale > 1:
                frame = frame.resize((frame.width * self.scale, frame.height * self.scale),
                                     resample=Image.Resampling.NEAREST)
                
            if self.bg_mode == "transparent":
                alpha = frame.split()[3]
                p_frame = frame.convert('RGB').convert('P', palette=Image.Palette.ADAPTIVE, colors=255)
                mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
                p_frame.paste(255, mask)
                p_frame.info['transparency'] = 255
                frames.append(p_frame)
            else:
                frames.append(frame.convert('RGB').convert('P', palette=Image.Palette.ADAPTIVE, colors=256))
                
        duration_ms = int(1000 / fps)
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration_ms,
            loop=0,
            disposal=2
        )
        print(f"✨ Successfully generated Koi: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Git Koi - Generative Pixel-Art Koi for GitHub Profiles")
    parser.add_argument("--username", type=str, default="namanmdave", help="GitHub username")
    parser.add_argument("--languages", type=str, default=None, help="Comma-separated languages (e.g. 'Go,TypeScript,Python')")
    parser.add_argument("--theme", type=str, default="auto", choices=["auto", "kohaku", "sanke", "showa", "asagi", "yamabuki"], help="Koi color theme")
    parser.add_argument("--primary", type=str, default=None, help="Custom hex color for primary patch (e.g. '#00ADD8')")
    parser.add_argument("--secondary", type=str, default=None, help="Custom hex color for secondary patch (e.g. '#E63946')")
    parser.add_argument("--bg", type=str, default="pond", choices=["pond", "dark", "light", "transparent"], help="Background style")
    parser.add_argument("--streak", type=int, default=14, help="Activity streak in days")
    parser.add_argument("--scale", type=int, default=1, help="Scale factor (1 for 320x200, 2 for 640x400)")
    parser.add_argument("--no-badge", action="store_true", help="Hide bottom stats bar")
    parser.add_argument("--output", type=str, default="koi.gif", help="Output GIF path")
    args = parser.parse_args()

    # Determine languages
    if args.languages:
        langs = [l.strip() for l in args.languages.split(",") if l.strip()]
    else:
        print(f"Fetching GitHub activity for @{args.username}...")
        langs = fetch_github_user_info(args.username)
        print(f"Detected languages: {', '.join(langs)}")

    koi = GitKoiRenderer(
        username=args.username,
        languages=langs,
        streak_days=args.streak,
        theme=args.theme,
        primary_color=args.primary,
        secondary_color=args.secondary,
        show_badge=not args.no_badge,
        bg_mode=args.bg,
        scale=args.scale
    )
    koi.generate(args.output)

if __name__ == "__main__":
    main()
