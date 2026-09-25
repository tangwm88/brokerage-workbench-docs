#!/usr/bin/env python3
"""生成资管业务自动驾驶整体方案图"""

from PIL import Image, ImageDraw, ImageFont
import os

# 画布尺寸
W, H = 2000, 1400
img = Image.new('RGB', (W, H), '#f8f9fa')
draw = ImageDraw.Draw(img)

# 字体
FONT_BOLD_PATH = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
FONT_REG_PATH = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'

def get_font(size, bold=False):
    path = FONT_BOLD_PATH if bold else FONT_REG_PATH
    try:
        return ImageFont.truetype(path, size, index=2)  # SC index
    except:
        try:
            return ImageFont.truetype(path, size)
        except:
            return ImageFont.load_default()

# 颜色
COLORS = {
    'title': '#1a1a2e',
    'subtitle': '#666666',
    'engine_border': '#1565c0',
    'engine_bg': '#ffffff',
    'task_bg': '#ffffff',
    'task_border': '#e3f2fd',
    'left_header_bg': '#e8f5e9',
    'left_header_text': '#2e7d32',
    'right_header_bg': '#e3f2fd',
    'right_header_text': '#1565c0',
    'model_bg': '#ffffff',
    'model_border': '#e0e0e0',
    'text_dark': '#333333',
    'text_mid': '#555555',
    'text_light': '#888888',
    'tag_green_bg': '#e8f5e9',
    'tag_green_text': '#2e7d32',
    'tag_blue_bg': '#e3f2fd',
    'tag_blue_text': '#1565c0',
    'tag_orange_bg': '#fff3e0',
    'tag_orange_text': '#e65100',
    'tag_purple_bg': '#f3e5f5',
    'tag_purple_text': '#6a1b9a',
    'footer': '#999999',
}

# 连接线颜色
CONN_COLORS = ['#2e7d32', '#1565c0', '#e65100', '#6a1b9a', '#c62828', '#00695c', '#283593', '#4e342e']

def draw_rounded_rect(d, xy, radius, fill, outline=None, width=1):
    x1, y1, x2, y2 = xy
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_text_centered(d, cx, y, text, font, fill):
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    d.text((cx - tw / 2, y), text, font=font, fill=fill)

def draw_text_left(d, x, y, text, font, fill):
    d.text((x, y), text, font=font, fill=fill)

def wrap_text(text, max_chars):
    """简单换行"""
    lines = []
    current = ''
    for char in text:
        current += char
        if len(current) >= max_chars:
            lines.append(current)
            current = ''
    if current:
        lines.append(current)
    return lines

# ==================== 标题 ====================
title_font = get_font(28, bold=True)
subtitle_font = get_font(14)
draw_text_centered(draw, W/2, 25, '资管业务自动驾驶整体方案', title_font, COLORS['title'])
draw_text_centered(draw, W/2, 65, '基于产品、客户、规则等原子模型实现资管业务自动驾驶 | 对标贝莱德、彭博 | 行业级智能体产品', subtitle_font, COLORS['subtitle'])

# ==================== 布局参数 ====================
LEFT_X = 30
LEFT_W = 320
RIGHT_X = W - 30 - 320
RIGHT_W = 320
ENGINE_X = LEFT_X + LEFT_W + 40
ENGINE_W = W - ENGINE_X - RIGHT_W - 40
ENGINE_Y = 100

# ==================== 左侧原子模型 ====================
left_models = [
    ('📐 资管产品设计原子模型', '3维', '配置结构 / 风险收益特征 / 期限安排', 'green'),
    ('📊 同业比对原子模型', '蒸馏', '市面十几万只产品比对 / 配置差异 / 费率差异', 'green'),
    ('🧮 收益测算原子模型', '测算', '预期收益 / 回撤压力测试 / 场景模拟', 'green'),
    ('👤 投资经理准入原子模型', '6维', '管理规模/处罚信息/经营财务/团队实力/投资能力/风控能力', 'green'),
    ('👥 客户分类原子模型', '分层', '个人客户分层 / 机构客户分类 / 资金规模', 'green'),
    ('🎯 客户与产品匹配规则原子模型', '5项', '合规/投资能力/风险偏好/投资意愿/投资期限', 'green'),
    ('📝 内容推介生成原子模型', '6项', '合规宣传/产品特征/风险揭示/收益预期/适配说明/发行安排', 'green'),
    ('🏦 渠道准入原子模型', '2情形', '已准入→直接办产品准入 / 新拓展→先机构后产品', 'green'),
]

