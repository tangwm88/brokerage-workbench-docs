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
draw_text_centered(draw, W/2, 25, '资产管理自动驾驶平台', title_font, COLORS['title'])
draw_text_centered(draw, W/2, 65, '基于产品、客户、规则等原子模型实现资产管理自动驾驶 | 对标贝莱德 | 行业级智能体产品', subtitle_font, COLORS['subtitle'])

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
        'title': '产品创设原子模型',
        'sec': 'sec1',
        'models': [
            {
                'title': '📐 资管产品设计原子模型',
                'tag': '7维',
                'items': [
                    ('产品类型', '权益/固收/混合/另类/FOF/量化'),
                    ('配置结构', '资产配置比例/投资策略/杠杆/衍生品'),
                    ('风险收益', '预期收益/最大回撤/波动率/夏普'),
                    ('期限安排', '封闭期/开放期/赎回条款/清算方式'),
                    ('规模目标', '最低成立/目标募集/上限/预警线'),
                    ('费率结构', '管理费/超额报酬/认申购费/销售服务费'),
                    ('投资限制', '投资范围/比例限制/集中度/流动性'),
                ]
            },
            {
                'title': '📊 同业比对原子模型',
                'tag': '6维',
                'items': [
                    ('产品池', '全市场资管产品按策略/风险分类'),
                    ('比对维度', '收益/回撤/夏普/费率/规模/经理业绩'),
                    ('业绩归因', '市场β/行业配置/个股选择/择时'),
                    ('配置差异', '与同类产品的资产配置/策略/风格差异'),
                    ('费率差异', '与同类产品的费率水平/计提差异'),
                    ('输出', '竞争优势/劣势分析/市场空白/定价建议'),
                ]
            },
            {
                'title': '🧮 收益测算原子模型',
                'tag': '6维',
                'items': [
                    ('预期收益', '基于历史数据/市场环境/策略容量测算'),
                    ('回撤压力', '极端情景(2008/2015/2020)最大回撤'),
                    ('场景模拟', '牛市/熊市/震荡市/黑天鹅事件'),
                    ('敏感性分析', '利率/汇率/股价/信用利差影响'),
                    ('流动性测算', '大额赎回情景流动性压力测试'),
                    ('容量测算', '策略容量上限/规模对收益影响'),
                ]
            },
            {
                'title': '👤 投资经理准入原子模型',
                'tag': '7维',
                'items': [
                    ('管理规模', '当前规模/历史变化/规模业绩匹配度'),
                    ('投资业绩', '近1/3/5年收益/超额/持续性/排名'),
                    ('风险控制', '最大回撤/波动率/下行风险/风险调整收益'),
                    ('投资策略', '策略类型/容量/稳定性/独特性'),
                    ('团队实力', '投研团队规模/核心成员稳定性/梯队'),
                    ('合规记录', '监管处罚/自律处分/合规运作'),
                    ('经营财务', '所在机构财务状况/盈利能力/资本实力'),
                ]
            },
        ]
    },
    {
        'title': '资金募集原子模型',
        'sec': 'sec2',
        'models': [
            {
                'title': '👥 客户分类原子模型',
                'tag': '6维',
                'items': [
                    ('个人分层', '高净值(≥300万)/超高净值(≥1000万)/家办'),
                    ('机构分类', '银行理财子/保险资管/券商资管/私募/企业'),
                    ('资金性质', '自有/受托/募集/专项/长期/短期'),
                    ('投资经验', '满2年/不满2年/专业投资者/普通投资者'),
                    ('风险承受', '保守/稳健/平衡/成长/进取(R1-R5)'),
                    ('投资偏好', '权益/固收/混合/另类/量化/ESG'),
                ]
            },
            {
                'title': '🎯 客户与产品匹配规则原子模型',
                'tag': '6项',
                'items': [
                    ('合规匹配', '合格投资者认定/投资经验/风险测评'),
                    ('投资能力', '资金规模与起投金额匹配/净资产要求'),
                    ('风险偏好', '客户风险等级与产品风险等级匹配'),
                    ('投资意愿', '客户投资倾向与产品策略匹配'),
                    ('投资期限', '客户资金期限与产品期限匹配'),
                    ('集中度', '单一客户比例限制/关联客户合并计算'),
                ]
            },
            {
                'title': '📝 内容推介生成原子模型',
                'tag': '7项',
                'items': [
                    ('合规宣传', '不得公开宣传收益/承诺保本/极端词汇'),
                    ('产品特征', '客观描述类型/配置/风险收益/期限/费率'),
                    ('风险揭示', '市场/信用/流动性/操作/策略风险'),
                    ('业绩展示', '过往业绩不代表未来/完整业绩区间'),
                    ('适配说明', '适合客户类型/风险要求/最低金额'),
                    ('发行安排', '募集期/成立条件/开放日/信息披露'),
                    ('冷静期提示', '认购后24小时冷静期/回访确认'),
                ]
            },
            {
                'title': '🏦 渠道准入原子模型',
                'tag': '6情形',
                'items': [
                    ('已准入银行', '总行/分行准入名单内直接办产品准入'),
                    ('新拓展银行', '先办机构准入(资质/尽调/协议)再产品准入'),
                    ('银行理财子', '满足委外要求/投资范围匹配/费率谈判'),
                    ('三方财富', '准入标准/合规要求/销售协议/培训认证'),
                    ('互联网平台', '监管许可/合规审查/技术对接/适当性'),
                    ('协议签署', '机构准入/产品准入/合作/销售协议'),
                ]
            },
        ]
    },
    {
        'title': '投资运作原子模型',
        'sec': 'sec3',
        'models': [
            {
                'title': '📋 投资运作动作原子模型',
                'tag': '5动作',
                'items': [
                    ('投资启动', '产品成立确认/资金到位/投资范围/策略确认'),
                    ('交易执行', '指令生成/审批/执行/成交确认/清算交收'),
                    ('持仓管理', '持仓监控/集中度控制/风险敞口/行业配置'),
                    ('估值核算', '每日估值/净值计算/会计核算/份额登记'),
                    ('信息披露', '定期报告/重大事项披露/净值披露/公告'),
                ]
            },
            {
                'title': '⚠️ 风险监测原子模型',
                'tag': '5维',
                'items': [
                    ('净值回撤', '当日≥3%预警/近周≥5%/历史≥10%报警'),
                    ('集中度', '单一标的≥10%/单一行业≥30%预警'),
                    ('流动性', '覆盖率<120%预警/大额赎回≥20%预警'),
                    ('合规风控', '投资范围超限/杠杆超限/限制违反'),
                    ('信用风险', '债券评级下调/发行人负面舆情'),
                ]
            },
            {
                'title': '🔧 持续服务原子模型',
                'tag': '6项',
                'items': [
                    ('定期报告', '季报/年报按时编制审核披露发送'),
                    ('净值波动', '当日≥3%或近周≥5%主动沟通客户'),
                    ('重大变化', '经理变更/策略调整/要素变更提前通知'),
                    ('大额赎回', '单笔≥10%或月累计≥30%主动沟通挽留'),
                    ('客户咨询', '24小时内响应/专业解答/记录归档'),
                    ('投诉处理', '2小时响应/48小时方案/全程留痕'),
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
                'title': '🛡️ 资管产品合规模型',
                'tag': '7项',
                'items': [
                    ('宣传合规', '不得公开宣传收益/承诺保本/极端词汇'),
                    ('合格投资者', '金融资产≥300万/收入≥50万/经验满2年'),
                    ('风险揭示', '充分揭示风险/签署风险揭示书'),
                    ('适当性匹配', '产品风险等级与客户承受能力匹配'),
                    ('购买回访', '签约24小时内购买意愿再确认'),
                    ('信息披露', '净值/定期报告/重大事项及时准确完整'),
                    ('投资运作合规', '投资范围/比例限制/杠杆比例符合监管'),
                ]
            },
            {
                'title': '👁️ 监督模型',
                'tag': '7项',
                'items': [
                    ('进度管控', '任务进度跟踪/节点检查/延期预警'),
                    ('质量检查', '输出物质量审核/合规检查/完整性验证'),
                    ('合规留痕', '全过程留痕/操作记录/审批记录'),
                    ('异常报警', '异常自动识别/分级报警/实时监测'),
                    ('推进督促', '任务滞留自动督促/升级处理'),
                    ('计量核算', '贡献计量/绩效核算/分配确认'),
                    ('独立监督', '独立于业务运作/直接向AI委员会报告'),
                ]
            },
            {
                'title': '⚖️ 员工贡献计量分配原子模型',
                'tag': '8类角色',
                'items': [
                    ('发起人/引入人', '引入规模×运行周期×引入费率0.03-0.05%'),
                    ('产品设计师', '管理费收入×15-20%'),
                    ('募集销售人', '实际募集金额×销售费率0.5-1.0%'),
                    ('投资经理', '管理费×40-50%+超额报酬×50-60%'),
                    ('筛选评估人', '一次性计提0.02-0.03%'),
                    ('投后管理人', '管理费×5-10%'),
                    ('协作支持人', '按支持贡献一次性或按期计提'),
                    ('平台运营方', '产品收入×10-15%'),
                ]
            },
            {
                'title': '📈 总绩效计量原子模型',
                'tag': '5类收入',
                'items': [
                    ('管理费收入', '提成20%/补贴10%'),
                    ('交易佣金', '20%×(实际佣金率-0.0001)'),
                    ('超额报酬收入', '提成20%/补贴10%'),
                    ('认/申购费', '提成100%'),
                    ('销售服务费', '提成50%/按年计提'),
                ]
            },
            {
                'title': '💰 准入标准费率原子模型',
                'tag': '按产品',
                'items': [
                    ('权益类管理费', '最低1.0%/目标1.5%'),
                    ('固收类管理费', '最低0.5%/目标0.75%'),
                    ('混合类管理费', '最低0.8%/目标1.2%'),
                    ('FOF管理费', '最低0.8%/目标1.0%'),
                    ('超额报酬分成', '最低超基准2%/目标超基准4%'),
                ]
            },
            {
                'title': '🔑 权限模型',
                'tag': '引擎',
                'items': [
                    ('任务组边界', '以任务组为边界隔离数据和模型'),
                    ('语料权限', '不同任务组访问不同语料库'),
                    ('授权失效', '任务结束后权限自动失效'),
                    ('访问留痕', '所有访问记录留痕可追溯'),
                ]
            },
            {
                'title': '📋 跟投评估模型',
                'tag': '模式五',
                'items': [
                    ('跟投比例', '评估合理跟投比例'),
                    ('风险评估', '评估跟投风险承受能力'),
                    ('资金来源', '核实跟投资金来源合法性'),
                    ('退出机制', '设计跟投退出机制和条件'),
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
footer_text = '资产管理自动驾驶平台 v3.0 | 一套方法论、一套模型、套不同产品特征 | 开放→聚合→机制→产品 | 对标贝莱德'
draw_text_centered(draw, W/2, max(task_y, max_side_y) + 20, footer_text, footer_font, COLORS['footer'])

# 保存
output_path = '/root/.openclaw/workspace/diagrams/资产管理自动驾驶平台方案-v3.png'
img.save(output_path, 'PNG', dpi=(150, 150))
print(f'OK: {output_path}, size: {W}x{max(H, max(task_y, max_side_y) + 60)}')
