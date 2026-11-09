#!/usr/bin/env python3
"""
Git Goku - 90-Day Saiyan Streak Evolution Engine (Toriyama Enhanced Edition)
100% self-contained, pure Python + Pillow. Zero malware, zero untrusted binaries.

Evolves Goku across 12 canonical Dragon Ball forms based on continuous commit streak:
0-3d   : Base Form
4-7d   : Powered Up (White Ki)
8-14d  : Kaio-ken (界王拳)
15-24d : Super Saiyan (SSJ1)
25-34d : Super Saiyan 2 (SSJ2 + Lightning)
35-44d : Super Saiyan 3 (SSJ3 + Flowing Golden Hair)
45-54d : Super Saiyan 4 (SSJ4 + Crimson Fur & Tail)
55-64d : Super Saiyan God (SSG + Ruby Divine Flame)
65-74d : Super Saiyan Blue (SSB + Cyan Divine Ki)
75-84d : SSB Kaio-ken x20 (Dual Layer Cyan + Crimson Fire)
85-89d : Ultra Instinct -Sign- (Silver-Edged Hair & Heat Haze)
90d+   : Mastered Ultra Instinct (Pure Celestial Silver God of Combat)
"""

import argparse
import json
import math
import os
import random
import subprocess
import sys
import urllib.request
from PIL import Image, ImageDraw

def hex_to_rgb(hex_str):
    if not hex_str:
        return (0, 0, 0)
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

GOKU_FORMS = [
    {
        'id': 'base',
        'name': 'Base Form',
        'min_days': 0,
        'max_days': 3,
        'hair_color': '#16161C',
        'hair_high': '#3A4254',
        'hair_style': 'base',
        'aura_type': None,
        'shirt_color': '#E86100',
        'undershirt': '#1A237E',
        'eye_color': '#16161C',
        'sparks': False,
    },
    {
        'id': 'aura',
        'name': 'Powered Up (White Ki)',
        'min_days': 4,
        'max_days': 7,
        'hair_color': '#16161C',
        'hair_high': '#3A4254',
        'hair_style': 'base',
        'aura_type': 'single',
        'aura_inner': '#FFFFFF',
        'aura_outer': '#CFD8DC',
        'shirt_color': '#E86100',
        'undershirt': '#1A237E',
        'eye_color': '#16161C',
        'sparks': False,
    },
    {
        'id': 'kaioken',
        'name': 'Kaio-ken',
        'min_days': 8,
        'max_days': 14,
        'hair_color': '#3A0E16',
        'hair_high': '#7A1C2E',
        'hair_style': 'base',
        'aura_type': 'single',
        'aura_inner': '#FF1744',
        'aura_outer': '#B71C1C',
        'shirt_color': '#FF5722',
        'undershirt': '#261438',
        'eye_color': '#16161C',
        'sparks': False,
    },
    {
        'id': 'ssj1',
        'name': 'Super Saiyan',
        'min_days': 15,
        'max_days': 24,
        'hair_color': '#FFEE58',
        'hair_high': '#FFFDE7',
        'hair_shad': '#F57F17',
        'hair_style': 'ssj',
        'aura_type': 'single',
        'aura_inner': '#FFFDE7',
        'aura_outer': '#FBC02D',
        'shirt_color': '#FFA726',
        'undershirt': '#283593',
        'eye_color': '#00E5FF',
        'sparks': False,
    },
    {
        'id': 'ssj2',
        'name': 'Super Saiyan 2',
        'min_days': 25,
        'max_days': 34,
        'hair_color': '#FFFF8D',
        'hair_high': '#FFFFFF',
        'hair_shad': '#FBC02D',
        'hair_style': 'ssj2',
        'aura_type': 'single',
        'aura_inner': '#FFFFFF',
        'aura_outer': '#FBC02D',
        'shirt_color': '#FFA726',
        'undershirt': '#283593',
        'eye_color': '#00E5FF',
        'sparks': True,
        'spark_color': '#80D8FF',
    },
    {
        'id': 'ssj3',
        'name': 'Super Saiyan 3',
        'min_days': 35,
        'max_days': 44,
        'hair_color': '#FFD54F',
        'hair_high': '#FFF9C4',
        'hair_shad': '#F57F17',
        'hair_style': 'ssj3',
        'aura_type': 'single',
        'aura_inner': '#FFF9C4',
        'aura_outer': '#F57F17',
        'shirt_color': '#FF9800',
        'undershirt': '#1A237E',
        'eye_color': '#00E5FF',
        'sparks': True,
        'spark_color': '#80D8FF',
        'eyebrows': False,
    },
    {
        'id': 'ssj4',
        'name': 'Super Saiyan 4',
        'min_days': 45,
        'max_days': 54,
        'hair_color': '#111115',
        'hair_high': '#3A4254',
        'hair_style': 'ssj4',
        'body_fur': '#D50000',
        'aura_type': 'single',
        'aura_inner': '#FFE082',
        'aura_outer': '#FF6F00',
        'shirt_color': None,
        'pants_color': '#FFEE58',
        'eye_color': '#FFD600',
        'sparks': True,
        'spark_color': '#FFD600',
    },
    {
        'id': 'ssg',
        'name': 'Super Saiyan God',
        'min_days': 55,
        'max_days': 64,
        'hair_color': '#FF1744',
        'hair_high': '#FF8A80',
        'hair_style': 'base',
        'aura_type': 'single',
        'aura_inner': '#FF8A80',
        'aura_outer': '#C62828',
        'shirt_color': '#E86100',
        'undershirt': '#1A237E',
        'eye_color': '#FF1744',
        'sparks': False,
    },
    {
        'id': 'ssb',
        'name': 'Super Saiyan Blue',
        'min_days': 65,
        'max_days': 74,
        'hair_color': '#00E5FF',
        'hair_high': '#E0F7FA',
        'hair_shad': '#0288D1',
        'hair_style': 'ssj',
        'aura_type': 'single',
        'aura_inner': '#E0F7FA',
        'aura_outer': '#0288D1',
        'shirt_color': '#E86100',
        'undershirt': '#1A237E',
        'eye_color': '#00E5FF',
        'sparks': True,
        'spark_color': '#E0F7FA',
    },
    {
        'id': 'ssb_kaioken',
        'name': 'SSB Kaio-ken (x20)',
        'min_days': 75,
        'max_days': 84,
        'hair_color': '#00E5FF',
        'hair_high': '#E0F7FA',
        'hair_shad': '#0288D1',
        'hair_style': 'ssj',
        'aura_type': 'dual',
        'aura_inner': '#E0F7FA',
        'aura_mid': '#00E5FF',
        'aura_outer': '#FF1744',
        'shirt_color': '#FF5722',
        'undershirt': '#311B92',
        'eye_color': '#00E5FF',
        'sparks': True,
        'spark_color': '#FF80AB',
    },
    {
        'id': 'ui_sign',
        'name': 'Ultra Instinct -Sign-',
        'min_days': 85,
        'max_days': 89,
        'hair_color': '#212121',
        'hair_high': '#B0BEC5',
        'hair_style': 'base',
        'aura_type': 'single',
        'aura_inner': '#FFFFFF',
        'aura_outer': '#90CAF9',
        'shirt_color': '#E86100',
        'undershirt': '#1A237E',
        'eye_color': '#CFD8DC',
        'sparks': False,
    },
    {
        'id': 'mui',
        'name': 'Mastered Ultra Instinct',
        'min_days': 90,
        'max_days': 9999,
        'hair_color': '#FFFFFF',
        'hair_high': '#FFFFFF',
        'hair_shad': '#B0BEC5',
        'hair_style': 'ssj_silver',
        'aura_type': 'single',
        'aura_inner': '#FFFFFF',
        'aura_outer': '#B0BEC5',
        'shirt_color': '#E86100',
        'undershirt': '#1A237E',
        'eye_color': '#FFFFFF',
        'sparks': True,
        'spark_color': '#E1F5FE',
    },
]

