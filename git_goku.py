#!/usr/bin/env python3
"""
Git Goku - 90-Day Saiyan Streak Evolution Engine
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
        'kanji': '基本',
        'min_days': 0,
        'max_days': 3,
        'hair_color': '#111115',
        'hair_style': 'base',
        'aura_type': None,
        'shirt_color': '#E86100',
        'undershirt': '#1E295A',
        'eye_color': '#111115',
        'sparks': False,
    },
    {
        'id': 'aura',
        'name': 'Powered Up (White Ki)',
        'kanji': '気',
        'min_days': 4,
        'max_days': 7,
        'hair_color': '#111115',
        'hair_style': 'base',
        'aura_type': 'single',
        'aura_inner': '#FFFFFF',
        'aura_outer': '#CFD8DC',
        'shirt_color': '#E86100',
        'undershirt': '#1E295A',
        'eye_color': '#111115',
        'sparks': False,
    },
    {
        'id': 'kaioken',
        'name': 'Kaio-ken',
        'kanji': '界王拳',
        'min_days': 8,
        'max_days': 14,
        'hair_color': '#3A0E16',
        'hair_style': 'base',
        'aura_type': 'single',
        'aura_inner': '#FF1744',
        'aura_outer': '#B71C1C',
        'shirt_color': '#FF5722',
        'undershirt': '#261438',
        'eye_color': '#111115',
        'sparks': False,
    },
    {
        'id': 'ssj1',
        'name': 'Super Saiyan',
        'kanji': '超サイヤ人',
        'min_days': 15,
        'max_days': 24,
        'hair_color': '#FFF176',
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
        'kanji': '超サイヤ人2',
        'min_days': 25,
        'max_days': 34,
        'hair_color': '#FFFF8D',
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
        'kanji': '超サイヤ人3',
        'min_days': 35,
        'max_days': 44,
        'hair_color': '#FFD54F',
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
        'kanji': '超サイヤ人4',
        'min_days': 45,
        'max_days': 54,
        'hair_color': '#111115',
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
        'kanji': '超サイヤ人ゴッド',
        'min_days': 55,
        'max_days': 64,
        'hair_color': '#FF1744',
        'hair_style': 'base',
        'aura_type': 'single',
        'aura_inner': '#FF8A80',
        'aura_outer': '#C62828',
        'shirt_color': '#E86100',
        'undershirt': '#1E295A',
        'eye_color': '#FF1744',
        'sparks': False,
    },
    {
        'id': 'ssb',
        'name': 'Super Saiyan Blue',
        'kanji': '超サイヤ人ブルー',
        'min_days': 65,
        'max_days': 74,
        'hair_color': '#00E5FF',
        'hair_style': 'ssj',
        'aura_type': 'single',
        'aura_inner': '#E0F7FA',
        'aura_outer': '#0288D1',
        'shirt_color': '#E86100',
        'undershirt': '#1E295A',
        'eye_color': '#00E5FF',
        'sparks': True,
        'spark_color': '#E0F7FA',
    },
    {
        'id': 'ssb_kaioken',
        'name': 'SSB Kaio-ken (x20)',
        'kanji': 'SSGSS界王拳',
        'min_days': 75,
        'max_days': 84,
        'hair_color': '#00E5FF',
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
        'kanji': '身勝手の極意"兆"',
        'min_days': 85,
        'max_days': 89,
        'hair_color': '#212121',
        'hair_style': 'base',
        'aura_type': 'single',
        'aura_inner': '#FFFFFF',
        'aura_outer': '#90CAF9',
        'shirt_color': '#E86100',
        'undershirt': '#1E295A',
        'eye_color': '#CFD8DC',
        'sparks': False,
    },
    {
        'id': 'mui',
        'name': 'Mastered Ultra Instinct',
        'kanji': '身勝手の極意"極"',
        'min_days': 90,
        'max_days': 9999,
        'hair_color': '#FFFFFF',
        'hair_style': 'ssj_silver',
        'aura_type': 'single',
        'aura_inner': '#FFFFFF',
        'aura_outer': '#B0BEC5',
        'shirt_color': '#E86100',
        'undershirt': '#1E295A',
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

def get_next_form(current_form):
    idx = GOKU_FORMS.index(current_form)
    if idx < len(GOKU_FORMS) - 1:
        return GOKU_FORMS[idx + 1]
    return None

def fetch_github_streak(username):
    """
    Safely calculates continuous active commit streak using GraphQL or gh CLI.
    Zero external dependencies, zero secret tokens exposed.
    """
    # 1. Try gh CLI locally
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

    # 2. Try inside GitHub Actions with GITHUB_TOKEN
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

    # Fallback to default
    return 1

def calculate_streak_from_days(days):
    streak = 0
    rev = list(reversed(days))
    if not rev:
        return 0
    idx = 0
    # If today hasn't had commits yet, check starting yesterday
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
            
        self.skin_base = (252, 216, 172)
        self.skin_shadow = (220, 165, 115)
        self.gi_orange = hex_to_rgb(self.form['shirt_color']) if self.form['shirt_color'] else (232, 97, 0)
        self.gi_dark = (195, 75, 0)
        self.undershirt_blue = hex_to_rgb(self.form.get('undershirt', '#1E295A'))
        self.belt_blue = (24, 38, 95)
        self.boots_blue = (20, 32, 80)
        self.hair_color = hex_to_rgb(self.form['hair_color'])
        self.eye_color = hex_to_rgb(self.form['eye_color'])

    def render_flame_spire(self, draw, cx, ground_y, base_w, height, phase, color, lick_freq=3.0, lick_amp=5.0):
        """Draws a vertical rising flame tongue grounded at ground_y and tapering to a sharp tip"""
        steps = 20
        pts_left = []
        pts_right = []
        tip_y = ground_y - height
        
        for i in range(steps):
            s = i / (steps - 1)  # 0 at ground, 1 at tip
            y = ground_y - s * height
            w_factor = math.sin(s * math.pi * 0.72) if s < 0.72 else (1.0 - s) / 0.28
            flicker = math.sin(phase * lick_freq - s * 12.0) * (lick_amp * s)
            w = max(1.0, base_w * w_factor)
            pts_left.append((cx - w + flicker, y))
            pts_right.append((cx + w + flicker, y))
            
        pts = pts_left + [(cx + math.sin(phase * lick_freq - 12.0) * lick_amp, tip_y)] + list(reversed(pts_right))
        # Ground floor closure
        pts.append((cx - base_w, ground_y))
        draw.polygon([(int(x), int(y)) for x, y in pts], fill=color)

    def render_aura(self, draw, cx, cy, t_norm):
        """Renders authentic DBZ Multi-Spire Ki Aura"""
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
            # SSB Kaio-ken: Inner Cyan God Ki + Outer Blazing Crimson Kaio-ken Fire!
            outer_red = hex_to_rgb(self.form['aura_outer'])
            mid_cyan = hex_to_rgb(self.form['aura_mid'])
            inner_white = hex_to_rgb(self.form['aura_inner'])
            
            # Outer Crimson Flame Shell
            self.render_flame_spire(draw, cx, ground_y, 54, 124, phase, outer_red + (100,), lick_freq=4.2, lick_amp=8.0)
            self.render_flame_spire(draw, cx - 24, ground_y - 4, 38, 96, phase + 1.2, outer_red + (110,), lick_freq=5.2, lick_amp=7.0)
            self.render_flame_spire(draw, cx + 24, ground_y - 4, 38, 96, phase + 2.4, outer_red + (110,), lick_freq=5.2, lick_amp=7.0)
            
            # Inner Divine Cyan Ki
            self.render_flame_spire(draw, cx, ground_y - 2, 36, 100, phase + 0.6, mid_cyan + (180,), lick_freq=4.8, lick_amp=5.0)
            self.render_flame_spire(draw, cx - 17, ground_y - 6, 24, 78, phase + 1.9, mid_cyan + (170,), lick_freq=5.6, lick_amp=4.0)
            self.render_flame_spire(draw, cx + 17, ground_y - 6, 24, 78, phase + 3.1, mid_cyan + (170,), lick_freq=5.6, lick_amp=4.0)
            
            # Hot White Core
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
        """Crackling electrical sparks for SSJ2, SSJ3, SSJ4, SSB, MUI"""
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
        """Detailed martial arts Goku sprite with proper back/front layering"""
        breath_y = int(math.sin(t_norm * 2 * math.pi) * 1.2)
        gy = cy + breath_y
        outline = (16, 20, 28)
        
        h_style = self.form['hair_style']
        h_col = self.hair_color
        h_high = tuple(min(255, c + 40) for c in h_col)

        # 1. LAYER A: Back Hair & Tail (Drawn behind body)
        if h_style == 'ssj3':
            # SSJ3 Golden Flowing Hair flowing behind shoulders
            ssj3_cape = [
                (cx - 12, gy - 26),
                (cx - 28, gy - 42),
                (cx - 8, gy - 54),
                (cx + 8, gy - 54),
                (cx + 28, gy - 42),
                (cx + 12, gy - 26),
                (cx + 30, gy + 15),
                (cx + 25, gy + 42),
                (cx + 14, gy + 46),
                (cx - 14, gy + 46),
                (cx - 25, gy + 42),
                (cx - 30, gy + 15),
            ]
            draw.polygon(ssj3_cape, fill=h_col, outline=outline)
            draw.line([(cx - 18, gy - 16), (cx - 18, gy + 38)], fill=h_high, width=1)
            draw.line([(cx + 18, gy - 16), (cx + 18, gy + 38)], fill=h_high, width=1)
            
        elif h_style == 'ssj4':
            # SSJ4 Back Mane
            mane = [
                (cx - 10, gy - 26),
                (cx - 24, gy - 42),
                (cx, gy - 50),
                (cx + 24, gy - 42),
                (cx + 10, gy - 26),
                (cx + 25, gy + 18),
                (cx - 25, gy + 18),
            ]
            draw.polygon(mane, fill=h_col, outline=outline)
            # Swaying monkey tail
            tail_phase = t_norm * 2 * math.pi
            tail_tip_x = cx + 28 + math.sin(tail_phase) * 6
            tail_pts = [(cx + 12, gy + 16), (cx + 22, gy + 18), (int(tail_tip_x), gy + 8), (int(tail_tip_x - 3), gy + 4)]
            draw.line(tail_pts, fill=(139, 69, 19), width=3)

        # 2. LAYER B: Boots & Feet
        draw.polygon([(cx - 16, cy + 50), (cx - 24, cy + 54), (cx - 14, cy + 55), (cx - 10, cy + 51)],
                     fill=self.boots_blue, outline=outline)
        draw.polygon([(cx + 10, cy + 51), (cx + 14, cy + 55), (cx + 24, cy + 54), (cx + 16, cy + 50)],
                     fill=self.boots_blue, outline=outline)
        draw.line([(cx - 17, cy + 47), (cx - 12, cy + 53)], fill=(225, 35, 35), width=1)
        draw.line([(cx + 12, cy + 53), (cx + 17, cy + 47)], fill=(225, 35, 35), width=1)

        # 3. LAYER C: Pants & Belt
        pants_col = hex_to_rgb(self.form.get('pants_color', '#E86100')) if self.form.get('pants_color') else self.gi_orange
        pants_poly = [
            (cx - 14, gy + 16),
            (cx - 19, gy + 32),
            (cx - 15, cy + 49),
            (cx - 5, cy + 49),
            (cx, gy + 28),
            (cx + 5, cy + 49),
            (cx + 15, cy + 49),
            (cx + 19, gy + 32),
            (cx + 14, gy + 16),
        ]
        draw.polygon(pants_poly, fill=pants_col, outline=outline)
        draw.line([(cx - 12, gy + 24), (cx - 8, gy + 36)], fill=self.gi_dark, width=1)
        draw.line([(cx + 12, gy + 24), (cx + 8, gy + 36)], fill=self.gi_dark, width=1)

        # Sash Belt
        draw.rectangle([(cx - 14, gy + 12), (cx + 14, gy + 16)], fill=self.belt_blue, outline=outline)
        draw.polygon([(cx - 4, gy + 16), (cx - 8, gy + 27), (cx - 3, gy + 28), (cx - 1, gy + 16)], fill=self.belt_blue)

        # 4. LAYER D: Torso & Gi Top
        if self.form.get('body_fur'):
            fur_col = hex_to_rgb(self.form['body_fur'])
            torso_poly = [(cx - 15, gy - 10), (cx + 15, gy - 10), (cx + 13, gy + 12), (cx - 13, gy + 12)]
            draw.polygon(torso_poly, fill=fur_col, outline=outline)
            draw.polygon([(cx - 7, gy - 7), (cx + 7, gy - 7), (cx + 4, gy + 4), (cx, gy + 8), (cx - 4, gy + 4)],
                         fill=self.skin_base, outline=self.skin_shadow)
        else:
            torso_poly = [(cx - 16, gy - 11), (cx + 16, gy - 11), (cx + 13, gy + 12), (cx - 13, gy + 12)]
            draw.polygon(torso_poly, fill=self.gi_orange, outline=outline)
            draw.polygon([(cx - 8, gy - 11), (cx + 8, gy - 11), (cx, gy - 2)], fill=self.undershirt_blue)
            draw.polygon([(cx - 4, gy - 11), (cx + 4, gy - 11), (cx, gy - 6)], fill=self.skin_base)
            draw.ellipse([cx + 4, gy - 5, cx + 10, gy + 1], fill=(255, 255, 255), outline=outline)
            draw.point((cx + 7, gy - 2), fill=outline)

        # 5. LAYER E: Arms & Fists
        draw.polygon([(cx - 16, gy - 9), (cx - 24, gy + 3), (cx - 22, gy + 16), (cx - 14, gy + 2)],
                     fill=self.skin_base, outline=outline)
        draw.rectangle([(cx - 24, gy + 9), (cx - 19, gy + 15)], fill=self.belt_blue, outline=outline)
        draw.ellipse([cx - 25, gy + 14, cx - 18, gy + 21], fill=self.skin_base, outline=outline)

        draw.polygon([(cx + 16, gy - 9), (cx + 24, gy + 3), (cx + 22, gy + 16), (cx + 14, gy + 2)],
                     fill=self.skin_base, outline=outline)
        draw.rectangle([(cx + 19, gy + 9), (cx + 24, gy + 15)], fill=self.belt_blue, outline=outline)
        draw.ellipse([cx + 18, gy + 14, cx + 25, gy + 21], fill=self.skin_base, outline=outline)

        # 6. LAYER F: Head & Face
        hcx, hcy = cx, gy - 18
        draw.rectangle([(cx - 4, hcy + 4), (cx + 4, hcy + 9)], fill=self.skin_base)
        jaw_poly = [
            (hcx - 7, hcy - 7),
            (hcx + 7, hcy - 7),
            (hcx + 6, hcy + 1),
            (hcx, hcy + 6),
            (hcx - 6, hcy + 1),
        ]
        draw.polygon(jaw_poly, fill=self.skin_base, outline=outline)

        if self.form.get('eyebrows') is not False:
            eb_color = self.hair_color
            draw.line([(hcx - 6, hcy - 3), (hcx - 1, hcy - 1)], fill=eb_color, width=1)
            draw.line([(hcx + 1, hcy - 1), (hcx + 6, hcy - 3)], fill=eb_color, width=1)
        else:
            draw.line([(hcx - 6, hcy - 3), (hcx + 6, hcy - 3)], fill=self.skin_shadow, width=2)

        draw.point((hcx - 4, hcy), fill=self.eye_color)
        draw.point((hcx + 3, hcy), fill=self.eye_color)
        draw.point((hcx - 5, hcy - 1), fill=outline)
        draw.point((hcx + 4, hcy - 1), fill=outline)
        draw.point((hcx, hcy + 1), fill=self.skin_shadow)
        draw.line([(hcx - 2, hcy + 4), (hcx + 2, hcy + 4)], fill=outline, width=1)

        # 7. LAYER G: Front Hair & Bangs
        if h_style == 'base':
            draw.polygon([(hcx - 4, hcy - 6), (hcx - 22, hcy - 16), (hcx - 8, hcy - 1)], fill=h_col, outline=outline)
            draw.polygon([(hcx - 5, hcy - 8), (hcx - 19, hcy - 25), (hcx - 4, hcy - 14)], fill=h_col, outline=outline)
            draw.polygon([(hcx - 2, hcy - 12), (hcx - 10, hcy - 31), (hcx + 2, hcy - 14)], fill=h_col, outline=outline)
            draw.polygon([(hcx + 3, hcy - 12), (hcx + 15, hcy - 25), (hcx + 7, hcy - 5)], fill=h_col, outline=outline)
            draw.polygon([(hcx + 6, hcy - 6), (hcx + 18, hcy - 14), (hcx + 7, hcy + 1)], fill=h_col, outline=outline)
            draw.polygon([(hcx - 6, hcy - 7), (hcx - 2, hcy - 3), (hcx, hcy - 7)], fill=h_col)
            draw.polygon([(hcx + 1, hcy - 7), (hcx + 3, hcy - 2), (hcx + 6, hcy - 7)], fill=h_col)

        elif h_style in ['ssj', 'ssj2', 'ssj_silver']:
            spikes = [
                [(hcx - 7, hcy - 6), (hcx - 19, hcy - 22), (hcx - 5, hcy - 12)],
                [(hcx - 6, hcy - 11), (hcx - 15, hcy - 33), (hcx - 2, hcy - 16)],
                [(hcx - 3, hcy - 14), (hcx - 3, hcy - 38), (hcx + 4, hcy - 16)],
                [(hcx + 2, hcy - 15), (hcx + 13, hcy - 34), (hcx + 6, hcy - 10)],
                [(hcx + 5, hcy - 8), (hcx + 19, hcy - 21), (hcx + 7, hcy - 2)],
            ]
            for s in spikes:
                draw.polygon(s, fill=h_col, outline=outline)
            draw.line([(hcx - 2, hcy - 34), (hcx - 1, hcy - 18)], fill=h_high, width=1)
            draw.line([(hcx - 11, hcy - 29), (hcx - 5, hcy - 14)], fill=h_high, width=1)
            if h_style == 'ssj2':
                draw.polygon([(hcx - 2, hcy - 8), (hcx - 1, hcy + 3), (hcx + 1, hcy - 8)], fill=h_col, outline=outline)
            else:
                draw.polygon([(hcx - 5, hcy - 7), (hcx - 2, hcy - 2), (hcx + 1, hcy - 7)], fill=h_col)

        elif h_style == 'ssj3':
            draw.polygon([(hcx - 3, hcy - 7), (hcx - 1, hcy + 4), (hcx + 2, hcy - 7)], fill=h_col, outline=outline)

        elif h_style == 'ssj4':
            draw.polygon([(hcx - 4, hcy - 7), (hcx - 1, hcy - 1), (hcx + 2, hcy - 7)], fill=h_col, outline=outline)
            draw.polygon([(hcx + 1, hcy - 7), (hcx + 3, hcy - 2), (hcx + 5, hcy - 7)], fill=h_col, outline=outline)

    def render_frame(self, frame_idx, total_frames=24, width=320, height=200):
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 1. Dark Dojo Space Background
        for y in range(height):
            prog = y / height
            draw.line([(0, y), (width, y)], fill=(int(10 + prog * 5), int(12 + prog * 6), int(22 + prog * 10), 255))
            
        t_norm = frame_idx / total_frames
        gx, gy = width // 2, height // 2 + 10
        
        # Ground battle circle
        draw.ellipse([(gx - 65, gy + 50), (gx + 65, gy + 66)], fill=(16, 20, 32, 230), outline=(32, 42, 64, 200))
        draw.line([(gx - 35, gy + 58), (gx - 15, gy + 56), (gx + 10, gy + 59), (gx + 32, gy + 57)], fill=(28, 36, 52, 255), width=1)

        # 2. Multi-Spire Ki Flame Aura (Behind Goku)
        self.render_aura(draw, gx, gy, t_norm)
        
        # 3. Goku Character Sprite
        self.render_goku(draw, gx, gy, t_norm)
        
        # 4. Crackling Lightning Sparks (In Front of Goku)
        self.render_sparks(draw, gx, gy, t_norm)
        
        # 5. Clean ASCII Saiyan HUD Banner
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
        print(f"✨ Successfully generated Git Goku ({self.form['name']}, Day {self.streak_days}) -> {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Git Goku - Saiyan Evolution Profile Engine")
    parser.add_argument("--username", type=str, default="namanmdave", help="GitHub username")
    parser.add_argument("--streak", type=int, default=None, help="Explicit streak count (if not querying API)")
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
