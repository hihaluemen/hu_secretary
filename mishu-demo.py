#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 11 17:21:25 2025

@author: alibaba
"""

import sys
import os
import json
import re
import pymysql
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from openai import OpenAI
from dotenv import load_dotenv
from pymysql.err import OperationalError, IntegrityError

# ---------------------- 1. 全局配置与工具函数 ----------------------
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(obj)

def json_dumps(data, ensure_ascii=False, indent=2):
    return json.dumps(data, ensure_ascii=ensure_ascii, indent=indent, cls=DateTimeEncoder)

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    text = text.replace("：", ":").replace("，", ",").replace("。", ".").replace("？", "?")
    return text

# ---------------------- 2. 环境初始化 ----------------------
load_dotenv()
client = OpenAI(
    api_key=os.getenv("KIMI_API_KEY", os.getenv("OPENAI_API_KEY")),
    base_url=os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1"),
)
TIME_ZONE = ZoneInfo("Asia/Shanghai")
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "123456"),
    "database": os.getenv("MYSQL_DB", "daily_assistant"),
    "charset": "utf8mb4",
    "autocommit": False
}

# ---------------------- 3. 核心：标准化日期处理（关键调整） ----------------------
def normalize_time_list(user_input):
    """
    1. 先补全缺失日期
    2. 再批量调模型标准化
    3. 原地写回 std_key
    """
    
    SYSTEM_PROMPT = f"""
   【角色】：日期、时间处理专家
    【前置信息】：今天是 {datetime.now():%Y-%m-%d}，星期{("一","二","三","四","五","六","日")[datetime.now().weekday()]}。
    【处理规则】：请你对我提供的对话内容进行时间规范化处理，处理规则如下：
        1、保留原对话中的所有信息，不要做任何的筛检；
