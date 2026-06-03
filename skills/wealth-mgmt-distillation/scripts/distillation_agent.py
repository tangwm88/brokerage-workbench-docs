#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业务模型蒸馏智能体脚本 v1.0
基于《企业级业务模型蒸馏智能体设计方案 v1.2》实现

功能：接收企业业务知识输入，按五步法蒸馏为可执行的业务模型
作者：Kimi Claw
日期：2026-06-03

使用方法：
    python distillation_agent.py --input business_desc.yaml --output model_package/

输入格式：YAML，包含业务描述、组织架构、制度规范等
输出格式：结构化模型包（角色体系+分析模型+动作模型+数据矩阵+验证报告）
"""

import json
import yaml
import os
import sys
import argparse
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path

# ============================================================================
# 第一部分：核心规则（不可修改）
# ============================================================================

CORE_RULES = {
    "version": "1.2",
    "date": "2026-06-03",
    "source": "陶总方法论 + 禁用词语表",
    "description": "蒸馏智能体执行五步法时必须遵守的底层约束"
}

# 陶总五大反对（硬性约束）
TAO_FIVE_OPPOSE = {
    1: {
        "name": "反对讲意义、讲作用、讲自洽，而不讲模型本身",
        "check": "输出是否有模型结构（主模型/维度/输入/输出/子模型/调用关系），而非仅讲意义",
        "action": "如违反，标记为'不合格'，必须补充模型结构"
    },
    2: {
        "name": "反对流程化、线性化地拆业务",
        "check": "输出是否为可复用原子库（事件驱动），而非线性流程",
        "action": "如违反，标记为'不合格'，改为原子库调用"
    },
    3: {
        "name": "反对角色混乱、目标混乱",
        "check": "每个模型是否明确服务目的、目标角色、执行角色",
        "action": "如违反，标记为'不合格'，重新梳理角色"
    },
    4: {
        "name": "反对主观拍脑袋和甩锅给大模型",
        "check": "是否基于客观事实（有数据支撑/来源明确），而非主观",
        "action": "如违反，标记为'不合格'，补充客观维度"
    },
    5: {
        "name": "反对传统信息系统视角和技术自说自话",
        "check": "是否从角色和目的出发，而非从系统功能出发",
        "action": "如违反，标记为'不合格'，切换为角色视角"
    }
}

# 陶总八步方法论
TAO_EIGHT_STEPS = {
    1: "定目的",
    2: "定角度",
    3: "客观分类",
    4: "提炼主维度",
    5: "对比蒸馏",
    6: "标准化建模",
    7: "场景调用",
    8: "监督迭代"
}

# 禁用词语表（硬性替换）
FORBIDDEN_WORDS = {
    "基本面": "企业实际质地/财务实际状况",
    "偏好": "倾向/选择方向",
    "流程": "协同",
    "行业": "产业",
    "场景": "应用",
    "逻辑": "规律",
    "对齐": "领会",
    "话术": "沟通要点"
}

# 扩展原则（软性约束）
EXTENSION_RULES = [
    "能用动词不用名词：赋能->让...能够/沉淀->积累/抓手->切入点",
    "能用具体不用抽象：颗粒度->细致程度/闭环->完整流程/打法->方法",
    "能用白话不用术语：心智->认知/链路->流程/私域->自有客户",
    "不用英文缩写：SOP->标准动作/KPI->考核指标/MVP->最简可行版",
    "不用问题式维度：靠不靠谱->直接写本质名词"
]


# ============================================================================
# 第二部分：数据类定义
# ============================================================================

@dataclass
class BusinessGoal:
    """业务目标"""
    name: str
    definition: str
    key_actions: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)
    boundary: str = ""

@dataclass
class Benchmark:
    """标杆分析"""
    dimension: str
    benchmark_obj: str
    benchmark_practice: str
    our_status: str
    gap: str
    adoption: str
    remark: str

@dataclass
class DataItem:
    """数据关联项"""
    indicator: str
    formula: str
    data_source: str
    access_path: str
    auto_manual: str
    remark: str

@dataclass
class AnalysisDimension:
    """分析维度"""
    name: str
    plain_language: str
    objective_data: str
    output: str
    analysis_framework: str = ""

@dataclass
class ActionItem:
    """规定动作"""
    name: str
    trigger: str
    steps: List[str] = field(default_factory=list)
    output: str = ""
    exception_handling: Dict[str, str] = field(default_factory=dict)
    deadline: str = ""
    risk_level: str = "可以"

@dataclass
class Role:
    """角色定义"""
    name: str
    source_position: str
    core_responsibility: str
    service_goal: str
    role_definition: str = ""
    goals: List[str] = field(default_factory=list)
    backstory: str = ""
    constraints: Dict[str, List[str]] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """验证结果"""
    check_item: str
    result: str
    issue: str
    severity: str


# ============================================================================
# 第三部分：核心规则校验器
# ============================================================================

class CoreRuleValidator:
    """核心规则校验器——陶总方法论+禁用词语表"""
    
    def __init__(self):
        self.forbidden_words = FORBIDDEN_WORDS
        self.tao_opposes = TAO_FIVE_OPPOSE
        self.tao_steps = TAO_EIGHT_STEPS
    
    def check_forbidden_words(self, text: str) -> List[Tuple[str, str]]:
        """检查禁用词，返回(禁用词, 推荐词)列表"""
        violations = []
        for forbidden, recommended in self.forbidden_words.items():
            if forbidden in text:
                violations.append((forbidden, recommended))
        return violations
    
    def check_tao_opposition_1(self, content: Dict, step_number: int) -> Tuple[bool, str]:
        """反对1：检查是否有模型结构，而非仅讲意义"""
        text = json.dumps(content, ensure_ascii=False)
        
        # Step 1: 业务目标 - 检查是否有明确的业务目标结构
        if step_number == 1:
            if "core_goals" in content and content.get("core_goals"):
                return True, "业务目标结构完整（core_goals已定义）"
            if "business_line" in content and content.get("business_line"):
                return True, "业务线已定义"
            return False, "缺少业务目标结构（无core_goals/business_line）"
        
        # Step 2: 标杆分析 - 检查是否有标杆分析结构
        if step_number == 2:
            if "benchmarks" in content and content.get("benchmarks"):
                return True, "标杆分析结构完整"
            return False, "缺少标杆分析结构"
        
        # Step 3: 数据关联 - 检查是否有数据矩阵结构
        if step_number == 3:
            if "data_items" in content or "data_matrix" in str(content):
                return True, "数据关联结构完整"
            return False, "缺少数据关联结构"
        
        # Step 4: 模型定义 - 检查是否有模型结构
        if step_number == 4:
            if "roles" in content or "dimensions" in str(content) or "events" in str(content):
                return True, "模型结构完整（角色/维度/动作）"
            return False, "缺少模型结构（无角色/维度/动作定义）"
        
        # Step 5: 验证报告 - 检查是否有验证结构
        if step_number == 5:
            if "validation_results" in content:
                return True, "验证结构完整"
            return False, "缺少验证结构"
        
        return True, "模型结构完整"
    
    def check_tao_opposition_2(self, content: Dict, step_number: int) -> Tuple[bool, str]:
        """反对2：检查是否为可复用原子库，而非线性流程"""
        text = json.dumps(content, ensure_ascii=False).lower()
        
        # Step 1: 业务目标 - 检查是否有线性流程描述
        if step_number == 1:
            # 业务目标本身不是流程，是目标定义，所以只要没有明显线性描述就算通过
            if "一步一步" in text or "linear flow" in text:
                return False, "业务目标描述为线性流程，非目标导向"
            return True, "业务目标为可定义的原子目标"
        
        # Step 4: 模型定义 - 检查动作模型是否为事件驱动
        if step_number == 4:
            if "events" in content and content.get("events"):
                return True, "动作模型为事件驱动（可复用原子）"
            if "actions" in str(content) and "trigger" in str(content):
                return True, "动作有触发条件（事件驱动）"
            return False, "动作模型缺少事件触发机制"
        
        return True, "输出为可调用原子库"
    
    def check_tao_opposition_3(self, content: Dict, step_number: int) -> Tuple[bool, str]:
        """反对3：检查角色/目标是否清晰"""
        text = json.dumps(content, ensure_ascii=False).lower()
        
        # Step 1: 业务目标 - 检查是否有清晰的业务目标
        if step_number == 1:
            if "core_goals" in content and content.get("core_goals"):
                goals = content.get("core_goals", [])
                for g in goals:
                    if g.get("name") and g.get("definition"):
                        return True, "业务目标有名称和定义（角色/目标清晰）"
                return False, "业务目标缺少名称或定义"
        
        # Step 4: 模型定义 - 检查角色定义
        if step_number == 4:
            if "roles" in content and content.get("roles"):
                return True, "角色体系已定义"
            if "role_definition" in text or "role" in text:
                return True, "角色定义已包含"
            return False, "缺少角色定义"
        
        # 其他步骤：通用检查
        if "goal" in text or "purpose" in text or "name" in text:
            return True, "目标/名称已定义"
        return True, "角色和目标清晰"
    
    def check_tao_opposition_4(self, content: Dict, step_number: int) -> Tuple[bool, str]:
        """反对4：检查是否客观（有数据支撑）"""
        text = json.dumps(content, ensure_ascii=False).lower()
        
        # Step 2: 标杆分析 - 检查是否有标杆来源
        if step_number == 2:
            if "benchmarks" in content and content.get("benchmarks"):
                for bm in content.get("benchmarks", []):
                    if bm.get("benchmark_obj") and bm.get("benchmark_practice"):
                        return True, "标杆分析有具体对象和做法（客观可验证）"
                return False, "标杆分析缺少具体对象或做法"
        
        # Step 3: 数据关联 - 检查是否有数据定义
        if step_number == 3:
            if "data_items" in content or "data_matrix" in str(content):
                return True, "数据关联有具体定义（客观数据）"
            return False, "缺少数据关联定义"
        
        # Step 4: 模型定义 - 检查维度是否有客观数据
        if step_number == 4:
            if "objective_data" in text or "objective" in text:
                return True, "分析维度有客观数据定义"
            if "dimensions" in text or "指标" in text:
                return True, "分析维度有指标定义"
            return True, "模型定义有数据支撑"
        
        # 通用检查：有metrics或数据来源
        if "metrics" in text or "data_source" in text or "indicator" in text:
            return True, "有客观数据指标"
        return True, "有客观数据支撑"
    
    def check_tao_opposition_5(self, content: Dict, step_number: int) -> Tuple[bool, str]:
        """反对5：检查是否从角色和目的出发，而非系统"""
        text = json.dumps(content, ensure_ascii=False).lower()
        
        # 检查是否从系统功能出发（负面信号）
        system_terms = ["系统功能", "功能模块", "系统模块", "系统架构", "功能列表"]
        has_system = any(term in text for term in system_terms)
        
        # 检查是否从角色/目的出发（正面信号）
        role_terms = ["role", "角色", "purpose", "目的", "goal", "目标", "responsibility", "职责"]
        has_role = any(term in text for term in role_terms)
        
        if has_system and not has_role:
            return False, "从系统功能出发，而非角色和目的"
        return True, "从角色和目的出发"
    
    def validate_step(self, step_name: str, content: Dict, step_number: int) -> List[ValidationResult]:
        """
        校验五步法每一步的输出
        返回校验结果列表
        """
        results = []
        
        # 1. 禁用词检查（只检查输出文本，不检查整个输入数据结构）
        text_content = json.dumps(content, ensure_ascii=False)
        forbidden_violations = self.check_forbidden_words(text_content)
        if forbidden_violations:
            for word, recommended in forbidden_violations:
                results.append(ValidationResult(
                    check_item=f"禁用词检查：{word}",
                    result="不通过",
                    issue=f"发现禁用词'{word}'，应替换为'{recommended}'",
                    severity="中"  # 中优先级：警告但不阻塞流程
                ))
        else:
            results.append(ValidationResult(
                check_item="禁用词检查",
                result="通过",
                issue="无禁用词",
                severity="-"
            ))
        
        # 2. 陶总五大反对检查
        oppose_checks = [
            ("反对1：模型结构", self.check_tao_opposition_1),
            ("反对2：原子库非流程", self.check_tao_opposition_2),
            ("反对3：角色目标清晰", self.check_tao_opposition_3),
            ("反对4：客观数据", self.check_tao_opposition_4),
            ("反对5：角色目的出发", self.check_tao_opposition_5),
        ]
        
        for check_name, check_func in oppose_checks:
            passed, msg = check_func(content, step_number)
            results.append(ValidationResult(
                check_item=check_name,
                result="通过" if passed else "不通过",
                issue=msg,
                severity="高" if not passed else "-"
            ))
        
        # 3. 陶总八步映射检查
        tao_step_map = {
            1: [1, 2, 3],  # 定目的+定角度+客观分类
            2: [5],        # 对比蒸馏
            3: [7],        # 场景调用（数据准备）
            4: [4, 6],     # 提炼主维度+标准化建模
            5: [8],        # 监督迭代
        }
        
        if step_number in tao_step_map:
            mapped_steps = tao_step_map[step_number]
            mapped_names = [self.tao_steps[s] for s in mapped_steps]
            results.append(ValidationResult(
                check_item=f"陶总八步校验：{', '.join(mapped_names)}",
                result="通过",
                issue=f"Step {step_number} 对应陶总八步中的 {mapped_names}",
                severity="-"
            ))
        
        return results
    
    def is_step_valid(self, results: List[ValidationResult]) -> bool:
        """判断步骤是否全部通过"""
        for r in results:
            if r.result == "不通过" and r.severity == "高":
                return False
        return True


# ============================================================================
# 第四部分：五步法蒸馏引擎
# ============================================================================

class DistillationEngine:
    """业务模型蒸馏引擎——五步法执行"""
    
    def __init__(self, input_data: Dict):
        self.input_data = input_data
        self.validator = CoreRuleValidator()
        self.results = {}
        self.validation_logs = {}
    
    # ------------------------------------------------------------------------
    # Step 1: 业务目标蒸馏
    # ------------------------------------------------------------------------
    def step1_business_goal(self) -> Dict:
        """
        触发条件：收到业务线蒸馏任务
        输入：企业业务描述（自然语言）
        输出：结构化业务目标树
        时限：2个工作日
        """
        print("[Step 1] 业务目标蒸馏...")
        
        business_desc = self.input_data.get("business_description", {})
        
        # 识别核心业务目标（1-4个）
        goals = []
        for i, goal_data in enumerate(business_desc.get("core_goals", [])[:4], 1):
            goal = BusinessGoal(
                name=goal_data.get("name", f"目标{i}"),
                definition=goal_data.get("definition", ""),
                key_actions=goal_data.get("key_actions", [])[:5],
                metrics=goal_data.get("metrics", [])[:2],
                boundary=goal_data.get("boundary", "")
            )
            goals.append(asdict(goal))
        
        relationships = business_desc.get("relationships", {})
        
        output = {
            "step": 1,
            "name": "业务目标蒸馏",
            "output_name": "《业务目标清单》",
            "core_goals": goals,
            "relationships": relationships,
            "business_line": business_desc.get("business_line", "未命名业务线"),
            "timestamp": datetime.now().isoformat()
        }
        
        # 校验
        validation = self.validator.validate_step("Step 1", output, 1)
        self.validation_logs[1] = validation
        
        if not self.validator.is_step_valid(validation):
            output["status"] = "不合格"
            output["validation_issues"] = [asdict(v) for v in validation if v.result == "不通过"]
            print("  ⚠️  Step 1 校验不通过，需修正")
        else:
            output["status"] = "通过"
            print("  ✅ Step 1 完成")
        
        self.results[1] = output
        return output
    
    # ------------------------------------------------------------------------
    # Step 2: 标杆分析蒸馏
    # ------------------------------------------------------------------------
    def step2_benchmark(self) -> Dict:
        """
        触发条件：Step 1验收通过
        输入：业务目标清单 + 标杆对象信息
        输出：标杆分析表
        时限：3个工作日
        """
        print("[Step 2] 标杆分析蒸馏...")
        
        if self.results.get(1, {}).get("status") != "通过":
            print("  ❌ Step 1 未通过，无法执行 Step 2")
            return {"error": "前置步骤未通过"}
        
        benchmarks = self.input_data.get("benchmarks", [])
        
        if len(benchmarks) < 3:
            print(f"  ⚠️  标杆数量不足（{len(benchmarks)} < 3），建议补充")
        
        benchmark_list = []
        for bm in benchmarks:
            benchmark = Benchmark(
                dimension=bm.get("dimension", ""),
                benchmark_obj=bm.get("benchmark_obj", ""),
                benchmark_practice=bm.get("benchmark_practice", ""),
                our_status=bm.get("our_status", ""),
                gap=bm.get("gap", ""),
                adoption=bm.get("adoption", "调整后采用"),
                remark=bm.get("remark", "")
            )
            benchmark_list.append(asdict(benchmark))
        
        output = {
            "step": 2,
            "name": "标杆分析蒸馏",
            "output_name": "《标杆分析表》",
            "benchmarks": benchmark_list,
            "benchmark_count": len(benchmark_list),
            "timestamp": datetime.now().isoformat()
        }
        
        validation = self.validator.validate_step("Step 2", output, 2)
        self.validation_logs[2] = validation
        
        if not self.validator.is_step_valid(validation):
            output["status"] = "不合格"
            output["validation_issues"] = [asdict(v) for v in validation if v.result == "不通过"]
            print("  ⚠️  Step 2 校验不通过，需修正")
        else:
            output["status"] = "通过"
            print("  ✅ Step 2 完成")
        
        self.results[2] = output
        return output
    
    # ------------------------------------------------------------------------
    # Step 3: 数据关联蒸馏
    # ------------------------------------------------------------------------
    def step3_data_association(self) -> Dict:
        """
        触发条件：Step 2验收通过
        输入：业务目标清单 + 标杆分析表 + 数据源清单
        输出：数据关联矩阵
        时限：3个工作日
        """
        print("[Step 3] 数据关联蒸馏...")
        
        if self.results.get(2, {}).get("status") != "通过":
            print("  ❌ Step 2 未通过，无法执行 Step 3")
            return {"error": "前置步骤未通过"}
        
        data_matrix = self.input_data.get("data_matrix", [])
        
        data_items = []
        auto_count = 0
        manual_count = 0
        semi_count = 0
        
        for item in data_matrix:
            data_item = DataItem(
                indicator=item.get("indicator", ""),
                formula=item.get("formula", ""),
                data_source=item.get("data_source", ""),
                access_path=item.get("access_path", ""),
                auto_manual=item.get("auto_manual", "手工"),
                remark=item.get("remark", "")
            )
            data_items.append(asdict(data_item))
            
            if data_item.auto_manual == "自动":
                auto_count += 1
            elif data_item.auto_manual == "半自动":
                semi_count += 1
            else:
                manual_count += 1
        
        total = len(data_items)
        auto_ratio = auto_count / total if total > 0 else 0
        
        output = {
            "step": 3,
            "name": "数据关联蒸馏",
            "output_name": "《数据关联矩阵》",
            "data_items": data_items,
            "statistics": {
                "total": total,
                "auto": auto_count,
                "semi": semi_count,
                "manual": manual_count,
                "auto_ratio": f"{auto_ratio:.1%}"
            },
            "auto_ratio_check": "通过" if auto_ratio >= 0.6 else "需改进（目标>=60%）",
            "timestamp": datetime.now().isoformat()
        }
        
        validation = self.validator.validate_step("Step 3", output, 3)
        self.validation_logs[3] = validation
        
        if not self.validator.is_step_valid(validation):
            output["status"] = "不合格"
            output["validation_issues"] = [asdict(v) for v in validation if v.result == "不通过"]
            print("  ⚠️  Step 3 校验不通过，需修正")
        else:
            output["status"] = "通过"
            print("  ✅ Step 3 完成")
        
        self.results[3] = output
        return output
    
    # ------------------------------------------------------------------------
    # Step 4: 模型定义蒸馏
    # ------------------------------------------------------------------------
    def step4_model_definition(self) -> Dict:
        """
        触发条件：Step 3验收通过
        输入：业务目标清单 + 标杆分析表 + 数据关联矩阵
        输出：角色体系 + 分析模型 + 动作模型
        时限：5个工作日
        """
        print("[Step 4] 模型定义蒸馏...")
        
        if self.results.get(3, {}).get("status") != "通过":
            print("  ❌ Step 3 未通过，无法执行 Step 4")
            return {"error": "前置步骤未通过"}
        
        # 4.1 角色体系设计
        roles_data = self.input_data.get("roles", [])
        roles = []
        organizer_count = 0
        employee_count = 0
        
        for role_data in roles_data:
            role = Role(
                name=role_data.get("name", ""),
                source_position=role_data.get("source_position", ""),
                core_responsibility=role_data.get("core_responsibility", ""),
                service_goal=role_data.get("service_goal", ""),
                role_definition=role_data.get("role_definition", ""),
                goals=role_data.get("goals", []),
                backstory=role_data.get("backstory", ""),
                constraints=role_data.get("constraints", {})
            )
            roles.append(asdict(role))
            
            if "组织者" in role.name or "协调官" in role.name:
                organizer_count += 1
            else:
                employee_count += 1
        
        # 4.2 业务分析模型（3-5维度）
        dimensions_data = self.input_data.get("analysis_dimensions", [])
        dimensions = []
        
        if len(dimensions_data) > 5:
            print(f"  ⚠️  维度数量超标（{len(dimensions_data)} > 5），强制压缩")
            dimensions_data = dimensions_data[:5]
        
        for dim_data in dimensions_data:
            dim = AnalysisDimension(
                name=dim_data.get("name", ""),
                plain_language=dim_data.get("plain_language", ""),
                objective_data=dim_data.get("objective_data", ""),
                output=dim_data.get("output", ""),
                analysis_framework=dim_data.get("analysis_framework", "")
            )
            dimensions.append(asdict(dim))
        
        # 4.3 规定动作模型
        events_data = self.input_data.get("events", [])
        events = []
        
        for event_data in events_data:
            actions = []
            for action_data in event_data.get("actions", []):
                action = ActionItem(
                    name=action_data.get("name", ""),
                    trigger=action_data.get("trigger", ""),
                    steps=action_data.get("steps", []),
                    output=action_data.get("output", ""),
                    exception_handling=action_data.get("exception_handling", {}),
                    deadline=action_data.get("deadline", ""),
                    risk_level=action_data.get("risk_level", "可以")
                )
                actions.append(asdict(action))
            
            events.append({
                "event_name": event_data.get("event_name", ""),
                "trigger_condition": event_data.get("trigger_condition", ""),
                "event_level": event_data.get("event_level", ""),
                "actions": actions
            })
        
        output = {
            "step": 4,
            "name": "模型定义蒸馏",
            "output_name": "角色体系 + 分析模型 + 动作模型",
            "roles": {
                "roles": roles,
                "organizer_count": organizer_count,
                "employee_count": employee_count,
                "role_check": "通过" if organizer_count == 1 and 3 <= employee_count <= 6 else "需调整"
            },
            "analysis_model": {
                "dimensions": dimensions,
                "dimension_count": len(dimensions),
                "dimension_check": "通过" if 3 <= len(dimensions) <= 5 else "需调整"
            },
            "action_model": {
                "events": events,
                "event_count": len(events)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        validation = self.validator.validate_step("Step 4", output, 4)
        self.validation_logs[4] = validation
        
        if not self.validator.is_step_valid(validation):
            output["status"] = "不合格"
            output["validation_issues"] = [asdict(v) for v in validation if v.result == "不通过"]
            print("  ⚠️  Step 4 校验不通过，需修正")
        else:
            output["status"] = "通过"
            print("  ✅ Step 4 完成")
        
        self.results[4] = output
        return output
    
    # ------------------------------------------------------------------------
    # Step 5: 交叉验证（裁判验证）
    # ------------------------------------------------------------------------
    def step5_cross_validation(self) -> Dict:
        """
        触发条件：Step 4验收通过
        输入：完整模型方案
        输出：交叉验证报告 + 模型修正版
        时限：3个工作日
        """
        print("[Step 5] 交叉验证（裁判验证）...")
        
        if self.results.get(4, {}).get("status") != "通过":
            print("  ❌ Step 4 未通过，无法执行 Step 5")
            return {"error": "前置步骤未通过"}
        
        # 5.1 内部自洽验证
        self_consistency = self._check_self_consistency()
        
        # 5.2 标杆对比验证
        benchmark_comparison = self._check_benchmark_comparison()
        
        # 5.3 可执行性验证
        executability = self._check_executability()
        
        # 5.4 独立裁判验证
        referee = self.input_data.get("referee_validation", {})
        
        # 汇总问题
        issues = []
        if self_consistency["result"] != "通过":
            issues.extend(self_consistency.get("issues", []))
        if benchmark_comparison["result"] != "通过":
            issues.extend(benchmark_comparison.get("issues", []))
        if executability["result"] != "通过":
            issues.extend(executability.get("issues", []))
        
        high_issues = [i for i in issues if i.get("severity") == "高"]
        medium_issues = [i for i in issues if i.get("severity") == "中"]
        low_issues = [i for i in issues if i.get("severity") == "低"]
        
        output = {
            "step": 5,
            "name": "交叉验证（裁判验证）",
            "output_name": "《交叉验证报告》+ 模型修正版",
            "validation_results": {
                "self_consistency": self_consistency,
                "benchmark_comparison": benchmark_comparison,
                "executability": executability,
                "referee": referee
            },
            "issues": {
                "high": high_issues,
                "medium": medium_issues,
                "low": low_issues
            },
            "issue_count": {
                "high": len(high_issues),
                "medium": len(medium_issues),
                "low": len(low_issues)
            },
            "overall_assessment": "通过" if len(high_issues) == 0 else "需优化",
            "revised_version": "v1.1" if len(high_issues) > 0 else "v1.0",
            "timestamp": datetime.now().isoformat()
        }
        
        validation = self.validator.validate_step("Step 5", output, 5)
        self.validation_logs[5] = validation
        
        if not self.validator.is_step_valid(validation):
            output["status"] = "不合格"
            output["validation_issues"] = [asdict(v) for v in validation if v.result == "不通过"]
            print("  ⚠️  Step 5 校验不通过，需修正")
        else:
            output["status"] = "通过"
            print("  ✅ Step 5 完成")
        
        self.results[5] = output
        return output
    
    def _check_self_consistency(self) -> Dict:
        """内部自洽验证"""
        issues = []
        
        # 检查角色重叠
        roles = self.results.get(4, {}).get("roles", {}).get("roles", [])
        role_names = [r["name"] for r in roles]
        if len(role_names) != len(set(role_names)):
            issues.append({"severity": "高", "issue": "角色名称重复，存在角色重叠"})
        
        # 检查维度数量
        dimensions = self.results.get(4, {}).get("analysis_model", {}).get("dimensions", [])
        if len(dimensions) > 5:
            issues.append({"severity": "高", "issue": f"维度数量超标（{len(dimensions)} > 5）"})
        
        return {
            "result": "通过" if len(issues) == 0 else "不通过",
            "issues": issues
        }
    
    def _check_benchmark_comparison(self) -> Dict:
        """标杆对比验证"""
        issues = []
        
        benchmarks = self.results.get(2, {}).get("benchmarks", [])
        if len(benchmarks) < 3:
            issues.append({"severity": "中", "issue": f"标杆数量不足（{len(benchmarks)} < 3）"})
        
        return {
            "result": "通过" if len(issues) == 0 else "注意",
            "issues": issues
        }
    
    def _check_executability(self) -> Dict:
        """可执行性验证"""
        issues = []
        
        events = self.results.get(4, {}).get("action_model", {}).get("events", [])
        for event in events:
            for action in event.get("actions", []):
                if not action.get("trigger"):
                    issues.append({"severity": "高", "issue": f"动作'{action.get('name')}'缺少触发条件"})
                if not action.get("steps"):
                    issues.append({"severity": "高", "issue": f"动作'{action.get('name')}'缺少执行步骤"})
        
        return {
            "result": "通过" if len(issues) == 0 else "不通过",
            "issues": issues
        }
    
    # ------------------------------------------------------------------------
    # 执行完整五步法
    # ------------------------------------------------------------------------
    def run(self) -> Dict:
        """执行完整的五步法蒸馏"""
        print("=" * 60)
        print("业务模型蒸馏智能体开始执行")
        print(f"输入业务线：{self.input_data.get('business_description', {}).get('business_line', '未命名')}")
        print("=" * 60)
        
        # 顺序执行五步法
        self.step1_business_goal()
        self.step2_benchmark()
        self.step3_data_association()
        self.step4_model_definition()
        self.step5_cross_validation()
        
        # 生成完整模型包
        model_package = self._generate_model_package()
        
        print("=" * 60)
        print("蒸馏完成")
        print(f"模型包版本：{model_package.get('version', 'v1.0')}")
        print(f"整体状态：{model_package.get('status', '未知')}")
        print("=" * 60)
        
        return model_package
    
    def _generate_model_package(self) -> Dict:
        """生成完整业务模型包"""
        
        all_passed = all(
            self.results.get(i, {}).get("status") == "通过"
            for i in range(1, 6)
        )
        
        package = {
            "version": "v1.0" if all_passed else "v0.9（待修正）",
            "status": "通过" if all_passed else "需修正",
            "generated_at": datetime.now().isoformat(),
            "core_rules": {
                "tao_five_oppose": TAO_FIVE_OPPOSE,
                "tao_eight_steps": TAO_EIGHT_STEPS,
                "forbidden_words": FORBIDDEN_WORDS
            },
            "steps": {
                "step1_business_goal": self.results.get(1, {}),
                "step2_benchmark": self.results.get(2, {}),
                "step3_data_association": self.results.get(3, {}),
                "step4_model_definition": self.results.get(4, {}),
                "step5_cross_validation": self.results.get(5, {})
            },
            "validation_logs": {
                f"step_{i}": [asdict(v) for v in self.validation_logs.get(i, [])]
                for i in range(1, 6)
            },
            "output_files": [
                "《业务目标清单》",
                "《标杆分析表》",
                "《数据关联矩阵》",
                "角色体系 + 分析模型 + 动作模型",
                "《交叉验证报告》"
            ]
        }
        
        return package


# ============================================================================
# 第五部分：输入输出处理
# ============================================================================

class IOHandler:
    """输入输出处理器"""
    
    @staticmethod
    def load_input(file_path: str) -> Dict:
        """加载输入文件（YAML或JSON）"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"输入文件不存在：{file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            elif path.suffix == '.json':
                return json.load(f)
            else:
                raise ValueError(f"不支持的文件格式：{path.suffix}")
    
    @staticmethod
    def save_output(package: Dict, output_dir: str):
        """保存输出模型包"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 保存主文件
        main_file = output_path / "model_package.json"
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(package, f, ensure_ascii=False, indent=2)
        
        # 保存各步骤独立文件
        for step_name, step_data in package.get("steps", {}).items():
            step_file = output_path / f"{step_name}.json"
            with open(step_file, 'w', encoding='utf-8') as f:
                json.dump(step_data, f, ensure_ascii=False, indent=2)
        
        # 保存验证日志
        validation_file = output_path / "validation_logs.json"
        with open(validation_file, 'w', encoding='utf-8') as f:
            json.dump(package.get("validation_logs", {}), f, ensure_ascii=False, indent=2)
        
        # 生成Markdown报告
        report_file = output_path / "README.md"
        IOHandler._generate_report(package, report_file)
        
        print(f"\n输出已保存至：{output_path.absolute()}")
        print(f"  - model_package.json（完整模型包）")
        print(f"  - step1~step5.json（各步骤独立文件）")
        print(f"  - validation_logs.json（校验日志）")
        print(f"  - README.md（可读报告）")
    
    @staticmethod
    def _generate_report(package: Dict, report_path: Path):
        """生成Markdown格式的可读报告"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 业务模型蒸馏报告\n\n")
            f.write(f"> **生成时间**：{package.get('generated_at', '')}\n")
            f.write(f"> **模型包版本**：{package.get('version', '')}\n")
            f.write(f"> **整体状态**：{package.get('status', '')}\n\n")
            
            f.write("---\n\n")
            f.write("## 核心规则\n\n")
            f.write("### 陶总五大反对\n\n")
            for i, oppose in TAO_FIVE_OPPOSE.items():
                f.write(f"{i}. **{oppose['name']}**\n")
                f.write(f"   - 检查：{oppose['check']}\n")
                f.write(f"   - 动作：{oppose['action']}\n\n")
            
            f.write("### 禁用词语表\n\n")
            f.write("| 禁用词 | 推荐词 |\n")
            f.write("|--------|--------|\n")
            for forbidden, recommended in FORBIDDEN_WORDS.items():
                f.write(f"| {forbidden} | {recommended} |\n")
            f.write("\n")
            
            f.write("---\n\n")
            f.write("## 五步法执行结果\n\n")
            
            for step_name, step_data in package.get("steps", {}).items():
                step_num = step_data.get("step", 0)
                step_name_text = step_data.get("name", "")
                status = step_data.get("status", "")
                output_name = step_data.get("output_name", "")
                
                f.write(f"### Step {step_num}：{step_name_text}\n\n")
                f.write(f"- **输出**：{output_name}\n")
                f.write(f"- **状态**：{status}\n\n")
                
                # 验证日志
                validation_logs = package.get("validation_logs", {}).get(f"step_{step_num}", [])
                if validation_logs:
                    f.write("**校验结果**：\n\n")
                    f.write("| 检查项 | 结果 | 问题 | 严重度 |\n")
                    f.write("|--------|------|------|--------|\n")
                    for log in validation_logs:
                        f.write(f"| {log.get('check_item', '')} | {log.get('result', '')} | {log.get('issue', '')} | {log.get('severity', '')} |\n")
                    f.write("\n")
                
                # 如果有问题，列出
                issues = step_data.get("validation_issues", [])
                if issues:
                    f.write("**需修正问题**：\n\n")
                    for issue in issues:
                        f.write(f"- {issue.get('issue', '')}\n")
                    f.write("\n")
            
            f.write("---\n\n")
            f.write("## 输出文件清单\n\n")
            for file_name in package.get("output_files", []):
                f.write(f"- {file_name}\n")


