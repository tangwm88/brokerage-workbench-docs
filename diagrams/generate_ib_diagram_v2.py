#!/usr/bin/env python3
"""生成资管业务自动驾驶整体方案图 v3 - 卡片式详细内容"""

from PIL import Image, ImageDraw, ImageFont
import os

W, H = 2400, 1800
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
draw_text_centered(draw, W/2, 25, '投资银行自动驾驶平台', title_font, COLORS['title'])

# ==================== 布局 ====================
LEFT_X = 20
LEFT_W = 400
RIGHT_X = W - 20 - 400
RIGHT_W = 400
ENGINE_X = LEFT_X + LEFT_W + 30
ENGINE_W = W - ENGINE_X - RIGHT_W - 30
ENGINE_Y = 100

# ==================== 原子模型定义（卡片式详细内容） ====================

sections_left = [
    {
        'title': '项目发现原子模型',
        'sec': 'sec1',
        'models': [
            {
                'title': '📐 投行项目类型原子模型',
                'tag': '6类',
                'items': [
                    ('股权融资', 'IPO/定增/配股/可转债/优先股'),
                    ('债券融资', '公司债/企业债/ABS/短融中票/私募债'),
                    ('并购重组', '借壳上市/整体上市/资产注入/要约收购'),
                    ('财务顾问', '常年顾问/专项顾问/独立财务顾问'),
                    ('资产证券化', '信贷ABS/企业ABS/REITs/CMBS'),
                    ('结构化融资', '股债结合/夹层融资/永续债/明股实债'),
                ]
            },
            {
                'title': '🔍 项目筛选评估原子模型',
                'tag': '6维',
                'items': [
                    ('企业质地', '行业地位/盈利能力/成长性/财务健康度'),
                    ('融资可行性', '监管要求/发行条件/时间窗口/市场接受度'),
                    ('交易复杂度', '交易结构/涉及方数量/监管审批层级'),
                    ('收益预期', '承销费/顾问费/综合收益/投入产出比'),
                    ('风险因素', '审核风险/市场风险/信用风险/操作风险'),
                    ('战略价值', '客户关系/后续业务机会/品牌影响力'),
                ]
            },
            {
                'title': '👤 投行团队匹配原子模型',
                'tag': '6维',
                'items': [
                    ('项目经验', '同类项目数量/规模/行业覆盖'),
                    ('专业资质', '保代资格/CPA/CFA/律师资格'),
                    ('历史业绩', '成功率/发行规模/客户满意度'),
                    ('行业专长', 'TMT/医药/制造/金融等深度'),
                    ('监管沟通', '审核沟通经验/反馈处理效率'),
                    ('团队协作', '团队配置/分工合理性/协同效率'),
                ]
            },
        ]
    },
    {
        'title': '交易撮合原子模型',
        'sec': 'sec2',
        'models': [
            {
                'title': '💰 资金方分类原子模型',
                'tag': '6类',
                'items': [
                    ('机构投资者', '公募/私募/保险/理财子/券商资管/产业资本'),
                    ('银行资金', '信贷资金/投贷联动/并购贷款/夹层资金'),
                    ('产业资本', '上市公司/产业集团/战略投资者/财务投资者'),
                    ('个人投资者', '高净值客户/专业投资者/合格投资者'),
                    ('另类资金', '并购基金/夹层基金/特殊机会基金/S基金'),
                    ('资金性质', '自有/受托/募集/专项投资资金'),
                ]
            },
            {
                'title': '🎯 项目与资金匹配规则原子模型',
                'tag': '6项',
                'items': [
                    ('合规匹配', '适当性认定/合格投资者/监管要求'),
                    ('规模匹配', '资金规模与项目规模匹配/比例限制'),
                    ('风险偏好', '投资者风险等级与项目风险等级匹配'),
                    ('行业偏好', '投资偏好与项目行业匹配/产业链协同'),
                    ('期限匹配', '资金期限与项目期限匹配/退出时间预期'),
                    ('回报匹配', '预期回报率与投资者回报要求匹配'),
                ]
            },
            {
                'title': '📝 交易结构生成原子模型',
                'tag': '6项',
                'items': [
                    ('融资方案', '股权/债权/混合/公开/非公开/一次/分期'),
                    ('增信安排', '抵押/质押/担保/差额补足/流动性支持'),
                    ('退出机制', 'IPO退出/并购退出/回购退出/转让退出'),
                    ('定价机制', '固定价格/询价定价/竞价定价/簿记建档'),
                    ('投资者保护', '回售条款/赎回条款/下修条款/优先清算权'),
                    ('结构创新', '股债结合/可转债/可交换债/永续债/优先股'),
                ]
            },
            {
                'title': '🤝 合作方对接原子模型',
                'tag': '6情形',
                'items': [
                    ('已合作机构', '直接进入交易执行/明确分工和费用分摊'),
                    ('新拓展机构', '先办准入(资质/尽调/协议)再开展业务'),
                    ('联合承销', '主承/副主承分工/份额分配/费用分摊'),
                    ('联合投资', '领投/跟投分工/投资决策/投后管理/退出'),
                    ('中介协作', '律所/会计师/评估机构协作/费用分摊'),
                    ('政府对接', '发改委/证监会/交易所/行业协会沟通'),
                ]
            },
        ]
    },
    {
        'title': '交易执行原子模型',
        'sec': 'sec3',
        'models': [
            {
                'title': '📋 项目执行动作原子模型',
                'tag': '6动作',
                'items': [
                    ('项目启动', '立项审批/团队组建/工作计划/保密协议'),
                    ('尽职调查', '业务/财务/法律尽调/行业研究/底稿编制'),
                    ('材料制作', '招股书/募集说明书/重组报告书/反馈回复'),
                    ('监管申报', '证监会/交易所/发改委申报/审核跟进'),
                    ('发行承销', '路演推介/簿记建档/定价发行/缴款结算'),
                    ('交割过户', '股份登记/资金划转/资产过户/工商变更'),
                ]
            },
            {
                'title': '🔧 持续督导原子模型',
                'tag': '6项',
                'items': [
                    ('定期报告', '年报/半年报/季报按时编制披露'),
                    ('重大事项', '重大合同/投资/诉讼/关联交易披露'),
                    ('募集资金', '使用进度监督/用途变更审批'),
                    ('股价异动', '异动≥20%/连续涨跌停核查披露'),
                    ('投资者关系', '投资者咨询/分析师调研/媒体采访'),
                    ('违规处理', '发行人违规/信披违规督促整改报告'),
                ]
            },
        ]
    },
]