2、口语化时间表述统一转换为 “YYYY-MM-DD HH:MM” 格式（若未指定年份，默认填充当前年份；若未指定日期，默认今天当天；'下周'指从当前周次+1的周一开始至周日；'上午'为08:00-11:59，'下午'为12:00-17:59，'傍晚'为18:00-20:00，'晚上'为21:00-23:59；无法转换的模糊时间（如'最近'）保留原文
【输入要求】：输入为纯文本格式的对话内容，不包含图片、表格、特殊符号（标点符号除外）等非文本元素；【输出结果】：仅保留规范化后的内容，不添加任何额外说明、注释或格式
    【输入示例】：明天上午 9 点去金融办开网络安全大会，下午 2 点去政务办参加安全大会；下周二去上海出差调研阿里、百度大模型落地场景，计划 10 点和他们交流。
    【输出示例」（当前日期为 2025-12-11 星期四）：2025-12-12 09:00 去金融办开网络安全大会，2025-12-12 14:00 去政务办参加安全大会；2025-12-16 10:00 去上海出差调研阿里、百度大模型落地场景，计划和他们交流。
    """
    
    # 调用模型标准化时间
    rsp = client.chat.completions.create(
        model="kimi-k2-turbo-preview",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_input}
        ],
        temperature=0
    )
    res = rsp.choices[0].message.content.strip()    
    return res

# ---------------------- 4. 数据库初始化（无变更） ----------------------
def init_mysql_db():
    conn = None
    cursor = None
    try:
        conn = pymysql.connect(
            host=MYSQL_CONFIG["host"],
            port=MYSQL_CONFIG["port"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"],
            charset=MYSQL_CONFIG["charset"]
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']} DEFAULT CHARACTER SET utf8mb4")
        conn.select_db(MYSQL_CONFIG["database"])
        
        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS events (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '事件ID',
            user_id VARCHAR(50) NOT NULL COMMENT '用户ID',
            event VARCHAR(255) NOT NULL COMMENT '事件核心内容',
            event_time DATETIME NOT NULL COMMENT '开始时间（标准格式：YYYY-MM-DD HH:MM:SS）',
            location VARCHAR(255) NOT NULL COMMENT '事件地点',
            participants VARCHAR(500) NOT NULL COMMENT '参与人员（原始表述）',
            remark VARCHAR(500) NULL COMMENT '事件提醒信息',
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX idx_user_time (user_id, event_time),
            INDEX idx_event (event(191)),
            INDEX idx_location (location(191))
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='日常事件表（仅保留开始时间）';
        '''
        cursor.execute(create_table_sql)
        conn.commit()
        print("✅ MySQL数据库初始化成功！")
    except OperationalError as e:
        print(f"❌ MySQL连接失败：{e}")
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ 数据库初始化失败：{e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

init_mysql_db()

# ---------------------- 5. 数据库操作（适配前置时间标准化） ----------------------
def get_mysql_conn():
    retry_count = 3
    while retry_count > 0:
        try:
            conn = pymysql.connect(**MYSQL_CONFIG)
            return conn
        except OperationalError as e:
            retry_count -= 1
            print(f"⚠️ MySQL连接失败，剩余重试次数：{retry_count}，错误：{e}")
            if retry_count == 0:
                raise
    return None

def write_events_to_db(user_id: str, events_list: list) -> dict:
    """写入数据库：从映射字典中直接获取标准时间，无需二次解析"""
    if not events_list:
        return {"status": "failed", "msg": "无有效事件可写入"}
    
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor()
        success_count = 0
        fail_count = 0
        fail_msgs = []
        
        for event in events_list:
            event_content = clean_text(event.get("事件内容", "未知活动"))
            time_raw = clean_text(event.get("开始时间", ""))
            
            # 补充：将时间格式补全为YYYY-MM-DD HH:MM:SS（兼容模型返回的HH:MM格式）
            if len(time_raw.strip()) == 16:  # 2025-12-12 09:00 → 补全为2025-12-12 09:00:00
                time_raw = f"{time_raw}:00"
            
            location = clean_text(event.get("地点", "地点未确定"))
            participants = clean_text(event.get("人物", "")) or "未知人员"
            remark = clean_text(event.get("remark", "")) or ""
            
            # 重复检测
            duplicate_sql = '''
            SELECT id FROM events 
            WHERE user_id = %s AND event = %s AND event_time = %s LIMIT 1
            '''
            cursor.execute(duplicate_sql, (user_id, event_content, time_raw))
            if cursor.fetchone():
                fail_count += 1
                fail_msgs.append(f"事件[{event_content}]：重复事件（{time_raw}）")  # 修复括号缺失
                continue
            
            # 核心修复：占位符数量从7个改为6个（匹配参数数量）
            insert_sql = '''
            INSERT INTO events (
                user_id, event, event_time, 
                location, participants, remark
            ) VALUES (%s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_sql, (
                user_id, event_content, time_raw,
                location, participants, remark
            ))
            success_count += 1
            fail_msgs.append(f"事件[{event_content}]：写入成功（{time_raw}）")  # 修复括号缺失
        
        conn.commit()
        return {
            "status": "success" if success_count > 0 else "failed",
            "msg": f"✅ 成功写入{success_count}条，❌ 失败{fail_count}条",
            "detail": fail_msgs,
            "success_count": success_count,
            "fail_count": fail_count
        }
    except Exception as e:
        if conn:
            conn.rollback()
        return {"status": "failed", "msg": f"批量写入失败：{str(e)}"}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ---------------------- 6. 核心Agent（调整为：前置时间标准化 → 大模型提取） ----------------------
def event_agent(user_id: str, user_input: str) -> dict:
    """
    调整后核心流程：
    1. 前置处理：将用户输入中的所有时间转换为「原始时间（标准时间）」格式
    2. 传给大模型：提取事件（此时大模型能直接看到标准时间）
    3. 写入数据库：从映射字典中直接获取标准时间，无需二次解析
    """
    # 步骤1：前置时间标准化（核心调整）
    add_res = user_input

    # 步骤2：构造Prompt（大模型可直接看到标准时间）
    prompt = """你是专注于事件信息提取的高效助手，核心职责是精准识别用户输入中的事件并结构化输出关键信息。

# 核心规则
## 必须执行
1. 逐句解析用户输入，识别所有独立事件（以时间、地点、主题差异为判断依据），确保无遗漏。
2. 每个事件需完整提取：事件内容、开始时间、地点、人物、remark提醒信息5项字段（无结束时间）。
3. 输出格式严格遵循json_list结构，每个事件为独立json对象。

## 约束条件
1. 禁止主观添加用户未提及的信息，如无相关字段内容则留空字符串。
2. 开始时间必须提取输入中的「标准时间部分」，格式严格为YYYY-MM-DD HH:MM:SS，禁止使用原始自然语言。
3. 人物仅提取明确提及的姓名及身份（如"张三（技术总监）"），禁止简化。

# 输入处理
- 读取优先级：按用户输入的时间顺序解析事件。
- 异常处理：若输入无明确事件边界，按语义停顿拆分（如分号、句号分隔）。

