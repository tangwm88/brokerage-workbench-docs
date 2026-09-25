#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_cell_shading(cell, color):
    """设置单元格背景色"""
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color)
    cell._tc.get_or_add_tcPr().append(shading)

def set_run_font(run, font_name='宋体', font_size=10.5, bold=False):
    """设置文字格式"""
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    run.font.size = Pt(font_size)
    run.font.bold = bold

def add_heading_paragraph(doc, text, font_size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER):
    """添加标题段落"""
    p = doc.add_paragraph()
    p.alignment = align
    run = p.add_run(text)
    set_run_font(run, font_size=font_size, bold=bold)
    return p

def add_normal_paragraph(doc, text, indent=True):
    """添加正文段落"""
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    set_run_font(run)
    return p

def add_bold_label_paragraph(doc, label, content=''):
    """添加带粗体标签的段落"""
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.line_spacing = 1.5
    run1 = p.add_run(label)
    set_run_font(run1, bold=True)
    if content:
        run2 = p.add_run(content)
        set_run_font(run2)
    return p

def main():
    doc = Document()
    
    # 设置页面边距
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3.17)
        section.right_margin = Cm(3.17)
    
    # 标题
    add_heading_paragraph(doc, '华创云信数字技术股份有限公司', font_size=18, bold=True)
    add_heading_paragraph(doc, 'AI事业委员会设立方案审议会议纪要', font_size=16, bold=True)
    
    # 会议基本信息
    doc.add_paragraph()  # 空行
    
    info_items = [
        ('会议名称：', 'AI事业委员会设立方案审议会议'),
        ('会议时间：', '2026年9月  日'),
        ('会议地点：', '公司会议室'),
        ('主持人：', '（主任委员/董事长）'),
        ('出席人员：', '汤文明、张迪侃、温从余、罗彤、段国成、黄涛、张洵、张健等'),
        ('列席人员：', '刘奕、齐玉健等'),
        ('记录人：', ''),
    ]
    
    for label, content in info_items:
        add_bold_label_paragraph(doc, label, content)
    
    # 分隔线
    doc.add_paragraph('_' * 50)
    
    # 一、会议议题
    add_heading_paragraph(doc, '一、会议议题', font_size=14, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT)
    
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run('审议《华创云信数字技术股份有限公司AI事业委员会组织方案》及配套文件《AI团队岗位职级与薪酬体系详表》，并就以下事项进行决策：')
    set_run_font(run)
    
    topics = [
        'AI事业委员会的组织架构与运行机制',
        'AI产品工作组设置及人员安排',
        'AI团队职级薪酬体系',
        '首批AI团队成员入职安排',
    ]
    for i, topic in enumerate(topics, 1):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(f'{i}、{topic}')
        set_run_font(run)
    
    # 二、审议事项及决议
    add_heading_paragraph(doc, '二、审议事项及决议', font_size=14, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT)
    
    # （一）审议通过AI事业委员会设立方案
    add_heading_paragraph(doc, '（一）审议通过AI事业委员会设立方案', font_size=12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT)
    
    add_bold_label_paragraph(doc, '1. 委员会定位')
    
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run('统筹推进企业自动驾驶操作系统、证券金融、文旅产业及企业服务等AI产品的研发方向、项目统筹、开发及推广运营；对AI相关重大事项进行统筹管理与决策。')
    set_run_font(run)
    
    add_bold_label_paragraph(doc, '2. 委员构成')
    
    items = [
        '委员会不少于5人组成，设主任委员1人，副主任委员根据需要设置',
        '委员从公司内部相关部门、子公司技术骨干或外部专家中遴选，由公司聘任',
        '任期为三年，可连任',
    ]
    for item in items:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run('• ' + item)
        set_run_font(run)
    
    add_bold_label_paragraph(doc, '3. 主要功能')
    
    functions = [
        ('方向决策：', '确定企业自动驾驶操作系统及各类智能体应用的研发方向、技术路线与项目统筹'),
        ('方案评审：', '确定证券金融、文旅产业、企业服务等应用产品方案'),
        ('运营决策：', '负责AI产品的研发、推广与运营决策'),
        ('资源调配：', '统一调配人员、算力等资源'),
        ('采购审批：', '审批外部工具、第三方服务的采购'),
        ('人事审批：', '审批团队引进及负责人任免'),
        ('投资审议：', '审议AI相关的投资事项'),
    ]
    for label, content in functions:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        run1 = p.add_run('• ' + label)
        set_run_font(run1, bold=True)
        run2 = p.add_run(content)
        set_run_font(run2)
    
    add_bold_label_paragraph(doc, '4. 议事规则')
    
    rules = [
        '会议须有三分之二以上的委员出席方可举行',
        '决议须经全体委员过半数通过',
        '审议结果形成书面文件，由参加会议的委员签字后执行',
    ]
    for rule in rules:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run('• ' + rule)
        set_run_font(run)
    
    # （二）审议通过AI产品工作组设置方案
    add_heading_paragraph(doc, '（二）审议通过AI产品工作组设置方案', font_size=12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT)
    
    add_bold_label_paragraph(doc, '1. 工作组设置')
    
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run('委员会下设四个工作组：证券金融工作组、文旅产业工作组、企业服务工作组、产品运营工作组')
    set_run_font(run)
    
    add_bold_label_paragraph(doc, '2. 组织原则')
    
    principles = [
        ('统一指挥：', '实行小团队作战，所有团队统一在委员会指挥下，团队长直接面向委员会，取消层层汇报、层层请示'),
        ('产品负责制：', '以AI产品为单元组建组织，每个产品设一名CEO（产品全闭环负责人），全权负责该产品的设计、开发、运营及组织协同'),
        ('主动请战：', '除组织分派外，任何人可主动申请承担产品或项目，委员会评估确定'),
    ]
    for label, content in principles:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        run1 = p.add_run('• ' + label)
        set_run_font(run1, bold=True)
        run2 = p.add_run(content)
        set_run_font(run2)
    
    add_bold_label_paragraph(doc, '3. 人员安排（首批）')
    
    # 创建表格
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # 表头
    hdr_cells = table.rows[0].cells
    headers = ['工作组', '职务', '人员']
    for i, header in enumerate(headers):
        hdr_cells[i].text = header
        set_cell_shading(hdr_cells[i], 'D9E2F3')
        for paragraph in hdr_cells[i].paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                set_run_font(run, bold=True)
    
    # 表格数据
    table_data = [
        ('AI企业服务组', '联席CEO', '罗彤、温从余'),
        ('AI文旅产业组', '联席CEO', '张洵、段国成'),
        ('证券金融组', '联席助理CEO', '刘奕、齐玉健'),
        ('产品运营组', 'COO', '黄涛'),
    ]
    
    for row_data in table_data:
        row_cells = table.add_row().cells
        for i, text in enumerate(row_data):
            row_cells[i].text = text
            for paragraph in row_cells[i].paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in paragraph.runs:
                    set_run_font(run)
    
    doc.add_paragraph()  # 空行
    
    # （三）审议通过AI团队岗位职级与薪酬体系
    add_heading_paragraph(doc, '（三）审议通过AI团队岗位职级与薪酬体系', font_size=12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT)
    
    add_bold_label_paragraph(doc, '1. 职级框架')
    
    items = [
        '设立A1至A8共八个职级，按实际付出与贡献动态匹配及调整',
        '团队内各角色均纳入A1-A8职级体系，不再单独设管理序列',
    ]
    for item in items:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run('• ' + item)
        set_run_font(run)
    
    add_bold_label_paragraph(doc, '2. 角色分类')
    
    # 创建角色分类表格
    table2 = doc.add_table(rows=1, cols=3)
    table2.style = 'Table Grid'
    table2.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    hdr_cells = table2.rows[0].cells
    headers = ['类别', '角色', '职级范围']
    for i, header in enumerate(headers):
        hdr_cells[i].text = header
        set_cell_shading(hdr_cells[i], 'D9E2F3')
        for paragraph in hdr_cells[i].paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                set_run_font(run, bold=True)
    
    role_data = [
        ('产品研发类', 'AI工程师', 'A1-A4'),
        ('产品研发类', '助理CEO', 'A3-A5'),
        ('产品研发类', 'AI产品CEO', 'A5-A8'),
        ('产品运营类', 'AI运营经理', 'A1-A4'),
        ('产品运营类', '助理COO', 'A3-A5'),
        ('产品运营类', 'AI产品运营COO', 'A5-A8'),
    ]
    
    for row_data in role_data:
        row_cells = table2.add_row().cells
        for i, text in enumerate(row_data):
            row_cells[i].text = text
            for paragraph in row_cells[i].paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in paragraph.runs:
                    set_run_font(run)
    
    doc.add_paragraph()  # 空行
    
    add_bold_label_paragraph(doc, '3. 考核原则')
    
    items = [
        '考核以产品结果为主，核心标准为"产品做出来、运营起来"',
        '以最终客户为导向，聚焦产品落地和用户价值，不直接考核营收指标',
    ]
    for item in items:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run('• ' + item)
        set_run_font(run)
    
    add_bold_label_paragraph(doc, '4. 激励机制')
    
    # 创建激励表格
    table3 = doc.add_table(rows=1, cols=3)
    table3.style = 'Table Grid'
    table3.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    hdr_cells = table3.rows[0].cells
    headers = ['职级', '优秀', '称职']
    for i, header in enumerate(headers):
        hdr_cells[i].text = header
        set_cell_shading(hdr_cells[i], 'D9E2F3')
        for paragraph in hdr_cells[i].paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                set_run_font(run, bold=True)
    
    incentive_data = [
        ('A4-A8（首席/助理首席）', '3倍月薪奖金+4倍月薪股权激励', '2倍月薪奖金+3倍月薪股权激励'),
        ('A1-A3（基础人员）', '6倍月薪奖金', '3倍月薪奖金（无股权）'),
    ]
    
    for row_data in incentive_data:
        row_cells = table3.add_row().cells
        for i, text in enumerate(row_data):
            row_cells[i].text = text
            for paragraph in row_cells[i].paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in paragraph.runs:
                    set_run_font(run)
    
    doc.add_paragraph()  # 空行
    
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run('激励股权为融汇金信股权，或通过奖励员工持股份额等方式参与华创云信员工持股。')
    set_run_font(run)
    
    # （四）审议通过首批AI团队成员入职安排
    add_heading_paragraph(doc, '（四）审议通过首批AI团队成员入职安排', font_size=12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT)
    
    add_bold_label_paragraph(doc, '1. 拟直接入职华创云信共12人')
    
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run('人员名单：黄涛、刘志璇、曲俊宇、周宇、宋珺、王琳、郭颖、刘欲晓、钟祥宇、许娇、刘嘉豪、王禹昊')
    set_run_font(run)
    
    add_bold_label_paragraph(doc, '2. 组织调度')
    
    items = [
        'AI团队在集团层面统一组织',
        '人员从华创证券、云码通等内部团队筛选组织和调度',
        '加入AI团队的人员可直接转岗入职华创云信，也可在当前岗位上接受AI团队统一组织调度',
    ]
    for item in items:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run('• ' + item)
        set_run_font(run)
    
    # 三、会议决议
    add_heading_paragraph(doc, '三、会议决议', font_size=14, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT)
    
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run('经出席会议委员审议表决，一致通过以下决议：')
    set_run_font(run)
    
    resolutions = [
        '批准设立华创云信数字技术股份有限公司AI事业委员会',
        '批准《华创云信数字技术股份有限公司AI事业委员会组织方案》',
        '批准《AI团队岗位职级与薪酬体系详表》',
        '批准首批AI产品工作组设置及人员安排',
        '批准首批12名AI团队成员入职华创云信',
    ]
    for i, res in enumerate(resolutions, 1):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        run1 = p.add_run(f'{i}、')
        set_run_font(run1, bold=True)
        run2 = p.add_run(res)
        set_run_font(run2)
    
    # 四、签批意见
    add_heading_paragraph(doc, '四、签批意见', font_size=14, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT)
    
    # 创建签批表格
    table4 = doc.add_table(rows=6, cols=5)
    table4.style = 'Table Grid'
    table4.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # 设置列宽
    widths = [Cm(2.5), Cm(2.5), Cm(2.5), Cm(2.5), Cm(2.5)]
    for row in table4.rows:
        for idx, width in enumerate(widths):
            row.cells[idx].width = width
    
    # 表头
    hdr_cells = table4.rows[0].cells
    headers = ['签批人', '职务', '意见', '签字', '日期']
    for i, header in enumerate(headers):
        hdr_cells[i].text = header
        set_cell_shading(hdr_cells[i], 'D9E2F3')
        for paragraph in hdr_cells[i].paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                set_run_font(run, bold=True)
    
    # 签批数据
    sign_data = [
        ('', '主任委员', '同意', '', ''),
        ('', '委员', '同意', '', ''),
        ('', '委员', '同意', '', ''),
        ('', '委员', '同意', '', ''),
        ('', '委员', '同意', '', ''),
    ]
    
    for i, row_data in enumerate(sign_data, 1):
        row_cells = table4.rows[i].cells
        for j, text in enumerate(row_data):
            row_cells[j].text = text
            for paragraph in row_cells[j].paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in paragraph.runs:
                    set_run_font(run)
    
    doc.add_paragraph()  # 空行
    
    # 附件
    add_heading_paragraph(doc, '附件：', font_size=12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT)
    
    attachments = [
        '《华创云信数字技术股份有限公司AI事业委员会组织方案》',
        '《AI团队岗位职级与薪酬体系详表》',
        '《华创云信AI团队组建方案》',
    ]
    for i, att in enumerate(attachments, 1):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(f'{i}、{att}')
        set_run_font(run)
    
    doc.add_paragraph()  # 空行
    doc.add_paragraph()  # 空行
    
    # 落款
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run('本纪要一式  份，与会人员各执一份，存档一份。')
    set_run_font(run)
    
    doc.add_paragraph()  # 空行
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run('华创云信数字技术股份有限公司 AI事业委员会')
    set_run_font(run, bold=True)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run('2026年9月  日')
    set_run_font(run)
    
    # 保存文档
    output_path = '/root/.openclaw/workspace/docs/AI事业委员会会议纪要-上会签批版.docx'
    doc.save(output_path)
    print(f'Word文档已生成: {output_path}')

if __name__ == '__main__':
    main()