sections_right = [
    {
        'title': '监督和计量原子模型',
        'sec': 'sec4',
        'models': [
            {
                'title': '⚠️ 风险监测原子模型',
                'tag': '5维',
                'items': [
                    ('项目进度', '节点延期≥30天预警/整体延期≥60天报警'),
                    ('审核风险', '反馈意见异常/审核周期超预期/被否风险'),
                    ('市场风险', '利率波动/估值下移/投资者情绪恶化'),
                    ('合规风险', '信披违规/内幕交易嫌疑/利益冲突'),
                    ('信用风险', '发行人财务恶化/偿债能力下降/违约风险'),
                ]
            },
            {
                'title': '🛡️ 投行项目合规模型',
                'tag': '7项',
                'items': [
                    ('信息披露合规', '真实/准确/完整/及时/公平披露'),
                    ('尽职调查合规', '尽调充分/底稿完整/核查到位'),
                    ('发行承销合规', '程序合规/定价公允/配售公平'),
                    ('持续督导合规', '督导到位/信披监督/募集资金监管'),
                    ('内幕信息管理', '知情人登记/信息隔离墙/禁止交易'),
                    ('利益冲突管理', '冲突识别/回避措施/信息披露'),
                    ('廉洁从业', '不得商业贿赂/不得利益输送/廉洁承诺'),
                ]
            },
            {
                'title': '👁️ 监督模型',
                'tag': '7项',
                'items': [
                    ('进度管控', '项目进度跟踪/节点检查/延期预警'),
                    ('质量检查', '申报文件审核/尽调工作检查/底稿检查'),
                    ('合规留痕', '全过程留痕/操作记录/审批记录'),
                    ('异常报警', '异常自动识别/分级报警/实时监测'),
                    ('推进督促', '项目滞留自动督促/升级处理'),
                    ('计量核算', '贡献计量/绩效核算/分配确认'),
                    ('独立监督', '独立于业务运作/直接向AI委员会报告'),
                ]
            },
            {
                'title': '⚖️ 投行项目员工贡献计量分配原子模型',
                'tag': '7类角色',
                'items': [
                    ('项目承揽人', '项目规模×承销费率0.5-2.0%'),
                    ('项目保荐人', '保荐费×30-40%'),
                    ('项目承做人', '承做工作量×承做费率'),
                    ('承销销售人', '销售金额×销售费率0.2-0.5%'),
                    ('持续督导人', '督导项目×5-20万/项目/年'),
                    ('协作支持人', '按支持贡献一次性或按期计提'),
                    ('平台运营方', '项目收入×10-15%'),
                ]
            },
            {
                'title': '📈 投行项目总绩效计量原子模型',
                'tag': '5类收入',
                'items': [
                    ('承销费收入', '提成20%/补贴10%'),
                    ('保荐费收入', '提成20%/补贴10%'),
                    ('财务顾问费收入', '提成25%/补贴10%'),
                    ('持续督导费收入', '提成30%/按年计提'),
                    ('分销费收入', '提成50%/分销贡献'),
                ]
            },
            {
                'title': '💰 投行项目准入标准费率原子模型',
                'tag': '按业务',
                'items': [
                    ('IPO承销费', '最低5.0%/目标8.0%'),
                    ('再融资承销费', '最低1.5%/目标3.0%'),
                    ('债券承销费', '最低0.3%/目标0.8%'),
                    ('并购重组顾问费', '最低1.0%/目标2.5%'),
                    ('财务顾问费', '最低0.5%/目标1.5%'),
                ]
            },
        ]
    },
]