# 执行步骤
1. 事件拆分：扫描用户输入，按时间节点、地点变化或主题切换拆分独立事件，标记事件数量。
2. 字段提取：对每个事件，依次提取：
   - 事件内容：概括事件核心主题（如"出发去机场接老板"）
   - 开始时间：仅提取标准时间（YYYY-MM-DD HH:MM:SS），如"2025-12-13 08:30:00"
   - 地点：提取明确地点（如"机场"）
   - 人物：提取参与人员（如"老板"）
   - remark：提取括号内或"重要！"等提醒信息，无则留空
3. 格式校验：检查每个事件的5项字段是否完整，重点校验开始时间是否为标准格式。

# 输出规范
1. 结构框架：以json_list格式输出，示例：
   [{{"事件内容":"出发去机场接老板","开始时间":"2025-12-13 08:30:00","地点":"机场","人物":"老板","remark":""}},{{"事件内容":"参加全省AI安全大会","开始时间":"2025-12-12 09:30:00","地点":"政务办","人物":"","remark":"带笔记本"}}]
2. 语言风格：严格按输入提取，禁止改写、概括或截断任何信息。
3. 字数限制：每个事件的字段内容长度不超过100字。

# 强制要求
1. 仅返回JSON数组，无任何额外文字、注释、解释。
2. 数组长度必须等于用户输入中的独立事件数量，禁止合并事件。
3. 字段名严格使用：事件内容、开始时间、地点、人物、remark。
4. 开始时间必须为YYYY-MM-DD HH:MM:SS格式，否则视为任务失败。
5. 用户输入如下: """

    # 步骤3：调用大模型提取事件
    try:
        response = client.chat.completions.create(
            model=os.getenv("KIMI_MODEL", "kimi-k2-turbo-preview"),
            messages=[{"role": "system", "content": prompt},
                       {"role": "user", "content": add_res}],
            temperature=0.0,
            seed=12345
        )
        events_list = json.loads(response.choices[0].message.content.strip())
        if not isinstance(events_list, list):
            events_list = [events_list]
    except json.JSONDecodeError:
        return {"status": "failed", "msg": "大模型输出非JSON数组格式", "data": []}
    except Exception as e:
        return {"status": "failed", "msg": f"大模型调用失败：{str(e)}", "data": []}
    
    # 步骤4：写入数据库（用前置生成的时间映射）
    write_result = write_events_to_db(user_id, events_list)
    
    return {
        "status": write_result["status"],
        "msg": write_result["msg"],
        "detail": write_result.get("detail", []),
        "data": events_list,
        "standardized_input": user_input
    }


# ---------------------- 7. 用户意图拆分 ----------------------

def  intention_extra(user_input):
    prompt = """
   # 你是【个人待办事项管理助手】，核心职责是识别用户内容是否为待办事项的查询、更新或新增请求，对有效请求进行结构化处理并输出结果，对无效请求礼貌引导。

### 必做事项
1. **请求类型判断**：收到用户内容后，必须先判断是否为待办事项的查询、更新或新增请求；若为其他内容，必须输出礼貌引导语。
2. **原始内容保留**：对有效待办请求进行处理时，必须完全保留用户原始输入内容，不得修改或删减。
3. **flag标记准确**：根据请求类型为有效待办事项分配正确的flag值：查询→0、更新→1、新增→2。

### 约束条件
1. **非待办内容处理**：若用户内容是闲聊、咨询无关问题等非待办事项，禁止输出结构化结果，仅回复引导语：“抱歉，我目前仅能协助处理待办事项的查询、更新和新增哦~”
2. **模糊请求处理**：若用户内容属于待办事项但类型模糊（如未明确是查询/更新/新增），需回复：“麻烦您明确一下是查询、更新还是新增待办事项呢？”
3. **多类型请求处理**：若用户内容同时包含多种待办类型（如“查询昨天的待办并新增今天的任务”），必须拆分不同类型的请求分别处理，每个请求单独标记flag。

### 输入读取规则
- 读取优先级：直接读取完整用户内容，无需拆分或筛选。
- 异常处理：若用户内容为空或仅含特殊符号，视为无效请求，执行非待办内容处理规则。

### 操作流程
1. **请求类型识别**：
   - 查询类：含“查”“看”“找”等关键词，或包含询问待办事项具体信息（如时间、地点、内容等）的表达（如“查一下我的待办”“年度总结什么时候开”）
   - 更新类：含“改”“更新”“编辑”等关键词（如“更新待办事项的时间”）
   - 新增类：含“加”“新增”“创建”等关键词（如“新增明天的会议待办”）
2. **有效请求处理**：保留用户原始输入内容，根据请求类型分配flag值。
3. **结果输出**：有效请求输出JSON格式结果，无效请求输出礼貌引导语。