def get_form_by_streak(days):
    for f in GOKU_FORMS:
        if f['min_days'] <= days <= f['max_days']:
            return f
    return GOKU_FORMS[-1]

def fetch_github_streak(username):
    try:
        query = '''query($u: String!) {
          user(login: $u) {
            contributionsCollection {
              contributionCalendar {
                weeks {
                  contributionDays {
                    date
                    contributionCount
                  }
                }
              }
            }
          }
        }'''
        cmd = ['gh', 'api', 'graphql', '-f', f'query={query}', '-F', f'u={username}']
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=8)
        if res.returncode == 0:
            data = json.loads(res.stdout)
            weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
            days = [d for w in weeks for d in w['contributionDays']]
            if days:
                return calculate_streak_from_days(days)
    except Exception:
        pass

    token = os.environ.get("GITHUB_TOKEN")
    if token and username:
        try:
            req_data = json.dumps({"query": query, "variables": {"u": username}}).encode("utf-8")
            req = urllib.request.Request(
                "https://api.github.com/graphql",
                data=req_data,
                headers={"Authorization": f"bearer {token}", "User-Agent": "Git-Goku"}
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())
                weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
                days = [d for w in weeks for d in w['contributionDays']]
                if days:
                    return calculate_streak_from_days(days)
        except Exception:
            pass

    return 1

def calculate_streak_from_days(days):
    streak = 0
    rev = list(reversed(days))
    if not rev:
        return 0
    idx = 0
    if rev[0]['contributionCount'] == 0:
        idx = 1
    while idx < len(rev) and rev[idx]['contributionCount'] > 0:
        streak += 1
        idx += 1
    return max(1, streak)

