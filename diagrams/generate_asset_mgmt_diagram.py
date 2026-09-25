#!/usr/bin/env python3
"""生成资管业务自动驾驶整体方案图 v3 - 按四大类分块"""

from PIL import Image, ImageDraw, ImageFont
import os

W, H = 2000, 1500
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
    'sec1_bg': '#e8f5e9', 'sec1_text': '#2e7d32',
    'sec2_bg': '#fff3e0', 'sec2_text': '#e65100',
    'sec3_bg': '#e3f2fd', 'sec3_text': '#1565c0',
    'sec4_bg': '#f3e5f5', 'sec4_text': '#6a1b9a',
    'model_bg': '#ffffff',
    'model_border': '#e0e0e0',
    'text_dark': '#333333',
    'text_mid': '#555555',
    'text_light': '#888888',
    'footer': '#999999',
}

SEC_STYLES = {
    'sec1': ('#e8f5e9', '#2e7d32'),
    'sec2': ('#fff3e0', '#e65100'),
    'sec3': ('#e3f2fd', '#1565c0'),
    'sec4': ('#f3e5f5', '#6a1b9a'),
}

def draw_rounded_rect(d, xy, radius, fill, outline=None, width=1):
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_text_centered(d, cx, y, text, font, fill):
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    d.text((cx - tw / 2, y), text, font=font, fill=fill)

def draw_text_left(d, x, y, text, font, fill):
    d.text((x, y), text, font=font, fill=fill)

def wrap_text_by_width(draw, text, font, max_width):
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
draw_text_centered(draw, W/2, 25, '资产管理自动驾驶平台方案', title_font, COLORS['title'])
draw_text_centered(draw, W/2, 65, '基于产品、客户、规则等原子模型实现资产管理自动驾驶 | 对标贝莱德、彭博 | 行业级智能体产品', subtitle_font, COLORS['subtitle'])

# ==================== 布局 ====================
LEFT_X = 20
LEFT_W = 300
RIGHT_X = W - 20 - 300
RIGHT_W = 300
ENGINE_X = LEFT_X + LEFT_W + 30
ENGINE_W = W - ENGINE_X - RIGHT_W - 30
ENGINE_Y = 100

# ==================== 四大类原子模型定义 ====================
# 左侧：产品创设阶段 + 资金募集阶段（整合渠道代销）+ 投资运作阶段
# 右侧：监督和计量

sections_left = [
    {
        'title': '产品创设原子模型',
        'sec': 'sec1',
        'models': [
            ('📐 资管产品设计原子模型', '3维', '配置结构/风险收益特征/期限安排'),
            ('📊 同业比对原子模型', '蒸馏', '市面十几万只产品比对/配置差异/费率差异'),
            ('🧮 收益测算原子模型', '测算', '预期收益/回撤压力测试/场景模拟'),
            ('👤 投资经理准入原子模型', '6维', '管理规模/处罚/财务/团队/投资能力/风控'),
        ]
    },
    {
        'title': '资金募集原子模型',
        'sec': 'sec2',
        'models': [
            ('👥 客户分类原子模型', '分层', '个人客户分层/机构客户分类/资金规模'),
            ('🎯 客户与产品匹配规则原子模型', '5项', '合规/投资能力/风险偏好/投资意愿/投资期限'),
            ('📝 内容推介生成原子模型', '6项', '合规宣传/产品特征/风险揭示/收益预期/适配说明/发行安排'),
            ('🏦 渠道准入原子模型', '2情形', '已准入→直接办产品准入/新拓展→先机构后产品'),
        ]
    },
    {
        'title': '投资运作原子模型',
        'sec': 'sec3',
        'models': [
            ('📋 投资运作动作原子模型', '动作', '投资范围确认/交易执行/持仓管理/估值核算'),
            ('⚠️ 风险监测原子模型', '监测', '净值回撤/集中度/流动性/合规风控线'),
            ('🔧 持续服务原子模型', '5项', '定期报告/净值波动沟通/重大变化/大额赎回/客户咨询'),
        ]
    },
]