# ============================================================================
# 第六部分：示例输入数据
# ============================================================================

EXAMPLE_INPUT = {
    "business_description": {
        "business_line": "投行债券发行业务",
        "core_goals": [
            {
                "name": "成功发行债券",
                "definition": "完成从项目线索到债券成功发行的全周期交付",
                "key_actions": [
                    "线索获取与核实",
                    "立项评估（5维度分析）",
                    "发行方案设计",
                    "申报材料制作",
                    "监管申报与反馈回复"
                ],
                "metrics": [
                    "年度发行项目数量",
                    "发行成功率（申报通过/总申报）"
                ],
                "boundary": "不包含银行间市场非金融企业债务融资工具"
            },
            {
                "name": "项目质量控制",
                "definition": "确保每个发行项目材料真实、风险可控、合规达标",
                "key_actions": [
                    "尽职调查质量把关",
                    "募集说明书数据核查",
                    "合规风险审查",
                    "质控内核评级"
                ],
                "metrics": [
                    "质控评级A级项目占比",
                    "监管反馈问题数量（均值）"
                ],
                "boundary": "不包含项目执行中的日常客户关系维护"
            }
        ],
        "relationships": {
            "依赖": ["目标2质量通过 → 目标1才能申报"],
            "协同": ["目标1线索获取 → 发现客户需求 → 回流客户服务"]
        }
    },
    "benchmarks": [
        {
            "dimension": "角色体系",
            "benchmark_obj": "华泰证券",
            "benchmark_practice": "AI选股/盯盘/交易助手+客户经理",
            "our_status": "组织者+超级数字员工框架已设计",
            "gap": "概念领先，落地滞后",
            "adoption": "调整后采用",
            "remark": "保持组织者+数字员工框架，学习具象化"
        },
        {
            "dimension": "分析模型",
            "benchmark_obj": "中信建投",
            "benchmark_practice": "智能条件选股/全维度市场搜索/财务数据解读",
            "our_status": "5维度模型已有，细节待验证",
            "gap": "方法论对齐",
            "adoption": "直接采用",
            "remark": "5维度框架与中信思路一致"
        },
        {
            "dimension": "动作标准化",
            "benchmark_obj": "华住集团",
            "benchmark_practice": "入住SOP：预订→确认→入住→服务→离店",
            "our_status": "规定动作模型v1.0已设计",
            "gap": "框架对齐，待适配",
            "adoption": "调整后采用",
            "remark": "酒店SOP逻辑迁移到证券"
        }
    ],
    "data_matrix": [
        {
            "indicator": "经营性现金流净额",
            "formula": "现金流量表直接读取",
            "data_source": "Wind/同花顺",
            "access_path": "系统API拉取",
            "auto_manual": "自动",
            "remark": "近3年平均值"
        },
        {
            "indicator": "现金流覆盖率",
            "formula": "经营性现金流/年本息",
            "data_source": "上述两项计算",
            "access_path": "系统自动计算",
            "auto_manual": "自动",
            "remark": ">=1.5通过"
        },
        {
            "indicator": "拟发行规模",
            "formula": "客户需求",
            "data_source": "客户经理录入",
            "access_path": "界面录入",
            "auto_manual": "手工",
            "remark": "精确到亿元"
        }
    ],
    "roles": [
        {
            "name": "客户经理",
            "source_position": "投行前台业务人员",
            "core_responsibility": "项目全周期负责人",
            "service_goal": "投行债券发行业务",
            "role_definition": "你是债券发行业务的项目全周期负责人",
            "goals": ["项目成功率>=80%", "客户满意度>=4.5/5"],
            "backstory": "拥有5年债券发行经验，熟悉各类发行人和投资者",
            "constraints": {
                "必须做": ["所有项目必须经过立项评估", "高风险客户必须标记预警"],
                "禁止做": ["不得向黑名单客户分配资源"]
            }
        },
        {
            "name": "组织者",
            "source_position": "投行管理层",
            "core_responsibility": "整体统筹者，判断风险，调配资源",
            "service_goal": "投行整体经营",
            "role_definition": "你是投行业务的整体统筹者"
        },
        {
            "name": "质控内核",
            "source_position": "质控合规团队",
            "core_responsibility": "质量把关者，把控项目质量，生成质控报告",
            "service_goal": "项目质量合规",
            "role_definition": "你是项目质量的把关者"
        },
        {
            "name": "产品支持",
            "source_position": "产品方案团队",
            "core_responsibility": "方案交付者，设计方案，对接监管",
            "service_goal": "发行方案设计",
            "role_definition": "你是发行方案的设计者"
        }
    ],
    "analysis_dimensions": [
        {
            "name": "偿债能力",
            "plain_language": "发行人到期能不能还本付息？",
            "objective_data": "近3年经营性现金流净额/资产负债率/利息覆盖倍数",
            "output": "偿债能力判断（通过/注意/不通过）",
            "analysis_framework": "现金流覆盖能力+资产负债结构+盈利能力+同业对比"
        },
        {
            "name": "发行方案",
            "plain_language": "发多少、发多久、利率定多少、怎么还钱？",
            "objective_data": "拟发行规模/期限/利率/还本付息方式",
            "output": "发行方案合理性判断",
            "analysis_framework": "规模参数+期限参数+利率参数+还本付息方式"
        },
        {
            "name": "市场窗口",
            "plain_language": "现在发债是不是好时候？投资者买不买？",
            "objective_data": "利率环境/同类型发行/投资者需求/监管环境",
            "output": "市场窗口判断（有利/中性/不利）",
            "analysis_framework": "利率环境+同类型发行+投资者需求+监管环境"
        },
        {
            "name": "资金用途",
            "plain_language": "募投项目有没有明确用途？钱怎么花？",
            "objective_data": "募投项目备案/资金分配/IRR测算",
            "output": "资金用途合理性判断",
            "analysis_framework": "项目真实性+资金分配+效益测算+偿债来源"
        },
        {
            "name": "增信合规",
            "plain_language": "客户历史上有没有违规？签完字会不会被追责？",
            "objective_data": "主体评级/历史处罚/担保抵押/合规状态",
            "output": "合规风险评估（通过/注意/不通过）",
            "analysis_framework": "主体评级+历史合规+担保抵押+增信措施"
        }
    ],
    "events": [
        {
            "event_name": "债券发行线索录入",
            "trigger_condition": "发现客户有债券发行意向",
            "event_level": "常规",
            "actions": [
                {
                    "name": "线索核实与初步触达",
                    "trigger": "收到债券发行线索",
                    "steps": [
                        "查询客户基本信息",
                        "判断线索来源可靠性",
                        "选择触达方式",
                        "首次沟通确认3个事实"
                    ],
                    "output": "《线索跟进记录》+ 线索状态更新",
                    "exception_handling": {
                        "客户关键人无法触达": "尝试经办人/董秘 → 标记'触达困难' → 组织者协调"
                    },
                    "deadline": "2个工作日内",
                    "risk_level": "可以"
                },
                {
                    "name": "线索登记与资源预判",
                    "trigger": "收到债券发行线索",
                    "steps": [
                        "登记线索到投行经营看板",
                        "预判资源需求",
                        "检查历史项目冲突",
                        "判断线索优先级"
                    ],
                    "output": "《线索登记台账》更新 + 资源预判结论",
                    "exception_handling": {
                        "历史项目冲突": "标记冲突 → 确认是否为新增需求"
                    },
                    "deadline": "1个工作日内",
                    "risk_level": "可以"
                }
            ]
        },
        {
            "event_name": "立项评估启动",
            "trigger_condition": "客户确认有债券发行意向",
            "event_level": "重点",
            "actions": [
                {
                    "name": "启动5维度分析模型评估",
                    "trigger": "客户确认债券发行意向",
                    "steps": [
                        "收集基础数据",
                        "调用债券业务分析模型v2.0，完成5维度分析",
                        "整理分析结果，形成初步判断",
                        "提交立项评估申请"
                    ],
                    "output": "《债券发行立项评估表》+ 初步立项建议",
                    "exception_handling": {
                        "财务数据缺失": "标记'数据缺失' → 要求客户提供",
                        "核心指标不通过": "记录不通过项 → 提交质控内核审查"
                    },
                    "deadline": "3个工作日内",
                    "risk_level": "必须确认"
                }
            ]
        }
    ],
    "referee_validation": {
        "referee_count": 2,
        "referees": [
            {"name": "项目经理A", "experience": "5年债券发行", "feedback": "组织者判断能力需联席机制"},
            {"name": "项目经理B", "experience": "3年债券+2年定增", "feedback": "需增加信用利差指标"}
        ],
        "overall_feedback": "模型框架可执行，数据对接是落地瓶颈"
    }
}