class GitGokuRenderer:
    def __init__(self, streak_days=1, username="namanmdave", force_form_id=None, scale=1):
        self.streak_days = max(0, int(streak_days))
        self.username = username
        self.scale = max(1, int(scale))
        
        if force_form_id:
            match = [f for f in GOKU_FORMS if f['id'] == force_form_id]
            self.form = match[0] if match else get_form_by_streak(self.streak_days)
        else:
            self.form = get_form_by_streak(self.streak_days)
            
        # Shaded Color Palettes
        self.skin_high = (254, 230, 196)
        self.skin_base = (247, 186, 123)
        self.skin_shad = (199, 124, 66)
        self.skin_dark = (130, 68, 30)

        self.gi_high = (255, 175, 45)
        self.gi_base = hex_to_rgb(self.form['shirt_color']) if self.form['shirt_color'] else (244, 81, 30)
        self.gi_shad = (185, 50, 10)
        self.gi_deep = (110, 24, 5)

        self.blue_high = (63, 81, 181)
        self.blue_base = hex_to_rgb(self.form.get('undershirt', '#1A237E'))
        self.blue_shad = (13, 19, 61)

        self.hair_col = hex_to_rgb(self.form['hair_color'])
        self.hair_high = hex_to_rgb(self.form.get('hair_high', '#3A4254'))
        self.hair_shad = hex_to_rgb(self.form.get('hair_shad', '#0A0A0E'))
        self.eye_color = hex_to_rgb(self.form['eye_color'])
        self.outline = (22, 18, 24)

    def render_flame_spire(self, draw, cx, ground_y, base_w, height, phase, color, lick_freq=3.0, lick_amp=5.0):
        steps = 22
        pts_left = []
        pts_right = []
        tip_y = ground_y - height
        
        for i in range(steps):
            s = i / (steps - 1)
            y = ground_y - s * height
            w_factor = math.sin(s * math.pi * 0.72) if s < 0.72 else (1.0 - s) / 0.28
            flicker = math.sin(phase * lick_freq - s * 12.0) * (lick_amp * s)
            w = max(1.0, base_w * w_factor)
            pts_left.append((cx - w + flicker, y))
            pts_right.append((cx + w + flicker, y))
            
        pts = pts_left + [(cx + math.sin(phase * lick_freq - 12.0) * lick_amp, tip_y)] + list(reversed(pts_right))
        pts.append((cx - base_w, ground_y))
        draw.polygon([(int(x), int(y)) for x, y in pts], fill=color)

    def render_aura(self, draw, cx, cy, t_norm):
        a_type = self.form.get('aura_type')
        if not a_type:
            return
            
        phase = t_norm * 2 * math.pi
        ground_y = cy + 50
        
        if a_type == 'single':
            inner_col = hex_to_rgb(self.form['aura_inner'])
            outer_col = hex_to_rgb(self.form['aura_outer'])
            
            # Layer 1: Outer Shell
            self.render_flame_spire(draw, cx, ground_y, 48, 116, phase, outer_col + (85,), lick_freq=4.0, lick_amp=7.0)
            self.render_flame_spire(draw, cx - 22, ground_y - 4, 34, 90, phase + 1.2, outer_col + (100,), lick_freq=5.0, lick_amp=6.0)
            self.render_flame_spire(draw, cx + 22, ground_y - 4, 34, 90, phase + 2.4, outer_col + (100,), lick_freq=5.0, lick_amp=6.0)
            
            # Layer 2: Mid Core
            self.render_flame_spire(draw, cx, ground_y - 2, 36, 100, phase + 0.5, inner_col + (160,), lick_freq=4.5, lick_amp=5.0)
            self.render_flame_spire(draw, cx - 18, ground_y - 6, 24, 78, phase + 1.8, inner_col + (150,), lick_freq=5.5, lick_amp=4.0)
            self.render_flame_spire(draw, cx + 18, ground_y - 6, 24, 78, phase + 3.0, inner_col + (150,), lick_freq=5.5, lick_amp=4.0)
            
            # Layer 3: Blazing Hot Core
            self.render_flame_spire(draw, cx, ground_y - 4, 22, 85, phase + 1.0, (255, 255, 255, 210), lick_freq=6.0, lick_amp=3.5)

        elif a_type == 'dual':
            outer_red = hex_to_rgb(self.form['aura_outer'])
            mid_cyan = hex_to_rgb(self.form['aura_mid'])
            inner_white = hex_to_rgb(self.form['aura_inner'])
            
            self.render_flame_spire(draw, cx, ground_y, 54, 124, phase, outer_red + (100,), lick_freq=4.2, lick_amp=8.0)
            self.render_flame_spire(draw, cx - 24, ground_y - 4, 38, 96, phase + 1.2, outer_red + (110,), lick_freq=5.2, lick_amp=7.0)
            self.render_flame_spire(draw, cx + 24, ground_y - 4, 38, 96, phase + 2.4, outer_red + (110,), lick_freq=5.2, lick_amp=7.0)
            
            self.render_flame_spire(draw, cx, ground_y - 2, 36, 100, phase + 0.6, mid_cyan + (180,), lick_freq=4.8, lick_amp=5.0)
            self.render_flame_spire(draw, cx - 17, ground_y - 6, 24, 78, phase + 1.9, mid_cyan + (170,), lick_freq=5.6, lick_amp=4.0)
            self.render_flame_spire(draw, cx + 17, ground_y - 6, 24, 78, phase + 3.1, mid_cyan + (170,), lick_freq=5.6, lick_amp=4.0)
            
            self.render_flame_spire(draw, cx, ground_y - 4, 22, 84, phase + 1.1, inner_white + (220,), lick_freq=6.2, lick_amp=3.5)

        # Rising Spark Embers
        part_col = hex_to_rgb(self.form.get('aura_inner', '#FFFFFF'))
        random.seed(int(t_norm * 600) // 50)
        for i in range(16):
            prog = (t_norm * 2.2 + i * 0.18) % 1.0
            sy = ground_y - prog * 115
            sx = cx + (math.sin(phase * 2.0 + i) * 36.0 * (1.0 - prog * 0.5))
            sz = 1 if i % 3 != 0 else 2
            alpha = int(240 * (1.0 - prog))
            draw.ellipse([sx - sz, sy - sz, sx + sz, sy + sz], fill=part_col + (alpha,))

    def render_sparks(self, draw, cx, cy, t_norm):
        if not self.form.get('sparks'):
            return
            
        spark_color = hex_to_rgb(self.form.get('spark_color', '#80D8FF'))
        step_bucket = int(t_norm * 14)
        random.seed(step_bucket * 7919)
        
        for _ in range(random.randint(2, 3)):
            ang = random.uniform(0, 2 * math.pi)
            rad_start = random.uniform(14, 28)
            rad_end = rad_start + random.uniform(16, 32)
            
            x0 = cx + math.cos(ang) * rad_start
            y0 = cy + math.sin(ang) * rad_start - 8
            x3 = cx + math.cos(ang + random.uniform(-0.5, 0.5)) * rad_end
            y3 = cy + math.sin(ang) * rad_end - 8
            
            x1 = (x0 * 2 + x3) / 3 + random.uniform(-6, 6)
            y1 = (y0 * 2 + y3) / 3 + random.uniform(-6, 6)
            x2 = (x0 + x3 * 2) / 3 + random.uniform(-6, 6)
            y2 = (y0 + y3 * 2) / 3 + random.uniform(-6, 6)
            
            pts = [(int(x0), int(y0)), (int(x1), int(y1)), (int(x2), int(y2)), (int(x3), int(y3))]
            draw.line(pts, fill=spark_color + (255,), width=1)
            draw.point(pts[1], fill=(255, 255, 255, 255))
            draw.point(pts[2], fill=(255, 255, 255, 255))

    def render_goku(self, draw, cx, cy, t_norm):
        """Authentic Toriyama Character Engine with volume, shading and signature features"""
        breath_y = int(math.sin(t_norm * 2 * math.pi) * 1.2)
        # Power vibration shake if aura is blazing
        shake_x = random.choice([-1, 0, 1]) if self.form.get('aura_type') else 0
        gx = cx + shake_x
        gy = cy + breath_y

        h_style = self.form['hair_style']

        # -------------------------------------------------------------
        # 1. LAYER A: Back Hair & Tail (Behind Body)
        # -------------------------------------------------------------
        if h_style == 'ssj3':
            # SSJ3 Epic Golden Cape Hair flowing down past knees
            ssj3_cape = [
                (gx - 12, gy - 26),
                (gx - 28, gy - 42),
                (gx - 8, gy - 54),
                (gx + 8, gy - 54),
                (gx + 28, gy - 42),
                (gx + 12, gy - 26),
                (gx + 30, gy + 15),
                (gx + 25, gy + 42),
                (gx + 14, gy + 46),
                (gx - 14, gy + 46),
                (gx - 25, gy + 42),
                (gx - 30, gy + 15),
            ]
            draw.polygon(ssj3_cape, fill=self.hair_col, outline=self.outline)
            draw.line([(gx - 18, gy - 16), (gx - 18, gy + 38)], fill=self.hair_high, width=1)
            draw.line([(gx + 18, gy - 16), (gx + 18, gy + 38)], fill=self.hair_high, width=1)
            draw.line([(gx - 8, gy + 8), (gx - 8, gy + 42)], fill=self.hair_shad, width=1)
            draw.line([(gx + 8, gy + 8), (gx + 8, gy + 42)], fill=self.hair_shad, width=1)
            
        elif h_style == 'ssj4':
            # SSJ4 Back Mane
            mane = [
                (gx - 10, gy - 26),
                (gx - 24, gy - 42),
                (gx, gy - 50),
                (gx + 24, gy - 42),
                (gx + 10, gy - 26),
                (gx + 25, gy + 18),
                (gx - 25, gy + 18),
            ]
            draw.polygon(mane, fill=self.hair_col, outline=self.outline)
            tail_phase = t_norm * 2 * math.pi
            tail_tip_x = gx + 28 + math.sin(tail_phase) * 6
            tail_pts = [(gx + 12, gy + 16), (gx + 22, gy + 18), (int(tail_tip_x), gy + 8), (int(tail_tip_x - 3), gy + 4)]
            draw.line(tail_pts, fill=(139, 69, 19), width=3)

        # -------------------------------------------------------------
        # 2. LAYER B: Boots & Feet
        # -------------------------------------------------------------
        # Left boot
        draw.polygon([(gx - 18, cy + 44), (gx - 28, cy + 50), (gx - 16, cy + 52), (gx - 12, cy + 46)], fill=self.blue_base, outline=self.outline)
        draw.line([(gx - 24, cy + 49), (gx - 16, cy + 51)], fill=(225, 35, 35), width=1)
        draw.polygon([(gx - 28, cy + 50), (gx - 20, cy + 51), (gx - 22, cy + 52), (gx - 28, cy + 52)], fill=(255, 215, 0))

        # Right boot
        draw.polygon([(gx + 12, cy + 46), (gx + 16, cy + 52), (gx + 28, cy + 50), (gx + 18, cy + 44)], fill=self.blue_base, outline=self.outline)
        draw.line([(gx + 16, cy + 51), (gx + 24, cy + 49)], fill=(225, 35, 35), width=1)
        draw.polygon([(gx + 20, cy + 51), (gx + 28, cy + 50), (gx + 28, cy + 52), (gx + 22, cy + 52)], fill=(255, 215, 0))

        # -------------------------------------------------------------
        # 3. LAYER C: Pants & Belt
        # -------------------------------------------------------------
        pants_col = hex_to_rgb(self.form.get('pants_color', '#E86100')) if self.form.get('pants_color') else self.gi_base
        pants_pts = [
            (gx - 15, gy + 14),
            (gx - 23, gy + 28),
            (gx - 17, cy + 44),
            (gx - 8, cy + 44),
            (gx, gy + 26),
            (gx + 8, cy + 44),
            (gx + 17, cy + 44),
            (gx + 23, gy + 28),
            (gx + 15, gy + 14),
        ]
        draw.polygon(pants_pts, fill=pants_col, outline=self.outline)
        draw.polygon([(gx - 18, gy + 22), (gx - 13, gy + 20), (gx - 15, gy + 32)], fill=self.gi_high)
        draw.polygon([(gx + 13, gy + 20), (gx + 18, gy + 22), (gx + 15, gy + 32)], fill=self.gi_high)
        draw.line([(gx - 12, gy + 24), (gx - 7, gy + 38)], fill=self.gi_shad, width=1)
        draw.line([(gx + 12, gy + 24), (gx + 7, gy + 38)], fill=self.gi_shad, width=1)
        draw.line([(gx - 20, gy + 28), (gx - 16, gy + 40)], fill=self.gi_deep, width=1)
        draw.line([(gx + 20, gy + 28), (gx + 16, gy + 40)], fill=self.gi_deep, width=1)

        # Sash Belt
        draw.rectangle([(gx - 15, gy + 10), (gx + 15, gy + 14)], fill=self.blue_base, outline=self.outline)
        draw.polygon([(gx - 5, gy + 14), (gx - 9, gy + 26), (gx - 4, gy + 28), (gx - 2, gy + 14)], fill=self.blue_shad, outline=self.outline)
        draw.polygon([(gx - 3, gy + 14), (gx - 6, gy + 23), (gx - 2, gy + 24), (gx - 1, gy + 14)], fill=self.blue_high)

        # -------------------------------------------------------------
        # 4. LAYER D: Torso & Gi Top
        # -------------------------------------------------------------
        if self.form.get('body_fur'):
            fur_col = hex_to_rgb(self.form['body_fur'])
            torso_pts = [(gx - 17, gy - 12), (gx + 17, gy - 12), (gx + 14, gy + 10), (gx - 14, gy + 10)]
            draw.polygon(torso_pts, fill=fur_col, outline=self.outline)
            draw.polygon([(gx - 7, gy - 7), (gx + 7, gy - 7), (gx + 4, gy + 4), (gx, gy + 8), (gx - 4, gy + 4)],
                         fill=self.skin_base, outline=self.skin_shad)
        else:
            torso_pts = [(gx - 17, gy - 12), (gx + 17, gy - 12), (gx + 14, gy + 10), (gx - 14, gy + 10)]
            draw.polygon(torso_pts, fill=self.gi_base, outline=self.outline)
            draw.polygon([(gx - 17, gy - 12), (gx - 11, gy - 12), (gx - 13, gy + 5), (gx - 16, gy + 5)], fill=self.gi_shad)
            draw.polygon([(gx + 11, gy - 12), (gx + 17, gy - 12), (gx + 16, gy + 5), (gx + 13, gy + 5)], fill=self.gi_shad)

            # Navy Undershirt
            draw.polygon([(gx - 9, gy - 12), (gx + 9, gy - 12), (gx, gy - 1)], fill=self.blue_base, outline=self.outline)
            draw.line([(gx - 8, gy - 11), (gx, gy - 2)], fill=self.blue_high, width=1)
            # Neck skin & muscle
            draw.polygon([(gx - 4, gy - 12), (gx + 4, gy - 12), (gx, gy - 5)], fill=self.skin_base)
            draw.line([(gx - 2, gy - 8), (gx + 2, gy - 8)], fill=self.skin_shad, width=1)

            # Turtle School Kanji Crest on Left Chest
            draw.ellipse([gx + 5, gy - 6, gx + 11, gy], fill=(255, 255, 255), outline=self.outline)
            draw.line([(gx + 7, gy - 4), (gx + 9, gy - 4)], fill=self.outline, width=1)
            draw.line([(gx + 8, gy - 5), (gx + 8, gy - 1)], fill=self.outline, width=1)

        # -------------------------------------------------------------
        # 5. LAYER E: Muscular Arms & Clenched Fists
        # -------------------------------------------------------------
        # Left Arm
        l_arm = [(gx - 17, gy - 10), (gx - 25, gy - 1), (gx - 24, gy + 13), (gx - 16, gy + 3)]
        draw.polygon(l_arm, fill=self.skin_base, outline=self.outline)
        draw.line([(gx - 22, gy - 2), (gx - 19, gy + 6)], fill=self.skin_shad, width=1)
        draw.rectangle([(gx - 25, gy + 8), (gx - 20, gy + 14)], fill=self.blue_base, outline=self.outline)
        draw.ellipse([gx - 26, gy + 13, gx - 19, gy + 20], fill=self.skin_base, outline=self.outline)
        draw.point((gx - 24, gy + 15), fill=self.skin_high)
        draw.point((gx - 22, gy + 18), fill=self.skin_shad)

        # Right Arm
        r_arm = [(gx + 17, gy - 10), (gx + 25, gy - 1), (gx + 24, gy + 13), (gx + 16, gy + 3)]
        draw.polygon(r_arm, fill=self.skin_base, outline=self.outline)
        draw.line([(gx + 22, gy - 2), (gx + 19, gy + 6)], fill=self.skin_shad, width=1)
        draw.rectangle([(gx + 20, gy + 8), (gx + 25, gy + 14)], fill=self.blue_base, outline=self.outline)
        draw.ellipse([gx + 19, gy + 13, gx + 26, gy + 20], fill=self.skin_base, outline=self.outline)
        draw.point((gx + 24, gy + 15), fill=self.skin_high)
        draw.point((gx + 22, gy + 18), fill=self.skin_shad)

        # -------------------------------------------------------------
        # 6. LAYER F: Head, Jaw & Eyes
        # -------------------------------------------------------------
        hcx, hcy = gx, gy - 18
        # Muscular Neck
        draw.polygon([(gx - 4, gy - 12), (gx + 4, gy - 12), (gx + 3, hcy + 5), (gx - 3, hcy + 5)], fill=self.skin_base, outline=self.outline)
        draw.polygon([(gx - 3, gy - 12), (gx, gy - 8), (gx - 2, hcy + 6)], fill=self.skin_shad)

        # Chiseled Jawline
        jaw_pts = [
            (hcx - 7, hcy - 6),
            (hcx + 7, hcy - 6),
            (hcx + 6, hcy + 2),
            (hcx, hcy + 7),
            (hcx - 6, hcy + 2),
        ]
        draw.polygon(jaw_pts, fill=self.skin_base, outline=self.outline)
        draw.polygon([(hcx - 5, hcy + 3), (hcx, hcy + 7), (hcx + 5, hcy + 3), (hcx, hcy + 5)], fill=self.skin_shad)

        # Ears
        draw.polygon([(hcx - 8, hcy - 3), (hcx - 6, hcy - 4), (hcx - 6, hcy + 2), (hcx - 8, hcy + 1)], fill=self.skin_base, outline=self.outline)
        draw.polygon([(hcx + 6, hcy - 4), (hcx + 8, hcy - 3), (hcx + 8, hcy + 1), (hcx + 6, hcy + 2)], fill=self.skin_base, outline=self.outline)

        # Eyebrows
        if self.form.get('eyebrows') is not False:
            draw.polygon([(hcx - 7, hcy - 4), (hcx - 1, hcy - 2), (hcx - 1, hcy - 3), (hcx - 6, hcy - 5)], fill=self.hair_col)
            draw.polygon([(hcx + 1, hcy - 2), (hcx + 7, hcy - 4), (hcx + 6, hcy - 5), (hcx + 1, hcy - 3)], fill=self.hair_col)
        else:
            # SSJ3 Brow Ridge
            draw.polygon([(hcx - 6, hcy - 4), (hcx + 6, hcy - 4), (hcx + 5, hcy - 2), (hcx - 5, hcy - 2)], fill=self.skin_shad)

        # White Sclera & Sharp Pupils
        draw.polygon([(hcx - 5, hcy - 2), (hcx - 2, hcy - 2), (hcx - 2, hcy), (hcx - 5, hcy)], fill=(255, 255, 255), outline=self.outline)
        draw.polygon([(hcx + 2, hcy - 2), (hcx + 5, hcy - 2), (hcx + 5, hcy), (hcx + 2, hcy)], fill=(255, 255, 255), outline=self.outline)
        draw.point((hcx - 3, hcy - 1), fill=self.eye_color)
        draw.point((hcx + 3, hcy - 1), fill=self.eye_color)
        draw.point((hcx - 4, hcy - 2), fill=(255, 255, 255))
        draw.point((hcx + 2, hcy - 2), fill=(255, 255, 255))

        # Nose & Mouth
        draw.point((hcx, hcy + 2), fill=self.skin_dark)
        draw.line([(hcx - 2, hcy + 5), (hcx + 2, hcy + 5)], fill=self.outline, width=1)

        # -------------------------------------------------------------
        # 7. LAYER G: Signature Toriyama Hair & Bangs
        # -------------------------------------------------------------
        if h_style == 'base':
            # Skull volume
            draw.ellipse([hcx - 9, hcy - 12, hcx + 9, hcy - 3], fill=self.hair_col, outline=self.outline)
            
            # Left Major Spikes
            tuft1 = [(hcx - 6, hcy - 8), (hcx - 14, hcy - 12), (hcx - 26, hcy - 10), (hcx - 16, hcy - 4), (hcx - 8, hcy - 1)]
            draw.polygon(tuft1, fill=self.hair_col, outline=self.outline)
            draw.polygon([(hcx - 7, hcy - 7), (hcx - 15, hcy - 10), (hcx - 24, hcy - 9), (hcx - 14, hcy - 8)], fill=self.hair_high)

            tuft2 = [(hcx - 4, hcy - 10), (hcx - 12, hcy - 19), (hcx - 22, hcy - 23), (hcx - 14, hcy - 14), (hcx - 6, hcy - 9)]
            draw.polygon(tuft2, fill=self.hair_col, outline=self.outline)
            draw.polygon([(hcx - 5, hcy - 10), (hcx - 13, hcy - 17), (hcx - 20, hcy - 21), (hcx - 11, hcy - 14)], fill=self.hair_high)

            tuft3 = [(hcx - 2, hcy - 12), (hcx - 6, hcy - 24), (hcx - 10, hcy - 31), (hcx - 1, hcy - 22), (hcx + 3, hcy - 12)]
            draw.polygon(tuft3, fill=self.hair_col, outline=self.outline)
            draw.polygon([(hcx - 2, hcy - 13), (hcx - 6, hcy - 22), (hcx - 9, hcy - 28), (hcx - 4, hcy - 20)], fill=self.hair_high)

            # Right Spikes
            tuft4 = [(hcx + 2, hcy - 12), (hcx + 10, hcy - 22), (hcx + 18, hcy - 24), (hcx + 12, hcy - 14), (hcx + 6, hcy - 8)]
            draw.polygon(tuft4, fill=self.hair_col, outline=self.outline)
            draw.polygon([(hcx + 3, hcy - 11), (hcx + 9, hcy - 19), (hcx + 16, hcy - 22), (hcx + 10, hcy - 14)], fill=self.hair_high)

            tuft5 = [(hcx + 6, hcy - 7), (hcx + 15, hcy - 13), (hcx + 20, hcy - 11), (hcx + 14, hcy - 4), (hcx + 7, hcy)]
            draw.polygon(tuft5, fill=self.hair_col, outline=self.outline)
            draw.polygon([(hcx + 6, hcy - 6), (hcx + 14, hcy - 11), (hcx + 18, hcy - 10), (hcx + 12, hcy - 5)], fill=self.hair_high)

            # Forehead Bangs
            draw.polygon([(hcx - 7, hcy - 6), (hcx - 3, hcy - 1), (hcx - 1, hcy - 6)], fill=self.hair_col, outline=self.outline)
            draw.point((hcx - 4, hcy - 3), fill=self.hair_high)
            draw.polygon([(hcx - 1, hcy - 6), (hcx + 1, hcy - 3), (hcx + 2, hcy - 6)], fill=self.hair_col, outline=self.outline)
            draw.polygon([(hcx + 2, hcy - 6), (hcx + 5, hcy - 2), (hcx + 7, hcy - 6)], fill=self.hair_col, outline=self.outline)

        elif h_style in ['ssj', 'ssj2', 'ssj_silver']:
            # Upward Super Saiyan Jagged Spikes with volume
            spikes = [
                [(hcx - 7, hcy - 7), (hcx - 21, hcy - 24), (hcx - 5, hcy - 13)],
                [(hcx - 6, hcy - 12), (hcx - 16, hcy - 36), (hcx - 2, hcy - 17)],
                [(hcx - 3, hcy - 15), (hcx - 3, hcy - 42), (hcx + 4, hcy - 17)],
                [(hcx + 2, hcy - 16), (hcx + 14, hcy - 37), (hcx + 6, hcy - 11)],
                [(hcx + 5, hcy - 9), (hcx + 21, hcy - 23), (hcx + 7, hcy - 3)],
            ]
            for sp in spikes:
                draw.polygon(sp, fill=self.hair_col, outline=self.outline)
            draw.line([(hcx - 2, hcy - 38), (hcx - 1, hcy - 20)], fill=self.hair_high, width=1)
            draw.line([(hcx - 12, hcy - 32), (hcx - 6, hcy - 16)], fill=self.hair_high, width=1)
            draw.line([(hcx + 10, hcy - 33), (hcx + 5, hcy - 14)], fill=self.hair_high, width=1)
            
            if h_style == 'ssj2':
                # SSJ2 Sharp bang between eyes
                draw.polygon([(hcx - 2, hcy - 7), (hcx - 1, hcy + 4), (hcx + 1, hcy - 7)], fill=self.hair_col, outline=self.outline)
                draw.line([(hcx - 1, hcy - 6), (hcx - 1, hcy + 2)], fill=self.hair_high, width=1)
            else:
                draw.polygon([(hcx - 5, hcy - 6), (hcx - 2, hcy - 1), (hcx + 1, hcy - 6)], fill=self.hair_col, outline=self.outline)

        elif h_style == 'ssj3':
            draw.polygon([(hcx - 3, hcy - 7), (hcx - 1, hcy + 4), (hcx + 2, hcy - 7)], fill=self.hair_col, outline=self.outline)

        elif h_style == 'ssj4':
            draw.polygon([(hcx - 4, hcy - 7), (hcx - 1, hcy - 1), (hcx + 2, hcy - 7)], fill=self.hair_col, outline=self.outline)
            draw.polygon([(hcx + 1, hcy - 7), (hcx + 3, hcy - 2), (hcx + 5, hcy - 7)], fill=self.hair_col, outline=self.outline)

    def render_frame(self, frame_idx, total_frames=24, width=320, height=200):
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 1. Dark Space Dojo Background
        for y in range(height):
            prog = y / height
            draw.line([(0, y), (width, y)], fill=(int(10 + prog * 5), int(12 + prog * 6), int(22 + prog * 10), 255))
            
        t_norm = frame_idx / total_frames
        gx, gy = width // 2, height // 2 + 10

        # 2. Floating Crater Debris Stones (reacting to raw Ki)
        if self.form.get('aura_type'):
            debris_data = [
                (-50, 32, 4, 3, 0.0),
                (-28, 12, 3, 2, 0.4),
                (38, 24, 5, 4, 0.7),
                (55, 8, 3, 3, 0.2),
                (-62, -8, 3, 2, 0.8),
                (64, -4, 4, 3, 0.5),
            ]
            for rx, r_base_y, rw, rh, off in debris_data:
                prog = (t_norm * 2.0 + off) % 1.0
                float_y = (gy + r_base_y) - prog * 42
                float_x = gx + rx + math.sin(t_norm * 4.0 + rx) * 3
                draw.polygon([(float_x - rw, float_y), (float_x + rw, float_y - 2),
                              (float_x + rw - 1, float_y + rh), (float_x - rw + 1, float_y + rh)],
                             fill=(65, 75, 95), outline=(25, 30, 42))
                draw.point((int(float_x), int(float_y - 1)), fill=(115, 130, 160))

        # 3. Ground Battle Crater
        draw.ellipse([(gx - 70, gy + 48), (gx + 70, gy + 66)], fill=(16, 20, 34, 230), outline=(35, 45, 70, 200))
        draw.line([(gx - 40, gy + 57), (gx - 18, gy + 55), (gx + 12, gy + 58), (gx + 38, gy + 56)], fill=(30, 38, 55, 255), width=1)

        # 4. Multi-Spire Ki Flame Aura (Behind Goku)
        self.render_aura(draw, gx, gy, t_norm)
        
        # 5. Authentic Toriyama Goku Character Sprite
        self.render_goku(draw, gx, gy, t_norm)
        
        # 6. Crackling Lightning Sparks (In Front of Goku)
        self.render_sparks(draw, gx, gy, t_norm)
        
        # 7. Clean Saiyan HUD Banner
        banner_y = height - 26
        draw.rectangle([(8, banner_y), (width - 8, height - 6)],
                       fill=(12, 16, 28, 235), outline=(45, 60, 90, 220))
        
        hud_text = f"@{self.username}  |  Day {self.streak_days}/90  |  {self.form['name']}"
        draw.text((14, banner_y + 3), hud_text, fill=(235, 242, 255, 255))
        
        # Progress Bar towards 90 Days
        bar_x = 14
        bar_y = banner_y + 15
        bar_w = width - 28
        bar_h = 2
        draw.rectangle([(bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h)], fill=(30, 40, 60, 255))
        fill_ratio = min(1.0, max(0.01, self.streak_days / 90.0))
        fill_w = int(bar_w * fill_ratio)
        bar_col = hex_to_rgb(self.form.get('aura_inner', '#FF9800'))
        draw.rectangle([(bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h)], fill=bar_col)
        
        return img

    def generate(self, output_path, total_frames=24, fps=12):
        frames = []
        for t in range(total_frames):
            frame = self.render_frame(t, total_frames=total_frames)
            if self.scale > 1:
                frame = frame.resize((frame.width * self.scale, frame.height * self.scale), resample=Image.Resampling.NEAREST)
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
        print(f"✨ Successfully generated Toriyama Git Goku ({self.form['name']}, Day {self.streak_days}) -> {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Git Goku - Saiyan Evolution Profile Engine")
    parser.add_argument("--username", type=str, default="namanmdave", help="GitHub username")
    parser.add_argument("--streak", type=int, default=None, help="Explicit streak count")
    parser.add_argument("--form", type=str, default=None, choices=[f['id'] for f in GOKU_FORMS], help="Force a specific transformation form")
    parser.add_argument("--scale", type=int, default=1, help="Scale factor (1 for 320x200, 2 for 640x400)")
    parser.add_argument("--output", type=str, default="goku.gif", help="Output GIF path")
    args = parser.parse_args()

    streak = args.streak
    if streak is None:
        print(f"Calculating continuous active streak for @{args.username}...")
        streak = fetch_github_streak(args.username)
        print(f"Detected streak: {streak} days")

    renderer = GitGokuRenderer(
        streak_days=streak,
        username=args.username,
        force_form_id=args.form,
        scale=args.scale
    )
    renderer.generate(args.output)

if __name__ == "__main__":
    main()