sections_right = [
    {
        'title': '监督和计量原子模型',
        'sec': 'sec4',
        'models': [
            ('🛡️ 资管产品合规模型', '5项', '宣传合规/合格投资者/风险提示/适当性/购买回访'),
            ('👁️ 监督模型', '6项', '进度管控/质量检查/合规留痕/异常报警/推进督促/计量核算'),
            ('⚖️ 员工贡献计量分配原子模型', '按角色', '发起人/产品设计师/募集销售人/投资经理/协作支持人'),
            ('📈 总绩效计量原子模型', '按模式', '管理费/超额报酬/认申购费/销售服务费/五模式分别定义'),
            ('💰 准入标准费率原子模型', '5项', '管理费下限/超额报酬基准/认申购费/销售服务费/业绩比较基准'),
            ('🔑 权限模型', '引擎', '任务组边界/语料权限/授权失效/访问留痕'),
            ('📋 跟投评估模型', '模式五', '跟投比例/风险评估/资金来源/退出机制'),
        ]
    },
]

# ==================== 渲染函数 ====================
sec_header_font = get_font(13, bold=True)
mc_font_title = get_font(11, bold=True)
mc_font_tag = get_font(9)
mc_font_content = get_font(9)
mc_h = 68
mc_gap = 6
sec_gap = 14

def render_sections(sections, x, w):
    y = ENGINE_Y
    card_positions = []
    for section in sections:
        bg, text_color = SEC_STYLES[section['sec']]
        # 分块标题
        hdr_rect = (x, y, x + w, y + 28)
        draw_rounded_rect(draw, hdr_rect, 6, bg)
        draw_text_centered(draw, x + w/2, y + 5, section['title'], sec_header_font, text_color)
        y += 34
        
        # 模型卡片
        for title, tag, content in section['models']:
            rect = (x, y, x + w, y + mc_h)
            draw_rounded_rect(draw, rect, 8, COLORS['model_bg'], COLORS['model_border'], 1)
            draw_text_left(draw, x + 10, y + 7, title, mc_font_title, COLORS['text_dark'])
            
            tag_rect = (x + w - 55, y + 7, x + w - 10, y + 24)
            draw_rounded_rect(draw, tag_rect, 8, bg)
            bbox = draw.textbbox((0,0), tag, font=mc_font_tag)
            tw = bbox[2]-bbox[0]
            draw_text_left(draw, x + w - 10 - tw - (45-tw)/2, y + 9, tag, mc_font_tag, text_color)
            
            lines = wrap_text_by_width(draw, content, mc_font_content, w - 20)
            for i, line in enumerate(lines[:3]):
                draw_text_left(draw, x + 10, y + 28 + i*14, line, mc_font_content, COLORS['text_mid'])
            
            card_positions.append((x + w if x < W/2 else x, y + mc_h/2))
            y += mc_h + mc_gap
        
        y += sec_gap
    
    return y, card_positions

# 渲染左侧
left_end_y, left_card_positions = render_sections(sections_left, LEFT_X, LEFT_W)

# 渲染右侧
right_end_y, right_card_positions = render_sections(sections_right, RIGHT_X, RIGHT_W)

# 取最大高度
max_side_y = max(left_end_y, right_end_y)

# ==================== 中间引擎 ====================
eng_title_font = get_font(18, bold=True)
eng_sub_font = get_font(11)
task_text_font = get_font(11)
task_label_font = get_font(12, bold=True)

eng_rect = (ENGINE_X, ENGINE_Y, ENGINE_X + ENGINE_W, max_side_y + 10)
draw_rounded_rect(draw, eng_rect, 16, COLORS['engine_bg'], COLORS['engine_border'], 3)

eng_cx = ENGINE_X + ENGINE_W / 2
draw_text_centered(draw, eng_cx, ENGINE_Y + 15, '🚗 资产管理自动驾驶引擎', eng_title_font, COLORS['engine_border'])
draw_text_centered(draw, eng_cx, ENGINE_Y + 45, '驱动模型=AI提示词 | 状态与计量分离 | 全部并发无流程', eng_sub_font, COLORS['text_light'])