# ==================== 渲染函数 ====================
sec_header_font = get_font(13, bold=True)
mc_font_title = get_font(11, bold=True)
mc_font_tag = get_font(9)
mc_font_key = get_font(9, bold=True)
mc_font_val = get_font(8)
mc_gap = 8
sec_gap = 16

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
        for model in section['models']:
            items = model['items']
            # 计算卡片高度：标题(22) + 每个条目(16) + 边距
            mc_h = 30 + len(items) * 16 + 10
            
            rect = (x, y, x + w, y + mc_h)
            draw_rounded_rect(draw, rect, 8, COLORS['model_bg'], COLORS['model_border'], 1)
            
            # 标题和标签
            draw_text_left(draw, x + 10, y + 7, model['title'], mc_font_title, COLORS['text_dark'])
            
            tag = model['tag']
            tag_rect = (x + w - 60, y + 7, x + w - 10, y + 24)
            draw_rounded_rect(draw, tag_rect, 8, bg)
            bbox = draw.textbbox((0,0), tag, font=mc_font_tag)
            tw = bbox[2]-bbox[0]
            draw_text_left(draw, x + w - 10 - tw - (50-tw)/2, y + 9, tag, mc_font_tag, text_color)
            
            # 键值对内容
            item_y = y + 30
            for key, val in items:
                # 键
                draw_text_left(draw, x + 12, item_y, f'▸ {key}', mc_font_key, text_color)
                # 值（换行处理）
                key_width = draw.textbbox((0,0), f'▸ {key}', font=mc_font_key)[2]
                val_x = x + 12 + key_width + 8
                val_max_w = w - (val_x - x) - 15
                val_lines = wrap_text_by_width(draw, val, mc_font_val, val_max_w)
                for i, line in enumerate(val_lines[:2]):  # 最多2行
                    draw_text_left(draw, val_x, item_y + i*14, line, mc_font_val, COLORS['text_mid'])
                item_y += max(16, len(val_lines[:2]) * 14 + 2)
            
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
draw_text_centered(draw, eng_cx, ENGINE_Y + 15, '🚗 投资银行自动驾驶引擎', eng_title_font, COLORS['engine_border'])
draw_text_centered(draw, eng_cx, ENGINE_Y + 45, '驱动模型=AI提示词 | 状态与计量分离 | 全部并发无流程', eng_sub_font, COLORS['text_light'])

