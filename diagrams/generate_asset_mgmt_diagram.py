#!/usr/bin/env python3
"""生成资管业务自动驾驶整体方案图 v2 - 参考零售表达方式"""

from PIL import Image, ImageDraw, ImageFont
import os

W, H = 2000, 1400
img = Image.new('RGB', (W, H), '#f8f9fa')
draw = ImageDraw.Draw(img)

FONT_BOLD_PATH = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
FONT_REG_PATH = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'

def get_font(size, bold=False):
    path = FONT_BOLD_PATH if bold else FONT_REG_PATH
    try:
        return ImageFont.truetype(path, size, index=2)
    except:
        try:
            return ImageFont.truetype(path, size)
        except:
            return ImageFont.load_default()

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
    'footer': '#999999',
}

CONN_COLORS = ['#2e7d32', '#1565c0', '#e65100', '#6a1b9a', '#c62828', '#00695c', '#283593', '#4e342e']

def draw_rounded_rect(d, xy, radius, fill, outline=None, width=1):
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_text_centered(d, cx, y, text, font, fill):
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    d.text((cx - tw / 2, y), text, font=font, fill=fill)

def draw_text_left(d, x, y, text, font, fill):
    d.text((x, y), text, font=font, fill=fill)

def wrap_text_by_width(draw, text, font, max_width):
    """按像素宽度换行"""
    lines = []
    current = ''
    for char in text:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(current)
            current = char
        else:
            current = test
    if current:
        lines.append(current)
    return lines

# ==================== 标题 ====================
title_font = get_font(28, bold=True)
subtitle_font = get_font(14)
draw_text_centered(draw, W/2, 25, '资管业务自动驾驶整体方案', title_font, COLORS['title'])
draw_text_centered(draw, W/2, 65, '基于产品、客户、规则等原子模型实现资管业务自动驾驶 | 对标贝莱德、彭博 | 行业级智能体产品', subtitle_font, COLORS['subtitle'])

# ==================== 布局 ====================
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

lh_font = get_font(14, bold=True)
lh_rect = (LEFT_X, ENGINE_Y, LEFT_X + LEFT_W, ENGINE_Y + 32)
draw_rounded_rect(draw, lh_rect, 6, COLORS['left_header_bg'])
draw_text_centered(draw, LEFT_X + LEFT_W/2, ENGINE_Y + 6, '创设与募集阶段原子模型', lh_font, COLORS['left_header_text'])

mc_font_title = get_font(11, bold=True)
mc_font_tag = get_font(9)
mc_font_content = get_font(9)
mc_y = ENGINE_Y + 42
mc_h = 72
mc_gap = 8

left_card_positions = []
for title, tag, content, color in left_models:
    rect = (LEFT_X, mc_y, LEFT_X + LEFT_W, mc_y + mc_h)
    draw_rounded_rect(draw, rect, 8, COLORS['model_bg'], COLORS['model_border'], 1)
    draw_text_left(draw, LEFT_X + 10, mc_y + 8, title, mc_font_title, COLORS['text_dark'])
    
    tag_rect = (LEFT_X + LEFT_W - 60, mc_y + 8, LEFT_X + LEFT_W - 10, mc_y + 26)
    draw_rounded_rect(draw, tag_rect, 8, COLORS['left_header_bg'])
    bbox = draw.textbbox((0,0), tag, font=mc_font_tag)
    tw = bbox[2]-bbox[0]
    draw_text_left(draw, LEFT_X + LEFT_W - 10 - tw - (50-tw)/2, mc_y + 10, tag, mc_font_tag, COLORS['left_header_text'])
    
    lines = []
    current = ''
    for char in content:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=mc_font_content)
        if bbox[2] - bbox[0] > LEFT_W - 20 and current:
            lines.append(current)
            current = char
        else:
            current = test
    if current:
        lines.append(current)
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
        'blue': ('#e3f2fd', '#1565c0'),
        'orange': ('#fff3e0', '#e65100'),
        'purple': ('#f3e5f5', '#6a1b9a'),
    }
    tag_bg, tag_text_color = tag_colors.get(color, ('#e3f2fd', '#1565c0'))
    tag_rect = (RIGHT_X + RIGHT_W - 65, mc_y + 8, RIGHT_X + RIGHT_W - 10, mc_y + 26)
    draw_rounded_rect(draw, tag_rect, 8, tag_bg)
    bbox = draw.textbbox((0,0), tag, font=mc_font_tag)
    tw = bbox[2]-bbox[0]
    draw_text_left(draw, RIGHT_X + RIGHT_W - 10 - tw - (55-tw)/2, mc_y + 10, tag, mc_font_tag, tag_text_color)
    
    lines = []
    current = ''
    for char in content:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=mc_font_content)
        if bbox[2] - bbox[0] > RIGHT_W - 20 and current:
            lines.append(current)
            current = char
        else:
            current = test
    if current:
        lines.append(current)
    for i, line in enumerate(lines[:3]):
        draw_text_left(draw, RIGHT_X + 10, mc_y + 32 + i*16, line, mc_font_content, COLORS['text_mid'])
    
    right_card_positions.append((RIGHT_X, mc_y + mc_h/2))
    mc_y += mc_h + mc_gap