tasks = [
    ('1', '发起创设/引入意向',
     '发起产品创设意向，来源包括：员工发起、外部投资经理提交、资金方需求、委外确认。生成标准化任务卡片，调用"权限模型"组建任务组，所有意向不判断可行性全部进入引擎'),
    ('2', '生成产品方案',
     '并发调用"资管产品设计原子模型"、"同业比对原子模型"、"收益测算原子模型"生成产品方案，调用"投资经理准入原子模型"做六维评价，调用"资管产品合规模型"、"准入标准费率原子模型"、"总绩效计量原子模型"完成合规校验与费率确认，不通过给调优建议不拒绝'),
    ('3', '产品准入与签约',
     '调用"客户分类原子模型"、"客户与产品匹配规则原子模型"进行自动撮合匹配找到目标客户，调用"内容推介生成原子模型"生成推介内容，经"资管产品合规模型"验证后，有经纪关系的派发给客户经理，无关系的全平台抢单'),
    ('4', '资金募集',
     '调用"渠道准入原子模型"区分已准入机构和新拓展机构，已准入的直接办产品准入，新拓展的先办机构准入再办产品准入，两种情形不混在一起，完成后签署合作协议和产品销售协议'),
    ('5', '投资运作',
     '确认投资经理或挂名投资经理，调用"资管产品设计原子模型"确认投资范围与限制，调用"资管产品合规模型"持续监测，净值异常只报警不干预投资决策'),
    ('6', '持续服务',
     '调用"持续服务原子模型"，事件驱动并发处理定期报告、净值波动沟通(当日3%/历史10%)、重大变化沟通、大额赎回(月减30%)、客户咨询响应，自动生成服务工单'),
    ('7', '监督全过程管控',
     '监督模型贯穿全程并发运行，进度管控、质量检查、合规留痕、异常报警、推进督促、计量核算，调用"资管产品合规模型"留痕，调用"权限模型"管理任务组权限，只留痕报警督促不干预业务执行'),
    ('8', '贡献计量与收入分配',
     '任务闭环后调用"员工贡献计量分配原子模型"、"总绩效计量原子模型"，按五类产品模式分别计量，机器完成的不计量，只拆核心链条，中后台不参与分成，当期与递延结合，调用"跟投评估模型"处理模式五跟投'),
]

task_y = ENGINE_Y + 72
task_left_pad = 15
text_left_pad = task_left_pad + 10

for idx, (num, theme, body) in enumerate(tasks):
    label = f'任务{num}'
    max_text_w = ENGINE_W - text_left_pad - 20
    theme_text = f'{label}  {theme}'
    theme_lines = wrap_text_by_width(draw, theme_text, task_label_font, max_text_w)
    body_lines = wrap_text_by_width(draw, body, task_text_font, max_text_w)
    task_h = max(52, len(theme_lines)*20 + len(body_lines)*18 + 18)
    
    t_rect = (ENGINE_X + task_left_pad, task_y, ENGINE_X + ENGINE_W - task_left_pad, task_y + task_h)
    draw_rounded_rect(draw, t_rect, 8, COLORS['task_bg'], COLORS['task_border'], 1)
    
    for i, line in enumerate(theme_lines):
        draw_text_left(draw, ENGINE_X + text_left_pad, task_y + 8 + i*20, line, task_label_font, '#2e7d32')
    
    body_start = task_y + 8 + len(theme_lines)*20 + 2
    for i, line in enumerate(body_lines):
        draw_text_left(draw, ENGINE_X + text_left_pad, body_start + i*18, line, task_text_font, COLORS['text_mid'])
    
    task_y += task_h + 8

# ==================== 底部说明 ====================
footer_font = get_font(12)
footer_text = '资产管理自动驾驶平台 v3.0 | 一套方法论、一套模型、套不同产品特征 | 开放→聚合→机制→产品 | 对标贝莱德、彭博'
draw_text_centered(draw, W/2, max(task_y, max_side_y) + 20, footer_text, footer_font, COLORS['footer'])

# 保存
output_path = '/root/.openclaw/workspace/diagrams/资管业务自动驾驶整体方案-v2.png'
img.save(output_path, 'PNG', dpi=(150, 150))
print(f'OK: {output_path}, size: {W}x{max(H, max(task_y, max_side_y) + 60)}')