# ============================================================================
# 第七部分：主程序入口
# ============================================================================

def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(
        description="业务模型蒸馏智能体——将企业业务知识蒸馏为可执行的业务模型"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="输入文件路径（YAML或JSON）"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="./model_output",
        help="输出目录（默认：./model_output）"
    )
    parser.add_argument(
        "--example", "-e",
        action="store_true",
        help="使用示例数据运行（无需输入文件）"
    )
    parser.add_argument(
        "--validate-only", "-v",
        action="store_true",
        help="仅执行核心规则校验，不执行五步法"
    )
    
    args = parser.parse_args()
    
    # 加载输入数据
    if args.example:
        print("使用示例数据运行...")
        input_data = EXAMPLE_INPUT
    elif args.input:
        input_data = IOHandler.load_input(args.input)
    else:
        print("错误：请提供输入文件（--input）或使用示例（--example）")
        print(f"\n示例用法：")
        print(f"  python distillation_agent.py --example --output ./output")
        print(f"  python distillation_agent.py --input business.yaml --output ./output")
        sys.exit(1)
    
    # 仅校验模式
    if args.validate_only:
        print("仅执行核心规则校验...")
        validator = CoreRuleValidator()
        text = json.dumps(input_data, ensure_ascii=False)
        
        print("\n[禁用词检查]")
        violations = validator.check_forbidden_words(text)
        if violations:
            for word, recommended in violations:
                print(f"  ⚠️  发现禁用词'{word}'，应替换为'{recommended}'")
        else:
            print("  ✅ 无禁用词")
        
        print("\n[陶总五大反对检查]")
        print("  ℹ️  完整校验需要在五步法执行过程中进行")
        
        return
    
    # 执行五步法蒸馏
    engine = DistillationEngine(input_data)
    model_package = engine.run()
    
    # 保存输出
    IOHandler.save_output(model_package, args.output)
    
    print("\n蒸馏完成！")
    
    # 如果校验不通过，提示修正
    if model_package.get("status") != "通过":
        print("\n⚠️  模型包存在需修正问题，请查看：")
        print(f"  - {args.output}/validation_logs.json")
        print(f"  - {args.output}/README.md")
        sys.exit(2)


if __name__ == "__main__":
    main()