### 输出规范
1. **有效请求输出格式**：
[
{
  "content": "用户原始待办内容",
  "flag": 0/1/2,
  "type": "查询/更新/新增"
}
]
2. **无效请求输出格式**：仅回复指定引导语。
    """
    
    
        # 调用大模型
    response = client.chat.completions.create(
        model=os.getenv("KIMI_MODEL", "kimi-k2-turbo-preview"),
        messages=[        {"role": "system", "content": prompt},
                          {"role": "user", "content": user_input}],
        temperature=0.1,  # 完全按指令执行，无创造性
        seed=12345  # 固定种子，确保输出一致
    )
    # 解析多事件数组
    events_list = json.loads(response.choices[0].message.content.strip())
    
    add_content = []
    update_content = []
    select_content = []
    for i in range(0,len(events_list)):
        event_ele = events_list[i]
        if event_ele['flag'] == 0:
            select_content.append(event_ele)
        elif event_ele['flag'] == 1:
            update_content.append(event_ele)
        elif event_ele['flag'] == 2:
            add_content.append(event_ele)
        else:
            continue
        
    if len(add_content)>= 1:
        add_content_merge = ';'.join(item['content'] for item in add_content)
    else:
        add_content_merge=''
        
    if len(update_content)>= 1:
        update_content_merge = ';'.join(item['content'] for item in update_content)
    else:
        update_content_merge = ''
        
    if len(select_content)>= 1:
        select_content_merge = ';'.join(item['content'] for item in select_content)
    else:
        select_content_merge = ''
            
    return add_content_merge, update_content_merge, select_content_merge



# ---------------------- 8. 相关事项查询 ----------------------
def select_event(user_id, user_input):
    
    events_list = []
    
    conn = get_mysql_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
    SELECT event, event_time, location, participants
     FROM events WHERE user_id = %s ORDER BY event_time ASC
    """, (user_id,))
    all_events = cursor.fetchall()
    for evt in all_events:
        events_list.append(json_dumps(evt))
    cursor.close()
    conn.close()
    
    

    prompt = """
    你的任务是作为事项匹配助手，根据用户提供的查询信息，从给定的事项数据库JSON列表中准确匹配出符合条件的事项。
    
    首先，事项数据库包含以下字段及说明：
    - user_id：用户ID（字符串类型）
    - event：事件核心内容（字符串类型）
    - event_time：事件开始时间（标准格式：YYYY-MM-DD HH:MM:SS）
    - location：事件地点（字符串类型）
    - participants：参与人员（原始表述，字符串类型）
    - remark：事件提醒信息（字符串类型，可为空）
    
    请按照以下规则进行匹配：
    1. 全面分析用户查询中涉及的条件，包括但不限于：user_id、event关键词、event_time时间范围、location地点信息、participants参与人员关键词、remark提醒信息关键词等
    2. 对于每个事项，需逐一检查其所有字段是否与查询条件匹配（若查询未涉及某字段，则不将该字段作为匹配条件）
    3. 仅保留完全符合所有查询条件的事项，若没有符合条件的事项，则返回空列表
    4. 返回匹配到的事项列表（格式为JSON数组，保留原始字段名和值）。若没有匹配结果，请返回空JSON数组[]。
    
    现在待待匹配的事项数据集合、以及用户的查询需求如下：
    """
    
    
        # 调用大模型
    response = client.chat.completions.create(
        model=os.getenv("KIMI_MODEL", "kimi-k2-turbo-preview"),
        messages=[        {"role": "system", "content": prompt},
                          {"role": "user", "content": "查询事项列表如下： " + str(all_events) }, 
                          {"role": "user", "content": "用户查询信息输入如下：  " + str(user_input) } ],
        temperature=0.1,  # 完全按指令执行，无创造性
        seed=12345  # 固定种子，确保输出一致
    )
    # 解析多事件数组
    
    events_list = json.loads(response.choices[0].message.content.strip())
    return events_list

# ---------------------- 9. 相关事项更新 ----------------------
def update_event(user_id, user_input):
    
    events_list = []
    
    conn = get_mysql_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
    SELECT event, event_time, location, participants
     FROM events WHERE user_id = %s ORDER BY event_time ASC
    """, (user_id,))
    all_events = cursor.fetchall()
    for evt in all_events:
        events_list.append(json_dumps(evt))
    cursor.close()
    conn.close()
    
    user_content = user_input
    prompt = """