# 左侧标题
lh_font = get_font(14, bold=True)
lh_rect = (LEFT_X, ENGINE_Y, LEFT_X + LEFT_W, ENGINE_Y + 32)
draw_rounded_rect(draw, lh_rect, 6, COLORS['left_header_bg'])
draw_text_centered(draw, LEFT_X + LEFT_W/2, ENGINE_Y + 6, '创设与募集阶段原子模型', lh_font, COLORS['left_header_text'])

# 左侧模型卡片
mc_font_title = get_font(12, bold=True)
mc_font_tag = get_font(10)
mc_font_content = get_font(10)
mc_y = ENGINE_Y + 42
mc_h = 82
mc_gap = 10

left_card_positions = []
for title, tag, content, color in left_models:
    rect = (LEFT_X, mc_y, LEFT_X + LEFT_W, mc_y + mc_h)
    draw_rounded_rect(draw, rect, 8, COLORS['model_bg'], COLORS['model_border'], 1)
    
    # 标题
    draw_text_left(draw, LEFT_X + 10, mc_y + 8, title, mc_font_title, COLORS['text_dark'])
    
    # 标签
    tag_bg = COLORS['tag_green_bg']
    tag_text = COLORS['tag_green_text']
    tag_rect = (LEFT_X + LEFT_W - 60, mc_y + 8, LEFT_X + LEFT_W - 10, mc_y + 26)
    draw_rounded_rect(draw, tag_rect, 8, tag_bg)
    bbox = draw.textbbox((0,0), tag, font=mc_font_tag)
    tw = bbox[2]-bbox[0]
    draw_text_left(draw, LEFT_X + LEFT_W - 10 - tw - (50-tw)/2, mc_y + 10, tag, mc_font_tag, tag_text)
    
    # 内容
    lines = wrap_text(content, 28)
    for i, line in enumerate(lines[:3]):
        draw_text_left(draw, LEFT_X + 10, mc_y + 32 + i*16, line, mc_font_content, COLORS['text_mid'])
    
    left_card_positions.append((LEFT_X + LEFT_W, mc_y + mc_h/2))
    mc_y += mc_h + mc_gap

# ==================== 右侧原子模型 ====================
right_models = [
    ('🛡️ 资管产品合规模型', '5项', '宣传内容合规/合格投资者/风险提示/适当性匹配/购买回访', 'blue'),
    ('📈 总绩效计量原子模型', '按模式', '管理费提成/超额报酬/认申购费/销售服务费/五种模式分别定义', 'blue'),
    ('💰 准入标准费率原子模型', '5项', '管理费下限/超额报酬基准/认申购费/销售服务费/业绩比较基准', 'blue'),
    ('⚖️ 员工贡献计量分配原子模型', '按角色', '发起人/产品设计师/募集销售人/投资经理/协作支持人', 'orange'),
    ('🔧 产品售后动作原子模型', '5项', '定期报告/净值波动沟通(当日3%历史10%)/重大变化/大额赎回(月减30%)', 'orange'),
    ('👁️ 监督模型', '6项', '进度管控/质量检查/合规留痕/异常报警/推进督促/计量核算', 'orange'),
    ('🔑 权限模型', '引擎', '任务组边界/语料权限/授权失效/访问留痕', 'purple'),
    ('📋 跟投评估模型', '模式五', '跟投比例/风险评估/资金来源/退出机制', 'purple'),
]

rh_rect = (RIGHT_X, ENGINE_Y, RIGHT_X + RIGHT_W, ENGINE_Y + 32)
draw_rounded_rect(draw, rh_rect, 6, COLORS['right_header_bg'])
draw_text_centered(draw, RIGHT_X + RIGHT_W/2, ENGINE_Y + 6, '公司标准规则与售后原子模型', lh_font, COLORS['right_header_text'])

mc_y = ENGINE_Y + 42
right_card_positions = []
for title, tag, content, color in right_models:
    rect = (RIGHT_X, mc_y, RIGHT_X + RIGHT_W, mc_y + mc_h)
    draw_rounded_rect(draw, rect, 8, COLORS['model_bg'], COLORS['model_border'], 1)
    
    draw_text_left(draw, RIGHT_X + 10, mc_y + 8, title, mc_font_title, COLORS['text_dark'])
    
    tag_colors = {
        'blue': (COLORS['tag_blue_bg'], COLORS['tag_blue_text']),
        'orange': (COLORS['tag_orange_bg'], COLORS['tag_orange_text']),
        'purple': (COLORS['tag_purple_bg'], COLORS['tag_purple_text']),
    }
    tag_bg, tag_text_color = tag_colors.get(color, (COLORS['tag_blue_bg'], COLORS['tag_blue_text']))
    tag_rect = (RIGHT_X + RIGHT_W - 65, mc_y + 8, RIGHT_X + RIGHT_W - 10, mc_y + 26)
    draw_rounded_rect(draw, tag_rect, 8, tag_bg)
    bbox = draw.textbbox((0,0), tag, font=mc_font_tag)
    tw = bbox[2]-bbox[0]
    draw_text_left(draw, RIGHT_X + RIGHT_W - 10 - tw - (55-tw)/2, mc_y + 10, tag, mc_font_tag, tag_text_color)
    
    lines = wrap_text(content, 28)
    for i, line in enumerate(lines[:3]):
        draw_text_left(draw, RIGHT_X + 10, mc_y + 32 + i*16, line, mc_font_content, COLORS['text_mid'])
    
    right_card_positions.append((RIGHT_X, mc_y + mc_h/2))
    mc_y += mc_h + mc_gap