tasks = [
    ('1', '发起项目撮合/承揽意向',
     '发起项目撮合意向，来源包括：员工发起、外部企业提交融资需求、投资机构推荐项目、资金方发布投资需求、委外顾问需求。生成标准化任务卡片，调用"任务组管理模型"组建任务组，并发调用资金方分类原子模型/合作方对接原子模型/持续督导原子模型做初步匹配，所有意向不判断可行性全部进入引擎'),
    ('2', '生成交易方案',
     '并发调用"投行项目类型原子模型"确定业务类型和交易结构，调用"项目筛选评估原子模型"评估企业质地和融资可行性，调用"投行团队匹配原子模型"匹配项目团队，调用"交易结构生成原子模型"设计融资方案/增信安排/退出机制/定价机制，调用"投行项目合规模型"完成合规校验'),
    ('3', '合作方准入与签约',
     '调用"合作方对接原子模型"区分已合作机构和新拓展机构，已合作的直接进入交易执行，新拓展的先办机构准入再开展业务，处理联合承销/联合投资/中介协作/政府对接，完成后签署合作协议/承销协议/投资协议'),
    ('4', '交易撮合启动',
     '调用"资金方分类原子模型"、"项目与资金匹配规则原子模型"进行自动撮合匹配找到目标资金方，调用"交易结构生成原子模型"生成路演材料和推介内容，经"投行项目合规模型"验证后，有固定关系的派发给对应销售，无关系的全平台抢单'),
    ('5', '项目执行与申报',
     '调用"项目执行动作原子模型"执行尽职调查、材料制作、监管申报、交割过户，调用"风险监测原子模型"监测项目进度和审核风险，调用"持续督导原子模型"启动督导服务框架'),
    ('6', '持续督导服务',
     '调用"持续督导原子模型"，事件驱动并发处理定期报告、重大事项、募集资金使用监督、股价异常波动、投资者关系管理、违规处理，自动生成督导工单'),
    ('7', '监督全过程管控',
     '监督模型贯穿全程并发运行，进度管控、质量检查、合规留痕、异常报警、推进督促、计量核算，调用"投行项目合规模型"留痕，只留痕报警督促不干预业务执行'),
    ('8', '贡献计量与收入分配',
     '项目闭环后调用"投行项目员工贡献计量分配原子模型"、"投行项目总绩效计量原子模型"，按四类业务（股权/债券/并购/资产证券化）分别计量，机器完成的不计量，只拆核心链条，中后台不参与分成，当期与递延结合'),
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
footer_text = '投资银行自动驾驶平台 v2.0 | 一套方法论、一套模型、套不同产品特征 | 开放→聚合→机制→产品'
draw_text_centered(draw, W/2, max(task_y, max_side_y) + 20, footer_text, footer_font, COLORS['footer'])

# 保存
output_path = '/root/.openclaw/workspace/diagrams/投资银行自动驾驶平台方案-v2.png'
img.save(output_path, 'PNG', dpi=(150, 150))
print(f'OK: {output_path}, size: {W}x{max(H, max(task_y, max_side_y) + 60)}')