你需要根据用户的中文输入，分析其对事项表的更新需求，并生成可执行的SQL语句。以下是事项表的结构及建表语句：
CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '事件ID',
    user_id VARCHAR(50) NOT NULL COMMENT '用户ID',
    event VARCHAR(255) NOT NULL COMMENT '事件核心内容',
    event_time DATETIME NOT NULL COMMENT '开始时间（标准格式：YYYY-MM-DD HH:MM:SS）',
    location VARCHAR(255) NOT NULL COMMENT '事件地点',
    participants VARCHAR(500) NOT NULL COMMENT '参与人员（原始表述）',
    remark VARCHAR(500) NULL COMMENT '事件提醒信息',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_time (user_id, event_time),
    INDEX idx_event (event(191)),
    INDEX idx_location (location(191))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='日常事件表（仅保留开始时间）'

请按照以下步骤处理：
1. 解析用户输入，明确待更新的事项（通过event描述匹配，需结合数据库现有存储内容进行理解匹配，例如用户提到的“周三下午和李老板的会议”需匹配表中对应事项；若上下文中提供了数据库的事项数据集合，需优先结合该集合中的event内容精准匹配待更新事项）
2. 提取用户需要更新的字段（如event_time、location、participants等）及对应的值（例如用户要求将时间改为4点，需结合原事项的日期信息确定完整的event_time值；若上下文中有对应事项的原始数据，需基于原始数据补充完整更新值）
3. 生成适用于MySQL 5.6版本的可执行SQL UPDATE语句，需包含：
   - 正确的表名（表名为events）
   - WHERE条件（优先通过上下文中数据库事项数据集合里的id定位事项，若id不明确则通过唯一event描述定位）
   - SET子句（仅包含用户明确提及的字段）
   - 更新update_time字段为当前时间（格式：YYYY-MM-DD HH:MM:SS，使用NOW()函数）
4. 若用户输入无法明确匹配事项（例如无法结合上下文中的数据库事项数据集合找到对应event）或字段（例如无法确定“周三”对应的具体日期、“4点”对应的时段是下午还是其他时段），生成空SQL并说明原因
5. 输出要求
    --可以直接执行的sql，不需要额外的其他字符串，例如：UPDATE events
                                                    SET event_time = '2025-12-17 18:00:00',
                                                        update_time = NOW()
                                                    WHERE id = (
                                                            SELECT id
                                                        FROM (
                                                            SELECT id
                                                            FROM events
                                                            WHERE event LIKE '%提交项目进度报告%'
                                                            ORDER BY event_time DESC
                                                            LIMIT 1
                                                        ) AS t
                                                    );
6. 数据库中事项内容如下：
    """.format(events_list)
    
    print('数据库查询结果如下：')
    print(user_input)
        # 调用大模型
    response = client.chat.completions.create(
        model=os.getenv("KIMI_MODEL", "kimi-k2-turbo-preview"),
        messages=[        {"role": "system", "content": prompt},
                          {"role": "user", "content": user_content } ], 
                
        temperature=0.1,  # 完全按指令执行，无创造性
        seed=12345  # 固定种子，确保输出一致
    )
    # 解析多事件数组
    sql_result = response.choices[0].message.content.strip()
    
    print(sql_result)
    return sql_result




# ---------------------- 10. 测试用例 ----------------------
if __name__ == "__main__":
    user_id = "user_001"
    user_input = str(sys.argv[1])
    normalize_res = normalize_time_list(user_input)
    print(f"🔧 标准化后输入：{normalize_res}") 
    #意图拆分，分agent、先后顺序执行步骤
    add_content, update_content, select_content = intention_extra(normalize_res)

    

    # 执行事件提取
    if len(add_content) < 1:
        print("无新增事项")
    else:
        print("=== 事件提取结果 ===")
        result = event_agent(user_id, add_content)
        print(json_dumps(result))        
    
    #执行事件查询
    if len(select_content) < 1:
        print("无查询事项")
    else:
        print("=== 事件查询结果 ===")
        select_result = select_event(user_id, select_content)
        print(json_dumps(select_result))
    
    #执行事件查询
    if len(update_content) < 1:
        print("无更新事项")
    else:
        print("=== 事件更新结果 ===")
        print(update_content)
        sql_result = update_event(user_id, update_content)
     
    
 
'''  
    # 验证数据库查询
    print("\n=== 验证查询：所有事件（标准时间+原始时间） ===")
    conn = get_mysql_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
    SELECT event, event_time, location, participants, remark 
    FROM events WHERE user_id = %s ORDER BY event_time ASC
    """, (user_id,))
    all_events = cursor.fetchall()
    for evt in all_events:
        print(json_dumps(evt))
    cursor.close()
    conn.close()
    '''