# ==================== 中间引擎 ====================
eng_title_font = get_font(18, bold=True)
eng_sub_font = get_font(11)
task_title_font = get_font(12, bold=True)
task_prompt_font = get_font(10)
task_model_font = get_font(9)

# 引擎外框
eng_rect = (ENGINE_X, ENGINE_Y, ENGINE_X + ENGINE_W, mc_y - mc_gap + 10)
draw_rounded_rect(draw, eng_rect, 16, COLORS['engine_bg'], COLORS['engine_border'], 3)

# 引擎标题
eng_cx = ENGINE_X + ENGINE_W / 2
draw_text_centered(draw, eng_cx, ENGINE_Y + 15, '🚗 资管业务自动驾驶引擎', eng_title_font, COLORS['engine_border'])
draw_text_centered(draw, eng_cx, ENGINE_Y + 45, '驱动模型=AI提示词 | 状态与计量分离 | 全部并发无流程', eng_sub_font, COLORS['text_light'])

# 任务列表
tasks = [
    ('1', '接收产品创设/引入意向', '接收员工发起、外部投资经理提交、资金方需求、委外确认→生成标准化任务卡片，不做可行性判断', '驱动模型、权限模型', '#1565c0'),
    ('2', '产品方案生成与评审', '并发：设计方案→同业比对→收益测算→合规校验→费率确认。不通过给调优建议，不拒绝', '产品设计/同业比对/收益测算/投资经理准入/合规/费率/绩效计量', '#2e7d32'),
    ('3', '资金募集启动', '并发：匹配客户→生成推介内容→合规验证→有经纪关系派发/无关系全平台抢单', '客户分类/匹配规则/内容推介生成/合规', '#e65100'),
    ('4', '渠道准入与产品上架', '已准入→直接办产品准入；新拓展→先机构准入再产品准入。两种情形不混', '渠道准入/合规', '#6a1b9a'),
    ('5', '产品投资运作启动', '确认投资经理→开放权限→合规持续监测→净值异常只报警不干预投资决策', '产品设计/合规', '#c62828'),
    ('6', '售后持续服务', '事件驱动并发：定期报告/净值波动(当日3%历史10%)/重大变化/大额赎回(月减30%)/客户咨询', '售后动作/合规', '#00695c'),
    ('7', '监督全过程管控', '贯穿全程：进度/质量/留痕/报警/督促/计量核算。只留痕报警督促，不干预执行', '监督/合规/计量分配/权限', '#283593'),
    ('8', '贡献计量与收入分配', '按五类模式分别计量。机器完成的不计量。只拆核心链条。中后台不分。当期+递延', '贡献计量分配/绩效计量/跟投评估', '#4e342e'),
]

task_y = ENGINE_Y + 72
task_h = 88
task_gap = 8
task_num_size = 22

task_positions = []  # (task_center_x, task_center_y, task_index)

for idx, (num, title, prompt, models, color) in enumerate(tasks):
    t_rect = (ENGINE_X + 15, task_y, ENGINE_X + ENGINE_W - 15, task_y + task_h)
    draw_rounded_rect(draw, t_rect, 8, COLORS['task_bg'], COLORS['task_border'], 1)
    
    # 编号圆圈
    cx = ENGINE_X + 15 + 18
    cy = task_y + 18
    r = task_num_size // 2
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=color)
    num_font = get_font(11, bold=True)
    bbox = draw.textbbox((0,0), num, font=num_font)
    nw = bbox[2]-bbox[0]
    nh = bbox[3]-bbox[1]
    draw.text((cx-nw/2, cy-nh/2-1), num, font=num_font, fill='white')
    
    # 任务标题
    draw_text_left(draw, cx + r + 8, cy - 8, title, task_title_font, COLORS['text_dark'])
    
    # 提示词内容
    prompt_lines = wrap_text(prompt, 40)
    for i, line in enumerate(prompt_lines[:3]):
        draw_text_left(draw, cx + r + 8, task_y + 34 + i*14, line, task_prompt_font, COLORS['text_mid'])
    
    # 调用的模型标签
    model_tags = models.split('/')
    tag_x = cx + r + 8
    tag_y = task_y + task_h - 20
    for mt in model_tags[:6]:
        mt = mt.strip()
        bbox = draw.textbbox((0,0), mt, font=task_model_font)
        tw = bbox[2]-bbox[0]
        tag_rect = (tag_x, tag_y, tag_x + tw + 8, tag_y + 14)
        draw_rounded_rect(draw, tag_rect, 3, '#e3f2fd')
        draw_text_left(draw, tag_x + 4, tag_y + 1, mt, task_model_font, '#1565c0')
        tag_x += tw + 14
    
    task_positions.append((ENGINE_X + 15, task_y + task_h/2, ENGINE_X + ENGINE_W - 15, idx))
    task_y += task_h + task_gap

