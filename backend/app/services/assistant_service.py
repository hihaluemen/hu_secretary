import json
import re
from datetime import datetime
from typing import Any

from app.repositories.event_repository import EventRepository
from app.services.llm_service import LLMService
from app.utils.text import clean_text


class AssistantService:
    def __init__(self, llm_service: LLMService | None = None, event_repository: EventRepository | None = None) -> None:
        self.llm_service = llm_service or LLMService()
        self.event_repository = event_repository or EventRepository()

    def normalize_time_text(self, user_input: str) -> str:
        weekday_map = ("一", "二", "三", "四", "五", "六", "日")
        now = datetime.now()
        system_prompt = f"""
【角色】：日期、时间处理专家
【前置信息】：今天是 {now:%Y-%m-%d}，星期{weekday_map[now.weekday()]}。
【处理规则】：请你对我提供的对话内容进行时间规范化处理，处理规则如下：
1、保留原对话中的所有信息，不要做任何的筛检；
2、口语化时间表述统一转换为 “YYYY-MM-DD HH:MM” 格式（若未指定年份，默认填充当前年份；若未指定日期，默认今天当天；'下周'指从当前周次+1的周一开始至周日；'上午'为08:00-11:59，'下午'为12:00-17:59，'傍晚'为18:00-20:00，'晚上'为20:00-23:59；若仅指定时段未指定具体时刻，默认：上午10:00、下午16:00、晚上20:00；若既无时段也无时刻，默认09:00；无法转换的模糊时间保留原文）
【输出结果】：仅保留规范化后的内容，不添加任何额外说明。
"""
        normalized = self.llm_service.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.0,
        )
        return self._replace_midnight_defaults(normalized, user_input)

    def _infer_default_hhmm(self, source_text: str) -> str:
        mapping = [
            ("上午", "10:00"),
            ("早上", "09:00"),
            ("中午", "12:00"),
            ("下午", "16:00"),
            ("傍晚", "18:00"),
            ("晚上", "20:00"),
            ("今晚", "20:00"),
            ("夜里", "21:00"),
            ("夜间", "21:00"),
        ]
        for keyword, hhmm in mapping:
            if keyword in source_text:
                return hhmm
        return "09:00"

    def _split_clauses(self, text: str) -> list[str]:
        if not text:
            return []
        return [segment.strip() for segment in re.split(r"[；;。.!?？]", text) if segment.strip()]

    def _replace_midnight_defaults(self, normalized_text: str, original_text: str) -> str:
        if not normalized_text or "00:00" not in normalized_text:
            return normalized_text

        midnight_pattern = r"(\d{4}-\d{2}-\d{2})([ T])00:00(?::00)?"

        normalized_clauses = self._split_clauses(normalized_text)
        original_clauses = self._split_clauses(original_text)
        if not normalized_clauses:
            fallback_hhmm = self._infer_default_hhmm(original_text)
            return re.sub(midnight_pattern, rf"\g<1>\g<2>{fallback_hhmm}", normalized_text)

        rebuilt_clauses: list[str] = []
        for index, clause in enumerate(normalized_clauses):
            if "00:00" not in clause:
                rebuilt_clauses.append(clause)
                continue

            source_clause = original_clauses[index] if index < len(original_clauses) else original_text
            default_hhmm = self._infer_default_hhmm(source_clause)
            replaced_clause = re.sub(midnight_pattern, rf"\g<1>\g<2>{default_hhmm}", clause)
            rebuilt_clauses.append(replaced_clause)

        if len(rebuilt_clauses) == 1:
            return rebuilt_clauses[0]
        return "；".join(rebuilt_clauses)

    def split_intentions(self, user_input: str) -> tuple[str, str, str]:
        prompt = """
你是个人待办事项管理助手。识别输入中的待办请求并返回 JSON 数组。
每项格式：{"content":"原始内容","flag":0/1/2,"type":"查询/更新/新增"}
flag 映射：查询=0、更新=1、新增=2。
仅返回 JSON，不要其他解释。
"""
        content = self.llm_service.chat(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.1,
        )
        try:
            events = self._parse_json_payload(content)
        except Exception:
            return self._fallback_intentions(user_input)

        if isinstance(events, dict):
            events = [events]
        if not isinstance(events, list):
            return self._fallback_intentions(user_input)

        add_items: list[str] = []
        update_items: list[str] = []
        select_items: list[str] = []

        for item in events:
            if not isinstance(item, dict):
                continue
            flag = item.get("flag")
            content_item = item.get("content", "")
            if flag == 0:
                select_items.append(content_item)
            elif flag == 1:
                update_items.append(content_item)
            elif flag == 2:
                add_items.append(content_item)

        add_merged = ";".join(add_items)
        update_merged = ";".join(update_items)
        select_merged = ";".join(select_items)
        if not add_merged and not update_merged and not select_merged:
            return self._fallback_intentions(user_input)

        return add_merged, update_merged, select_merged

    def _parse_json_payload(self, content: str) -> Any:
        text = (content or "").strip()
        if not text:
            raise ValueError("empty payload")

        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if fence_match:
            text = fence_match.group(1).strip()

        try:
            return json.loads(text)
        except Exception:
            pass

        array_match = re.search(r"\[[\s\S]*\]", text)
        if array_match:
            return json.loads(array_match.group(0))

        object_match = re.search(r"\{[\s\S]*\}", text)
        if object_match:
            return json.loads(object_match.group(0))

        raise ValueError("json payload not found")

    def _fallback_intentions(self, user_input: str) -> tuple[str, str, str]:
        text = clean_text(user_input)
        query_keywords = ("查", "查询", "看", "找", "检索")
        update_keywords = ("改", "修改", "更新", "调整", "变更")
        if any(keyword in text for keyword in query_keywords):
            return "", "", text
        if any(keyword in text for keyword in update_keywords):
            return "", text, ""
        return text, "", ""

    def extract_events(self, user_input: str) -> list[dict[str, Any]]:
        prompt = """
你是事件信息提取助手。请提取事件并返回 JSON 数组。
字段严格使用：事件内容、开始时间、地点、人物、remark。
开始时间格式必须为 YYYY-MM-DD HH:MM:SS。
仅返回 JSON 数组。
"""
        content = self.llm_service.chat(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.0,
        )
        try:
            data = self._parse_json_payload(content)
        except Exception:
            return []
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            return []

        normalized_events: list[dict[str, Any]] = []
        for item in data:
            if isinstance(item, dict):
                normalized_events.append(item)
        return normalized_events

    def select_events(self, user_id: str, user_input: str) -> list[dict[str, Any]]:
        all_events = self.event_repository.list_events(user_id)
        prompt = """
你是事项匹配助手。根据用户查询从候选事项中筛选符合条件项。
仅返回 JSON 数组（匹配项），没有结果返回 []。
"""
        content = self.llm_service.chat(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"查询事项列表：{all_events}"},
                {"role": "user", "content": f"用户查询：{user_input}"},
            ],
            temperature=0.1,
        )
        try:
            data = self._parse_json_payload(content)
        except Exception:
            return []
        if isinstance(data, dict):
            return [data]
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        return []

    def build_update_sql(self, user_id: str, user_input: str) -> str:
        all_events = self.event_repository.list_events(user_id)
        prompt = f"""
你需要根据用户输入生成可执行 MySQL UPDATE 语句。
表名 events，字段包含 event/event_time/location/participants/remark/update_time。
优先结合数据库事项数据定位目标：{all_events}
仅输出 SQL，不输出其他说明。
"""
        return self.llm_service.chat(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.1,
        )

    def process(self, user_id: str, text: str, dry_run: bool = False) -> dict[str, Any]:
        normalized = self.normalize_time_text(clean_text(text))
        add_content, update_content, select_content = self.split_intentions(normalized)

        add_result: dict[str, Any] | None = None
        add_events: list[dict[str, Any]] = []
        if add_content:
            add_events = self.extract_events(add_content)
            if not dry_run:
                add_result = self.event_repository.insert_events(user_id, add_events)
            else:
                add_result = {
                    "status": "success",
                    "msg": "dry_run 模式未写入数据库",
                    "detail": [],
                    "success_count": 0,
                    "fail_count": 0,
                }

        select_result: list[dict[str, Any]] = []
        if select_content:
            select_result = self.select_events(user_id, select_content)

        update_sql = ""
        if update_content:
            update_sql = self.build_update_sql(user_id, update_content)

        return {
            "user_id": user_id,
            "input": text,
            "normalized_input": normalized,
            "intent": {
                "add_content": add_content,
                "update_content": update_content,
                "select_content": select_content,
            },
            "add": {
                "events": add_events,
                "result": add_result,
            },
            "select": select_result,
            "update_sql": update_sql,
            "dry_run": dry_run,
        }