# ==================== 中间引擎 ====================
eng_title_font = get_font(18, bold=True)
eng_sub_font = get_font(11)
task_num_font = get_font(11, bold=True)
task_text_font = get_font(11)
task_label_font = get_font(12, bold=True)

eng_rect = (ENGINE_X, ENGINE_Y, ENGINE_X + ENGINE_W, mc_y - mc_gap + 10)
draw_rounded_rect(draw, eng_rect, 16, COLORS['engine_bg'], COLORS['engine_border'], 3)

eng_cx = ENGINE_X + ENGINE_W / 2
draw_text_centered(draw, eng_cx, ENGINE_Y + 15, '🚗 资管业务自动驾驶引擎', eng_title_font, COLORS['engine_border'])
draw_text_centered(draw, eng_cx, ENGINE_Y + 45, '驱动模型=AI提示词 | 状态与计量分离 | 全部并发无流程', eng_sub_font, COLORS['text_light'])

# 任务列表 - 参考零售表达方式：任务N + 自然语言调度指令
tasks = [
    ('1', '接收创设/引入意向',
     '接收员工发起、外部投资经理提交、资金方需求、委外确认，生成标准化任务卡片，调用"权限模型"组建任务组，所有意向不判断可行性全部进入引擎'),
    ('2', '产品方案生成与评审',
     '并发调用"资管产品设计原子模型"、"同业比对原子模型"、"收益测算原子模型"生成产品方案，调用"投资经理准入原子模型"做六维评价，调用"资管产品合规模型"、"准入标准费率原子模型"、"总绩效计量原子模型"完成合规校验与费率确认，不通过给调优建议不拒绝'),
    ('3', '资金募集启动',
     '并发调用"客户分类原子模型"、"客户与产品匹配规则原子模型"自动匹配目标客户，调用"内容推介生成原子模型"生成推介内容，经"资管产品合规模型"验证后，有经纪关系的派发给客户经理，无关系的全平台抢单'),
    ('4', '渠道准入与产品上架',
     '调用"渠道准入原子模型"判断渠道类型，已准入机构直接办产品准入，新拓展机构先机构准入再产品准入，两种情形不混在一起，完成后产品上架'),
    ('5', '投资运作启动',
     '确认投资经理或挂名投资经理，调用"资管产品设计原子模型"确认投资范围与限制，调用"资管产品合规模型"持续监测，净值异常只报警不干预投资决策'),
    ('6', '售后持续服务',
     '调用"产品售后动作原子模型"，事件驱动并发处理：定期报告、净值波动沟通(当日3%/历史10%)、重大变化沟通、大额赎回(月减30%)、客户咨询响应，自动生成售后工单'),
    ('7', '监督全过程管控',
     '监督模型贯穿全程并发运行：进度管控、质量检查、合规留痕、异常报警、推进督促、计量核算，调用"资管产品合规模型"留痕，调用"权限模型"管理任务组权限，只留痕报警督促不干预业务执行'),
    ('8', '贡献计量与收入分配',
     '任务闭环后调用"员工贡献计量分配原子模型"、"总绩效计量原子模型"，按五类产品模式分别计量：机器完成的不计量，只拆核心链条，中后台不参与分成，当期与递延结合，调用"跟投评估模型"处理模式五跟投'),
]