# ==================== 连接线 ====================
# 左模型对应任务索引
left_conn = [
    (0, 1),  # 产品设计 → task2
    (1, 1),  # 同业比对 → task2
    (2, 1),  # 收益测算 → task2
    (3, 1),  # 投资经理准入 → task2
    (4, 2),  # 客户分类 → task3
    (5, 2),  # 匹配规则 → task3
    (6, 2),  # 内容推介生成 → task3
    (7, 3),  # 渠道准入 → task4
]

# 右模型对应任务索引
right_conn = [
    (0, 1),  # 合规 → task2
    (0, 2),  # 合规 → task3
    (0, 3),  # 合规 → task4
    (0, 4),  # 合规 → task5
    (0, 5),  # 合规 → task6
    (0, 6),  # 合规 → task7
    (1, 1),  # 绩效计量 → task2
    (1, 7),  # 绩效计量 → task8
    (2, 1),  # 费率 → task2
    (3, 7),  # 贡献计量分配 → task8
    (4, 5),  # 售后动作 → task6
    (5, 6),  # 监督 → task7
    (6, 0),  # 权限 → task1
    (6, 6),  # 权限 → task7
    (7, 7),  # 跟投评估 → task8
]

# 画连接线（左）
for model_idx, task_idx in left_conn:
    lx, ly = left_card_positions[model_idx]
    tx, ty, _, _ = task_positions[task_idx]
    color = CONN_COLORS[task_idx % len(CONN_COLORS)]
    # 贝塞尔曲线近似
    mid_x = (lx + tx) / 2
    points = []
    for t in range(0, 21):
        t = t / 20
        x = (1-t)**2 * lx + 2*(1-t)*t * mid_x + t**2 * tx
        y = (1-t)**2 * ly + 2*(1-t)*t * ly + t**2 * ty
        # 控制点
        cx1 = mid_x
        cy1 = ly
        cx2 = mid_x
        cy2 = ty
        x = (1-t)**3 * lx + 3*(1-t)**2*t*cx1 + 3*(1-t)*t**2*cx2 + t**3*tx
        y = (1-t)**3 * ly + 3*(1-t)**2*t*cy1 + 3*(1-t)*t**2*cy2 + t**3*ty
        points.append((x, y))
    for i in range(len(points)-1):
        draw.line([points[i], points[i+1]], fill=color, width=1)

# 画连接线（右）
for model_idx, task_idx in right_conn:
    rx, ry = right_card_positions[model_idx]
    tx, ty, _, _ = task_positions[task_idx]
    color = CONN_COLORS[task_idx % len(CONN_COLORS)]
    mid_x = (rx + tx) / 2
    points = []
    for t in range(0, 21):
        t = t / 20
        cx1 = mid_x
        cy1 = ry
        cx2 = mid_x
        cy2 = ty
        x = (1-t)**3 * tx + 3*(1-t)**2*t*cx1 + 3*(1-t)*t**2*cx2 + t**3*rx
        y = (1-t)**3 * ty + 3*(1-t)**2*t*cy1 + 3*(1-t)*t**2*cy2 + t**3*ry
        points.append((x, y))
    for i in range(len(points)-1):
        draw.line([points[i], points[i+1]], fill=color, width=1)

# ==================== 底部说明 ====================
footer_font = get_font(12)
footer_text = '资管业务自动驾驶引擎 v2.0 | 一套方法论、一套模型、套不同产品特征 | 开放→聚合→机制→产品 | 对标贝莱德、彭博'
draw_text_centered(draw, W/2, H - 40, footer_text, footer_font, COLORS['footer'])

# 保存
output_path = '/root/.openclaw/workspace/diagrams/资管业务自动驾驶整体方案-v2.png'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
img.save(output_path, 'PNG', dpi=(150, 150))
print(f'OK: {output_path}')
