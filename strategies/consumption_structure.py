# 消费结构诊断策略 — 学生适配版恩格尔系数
# 将餐饮支出细分为基础饮食（食堂/食材/超市）和社交饮食（外卖/聚餐）
# 加上娱乐、学习共四个维度，逐一与健康区间比较
from models.transaction import Transaction
from models.budget import Budget
from models.diagnosis_report import DiagnosisReport, DimensionDetail, HealthLevel
from models.suggestion import Suggestion
from .diagnostic_strategy import DiagnosticStrategy


class ConsumptionStructureStrategy(DiagnosticStrategy):
    """消费结构分析：基础饮食/社交饮食/娱乐/学习 四维度占比诊断。

    健康区间（学生适配）：
    - 基础饮食（食堂+食材+超市）≤ 25%
    - 社交饮食（外卖+聚餐+其他餐饮）≤ 15%
    - 娱乐 ≤ 15%
    - 学习 ≥ 5%

    当备注数据不足以区分两类饮食时，自动回退为简化模式（总餐饮≤30%）。
    """

    # 可配置阈值（答辩时可调参演示）
    BASIC_FOOD_MAX = 0.25
    SOCIAL_FOOD_MAX = 0.15
    ENTERTAINMENT_MAX = 0.15
    STUDY_MIN = 0.05
    SIMPLE_FOOD_MAX = 0.30       # 简化模式：总餐饮占比上限
    CLASSIFY_THRESHOLD = 0.10    # 简化模式触发阈值：基础饮食识别率不到 10%

    def diagnose(self, transactions: list[Transaction],
                 budgets: list[Budget]) -> DiagnosisReport:
        # 只分析支出
        expenses = [t for t in transactions if t.is_expense()]
        total_expense = sum(t.amount for t in expenses)

        # 边界：无支出
        if total_expense == 0:
            dim = DimensionDetail("消费结构诊断", 100, HealthLevel.HEALTHY, None)
            return DiagnosisReport(HealthLevel.HEALTHY, 100, [dim], [])

        # 步骤1：按备注关键词分类汇总
        basic_food = 0.0  # 基础饮食：食堂/食材/超市
        social_food = 0.0  # 社交饮食：外卖/聚餐/其他餐饮
        entertainment = 0.0
        study = 0.0

        for t in expenses:
            note = t.note if t.note else ""
            if t.category in ("餐饮", "餐饮食品"):
                if "食堂" in note or "食材" in note or "超市" in note:
                    basic_food += t.amount
                elif "外卖" in note or "聚餐" in note:
                    social_food += t.amount
                else:
                    if t.category == "餐饮食品":
                        basic_food += t.amount  # 包装食品/饮料/零食 → 基础饮食
                    else:
                        social_food += t.amount  # 无法区分 → 社交饮食（外食为主）
            elif t.category in ("娱乐", "娱乐玩具"):
                entertainment += t.amount
            elif t.category == "学习":
                study += t.amount

        total_food = basic_food + social_food

        # 步骤2：判断是否用简化模式
        if total_food > 0 and (basic_food / total_food) < self.CLASSIFY_THRESHOLD:
            return self._diagnose_simple(total_expense, total_food)
        else:
            return self._diagnose_full(total_expense, basic_food, social_food,
                                       entertainment, study)

    # ================================================================
    # 简化模式：只检查总餐饮占比
    # ================================================================

    def _diagnose_simple(self, total_expense, total_food):
        food_ratio = total_food / total_expense

        if food_ratio <= self.SIMPLE_FOOD_MAX:
            s = Suggestion(3, 0, "餐饮",
                           f"餐饮总支出 ¥{total_food:.0f}，占比 {food_ratio:.0%}，在健康范围内。")
            dim = DimensionDetail("消费结构诊断", 100, HealthLevel.HEALTHY, s)
            return DiagnosisReport(HealthLevel.HEALTHY, 100, [dim], [s])

        # 超出健康上限
        excess = total_food - total_expense * self.SIMPLE_FOOD_MAX
        deviation = food_ratio - self.SIMPLE_FOOD_MAX
        score = max(0, 100 - deviation * 200)

        level = HealthLevel.CRITICAL if deviation > 0.15 else HealthLevel.WARNING

        s = Suggestion(1, excess, "餐饮",
                       f"餐饮总支出 ¥{total_food:.0f}，占总支出 {food_ratio:.0%}"
                       f"（建议 <{self.SIMPLE_FOOD_MAX:.0%}）。超出 ¥{excess:.0f}/月。"
                       f"建议适当减少外食频次。")
        dim = DimensionDetail("消费结构诊断", score, level, s)
        return DiagnosisReport(level, score, [dim], [s])

    # ================================================================
    # 完整模式：四维度独立分析
    # ================================================================

    def _diagnose_full(self, total_expense, basic_food, social_food,
                       entertainment, study):
        basic_ratio = basic_food / total_expense
        social_ratio = social_food / total_expense
        ent_ratio = entertainment / total_expense
        study_ratio = study / total_expense

        # 各维度评分
        basic_score = self._score_upper(basic_ratio, self.BASIC_FOOD_MAX)
        social_score = self._score_upper(social_ratio, self.SOCIAL_FOOD_MAX)
        ent_score = self._score_upper(ent_ratio, self.ENTERTAINMENT_MAX)
        study_score = self._score_lower(study_ratio, self.STUDY_MIN)

        # 综合分 = 四维度平均
        overall_score = (basic_score + social_score + ent_score + study_score) / 4

        # 综合等级
        if overall_score >= 80:
            overall_level = HealthLevel.HEALTHY
        elif overall_score >= 50:
            overall_level = HealthLevel.WARNING
        else:
            overall_level = HealthLevel.CRITICAL

        dimensions = []
        suggestions = []

        # 基础饮食维度
        dim, s = self._eval_upper_dim(
            "基础饮食占比", "基础饮食", basic_food, basic_ratio,
            self.BASIC_FOOD_MAX, total_expense, 2,
            "食堂/食材/超市 ¥{amount:.0f}，占比 {ratio:.0%}（建议 <{bound:.0%}）。超出 ¥{excess:.0f}/月。"
        )
        dimensions.append(dim)
        if s: suggestions.append(s)

        # 社交饮食维度
        dim, s = self._eval_upper_dim(
            "社交饮食占比", "社交饮食", social_food, social_ratio,
            self.SOCIAL_FOOD_MAX, total_expense, 1,
            "外卖+聚餐 ¥{amount:.0f}，占比 {ratio:.0%}（建议 <{bound:.0%}）。超出 ¥{excess:.0f}/月。建议减少外卖或聚餐次数。"
        )
        dimensions.append(dim)
        if s: suggestions.append(s)

        # 娱乐维度
        dim, s = self._eval_upper_dim(
            "娱乐占比", "娱乐", entertainment, ent_ratio,
            self.ENTERTAINMENT_MAX, total_expense, 2,
            "娱乐 ¥{amount:.0f}，占比 {ratio:.0%}（建议 <{bound:.0%}）。超出 ¥{excess:.0f}/月。"
        )
        dimensions.append(dim)
        if s: suggestions.append(s)

        # 学习维度（下限型）
        dim, s = self._eval_lower_dim(
            "学习占比", "学习", study, study_ratio,
            self.STUDY_MIN, total_expense, 2,
            "学习支出 ¥{amount:.0f}，占比 {ratio:.0%}（建议 >{bound:.0%}）。建议增加学习投资 ¥{shortage:.0f}/月。"
        )
        dimensions.append(dim)
        if s: suggestions.append(s)

        return DiagnosisReport(overall_level=overall_level, overall_score=overall_score,
                               dimensions=dimensions, suggestions=suggestions)

    # ================================================================
    # 评分工具函数
    # ================================================================

    def _score_upper(self, actual, max_val):
        """上限型评分：实际值超过上限则扣分。每超过 1% 扣 2 分。"""
        if actual <= max_val:
            return 100.0
        return max(0, 100 - (actual - max_val) * 200)

    def _score_lower(self, actual, min_val):
        """下限型评分：实际值低于下限则扣分。"""
        if actual >= min_val:
            return 100.0
        if min_val == 0:
            return 100.0
        return max(0, actual / min_val * 100)

    def _eval_upper_dim(self, dim_name, cat_label, amount, ratio, bound,
                        total_expense, priority, template):
        """评价一个上限型维度，返回 (DimensionDetail, Suggestion或None)"""
        score = self._score_upper(ratio, bound)
        if ratio <= bound:
            return DimensionDetail(dim_name, score, HealthLevel.HEALTHY, None), None

        excess = amount - total_expense * bound
        level = HealthLevel.CRITICAL if ratio > bound + 0.10 else HealthLevel.WARNING

        desc = template.format(amount=amount, ratio=ratio, bound=bound, excess=excess)
        s = Suggestion(priority, excess, cat_label, desc)
        return DimensionDetail(dim_name, score, level, s), s

    def _eval_lower_dim(self, dim_name, cat_label, amount, ratio, bound,
                        total_expense, priority, template):
        """评价一个下限型维度，返回 (DimensionDetail, Suggestion或None)"""
        score = self._score_lower(ratio, bound)
        if ratio >= bound:
            return DimensionDetail(dim_name, score, HealthLevel.HEALTHY, None), None

        shortage = total_expense * bound - amount
        level = HealthLevel.CRITICAL if ratio < 0.01 else HealthLevel.WARNING

        desc = template.format(amount=amount, ratio=ratio, bound=bound, shortage=shortage)
        s = Suggestion(priority, shortage, cat_label, desc)
        return DimensionDetail(dim_name, score, level, s), s