task_y = ENGINE_Y + 72
task_num_size = 24
task_left_pad = 15
text_left_pad = task_left_pad + task_num_size + 12

task_positions = []

for idx, (num, theme, body) in enumerate(tasks):
    label = f'任务{num}'
    
    # 计算文本行数确定高度
    max_text_w = ENGINE_W - text_left_pad - 20
    
    # 主题行
    theme_text = f'{label}  {theme}'
    theme_lines = wrap_text_by_width(draw, theme_text, task_label_font, max_text_w)
    
    # 正文行
    body_lines = wrap_text_by_width(draw, body, task_text_font, max_text_w)
    
    task_h = max(52, len(theme_lines)*20 + len(body_lines)*18 + 18)
    
    t_rect = (ENGINE_X + task_left_pad, task_y, ENGINE_X + ENGINE_W - task_left_pad, task_y + task_h)
    draw_rounded_rect(draw, t_rect, 8, COLORS['task_bg'], COLORS['task_border'], 1)
    
    # 主题行 - 绿色加粗
    for i, line in enumerate(theme_lines):
        draw_text_left(draw, ENGINE_X + text_left_pad, task_y + 8 + i*20, line, task_label_font, '#2e7d32')
    
    # 正文
    body_start = task_y + 8 + len(theme_lines)*20 + 2
    for i, line in enumerate(body_lines):
        draw_text_left(draw, ENGINE_X + text_left_pad, body_start + i*18, line, task_text_font, COLORS['text_mid'])
    
    task_positions.append((ENGINE_X + task_left_pad, task_y + task_h/2, ENGINE_X + ENGINE_W - task_left_pad, idx))
    task_y += task_h + 8

# ==================== 连接线 ====================
# 连接线已移除（用户要求）
left_conn = []
right_conn = []

for model_idx, task_idx in left_conn:
    lx, ly = left_card_positions[model_idx]
    tx, ty, _, _ = task_positions[task_idx]
    color = CONN_COLORS[task_idx % len(CONN_COLORS)]
    mid_x = (lx + tx) / 2
    points = []
    for t in range(0, 21):
        t = t / 20
        cx1, cy1 = mid_x, ly
        cx2, cy2 = mid_x, ty
        x = (1-t)**3 * lx + 3*(1-t)**2*t*cx1 + 3*(1-t)*t**2*cx2 + t**3*tx
        y = (1-t)**3 * ly + 3*(1-t)**2*t*cy1 + 3*(1-t)*t**2*cy2 + t**3*ty
        points.append((x, y))
    for i in range(len(points)-1):
        draw.line([points[i], points[i+1]], fill=color, width=1)

for model_idx, task_idx in right_conn:
    rx, ry = right_card_positions[model_idx]
    tx, ty, _, _ = task_positions[task_idx]
    color = CONN_COLORS[task_idx % len(CONN_COLORS)]
    mid_x = (rx + tx) / 2
    points = []
    for t in range(0, 21):
        t = t / 20
        cx1, cy1 = mid_x, ry
        cx2, cy2 = mid_x, ty
        x = (1-t)**3 * tx + 3*(1-t)**2*t*cx1 + 3*(1-t)*t**2*cx2 + t**3*rx
        y = (1-t)**3 * ty + 3*(1-t)**2*t*cy1 + 3*(1-t)*t**2*cy2 + t**3*ry
        points.append((x, y))
    for i in range(len(points)-1):
        draw.line([points[i], points[i+1]], fill=color, width=1)

# ==================== 底部说明 ====================
footer_font = get_font(12)
footer_text = '资管业务自动驾驶引擎 v2.1 | 一套方法论、一套模型、套不同产品特征 | 开放→聚合→机制→产品 | 对标贝莱德、彭博'
draw_text_centered(draw, W/2, task_y + 20, footer_text, footer_font, COLORS['footer'])

# 保存
output_path = '/root/.openclaw/workspace/diagrams/资管业务自动驾驶整体方案-v2.png'
img.save(output_path, 'PNG', dpi=(150, 150))
print(f'OK: {output_path}, size: {W}x{H}')
