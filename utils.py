import json
import re
from datetime import datetime
from typing import List
from loguru import logger as log
from tqdm import tqdm

from numpy import ndarray
from paddleocr import PaddleOCR

from config import config
from model import pipeline
from classes import invoice_content

ocr = PaddleOCR(paddlex_config="PaddleOCR.yaml")

base_key_words = [
    "invoice_date",
    "invoice_number",
]

ticket_key_words = [
    "first_station",
    "second_station",
    "passenger_name",
    "price",
    "departure_time",
    "seat_class",
    "train_service",
    "travel_date",
]

invoice_key_words = [
    "total_amount",
    "program_name",
]

all_key_words = base_key_words + ticket_key_words + invoice_key_words


def invoice_verify(code: str) -> bool | List[str]:
    """
    验证二维码内容格式是否正确
    :param code: 二维码内容
    :return: bool

    二维码内容应为8位由逗号分割的字符串。
    """

    code = code.strip()
    data = code.split(",")
    log.debug(f"二维码内容分割结果: {data}")
    if not data:
        log.error("二维码内容为空")
        return False

    expected_lengths = [2, 2, None, None, None, 8, None, 4]
    if len(data) != len(expected_lengths):
        log.error("二维码内容长度不匹配!")
        return False

    for i, expected in enumerate(expected_lengths):
        if expected is not None and len(data[i]) != expected:
            log.error(f"二维码内容{i + 1}格式不正确:{data[i]}")
            return False

    if data[0] != "01":
        log.error(f"二维码内容第1部分不正确: {data[0]}")
        return False

    return data


def ocr_llm_verify(chat_result: dict) -> dict:
    for key in tqdm(
        list(chat_result.keys()), total=len(chat_result), desc="正在验证LLM结果"
    ):
        content = chat_result[key]
        log.debug(f"正在处理键: {key}, 内容: {content}")
        if "对不起" in content or "无法识别" in content:
            log.warning(f"{key} 处理结果: {content}")
            raise ValueError(f"{key} 处理结果: {content}！请联系管理员！")

        lines = content.splitlines()
        if len(lines) > 20:
            log.warning(f"{key} 处理结果行数超过10行，LLM可能出现复读问题！")
            log.warning(f"不正常的结果：{content}")
            chat_result[key] = lines[0]
        elif len(lines) > 1:
            for line in lines:
                if key not in line:
                    continue
                else:
                    chat_result[key] = line

        if ":" in content:
            chat_result[key] = content.split(":")[1].strip()
        if "：" in content:
            chat_result[key] = content.split("：")[1].strip()

        if key == "invoice_number":
            try:
                pattern = r"\b\d{10,}\b"
                result = re.findall(pattern, chat_result[key])[0]
                chat_result[key] = int(result)
            except ValueError:
                log.error(f"无法将{key}转换为整数: {chat_result[key]}")
                chat_result[key] = 0

        if key == "price" or key == "amount":
            chat_result[key] = (
                chat_result[key]
                .replace("￥", "")
                .replace("¥", "")
                .replace("元", "")
                .replace("人民币", "")
                .replace("人民币元", "")
                .strip()
            )

            assert float(
                chat_result[key]
            ), f"{key} should be a valid float, but got '{chat_result[key]}'!"

    return chat_result


def ocr_pipline(img_ndarray: ndarray) -> invoice_content | str:
    log.info("开始进行OCR识别...")
    visual_predict_res = pipeline.visual_predict(
        input=img_ndarray,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_common_ocr=True,
        use_seal_recognition=False,
        use_table_recognition=True,
    )

    if not visual_predict_res:
        return "OCR returned no results."

    visual_info_list = []
    for verified_result in visual_predict_res:
        if "visual_info" not in verified_result:
            log.warning("视觉预测结果中缺少visual_info字段")
            continue
        visual_info_list.append(verified_result["visual_info"])
        layout_parsing_result = verified_result.get("layout_parsing_result", None)

    if not visual_info_list:
        return "无法从OCR结果中提取视觉信息"

    log.info(f"OCR提取完成，开始构建向量")

    vector_info = pipeline.build_vector(
        visual_info_list,
        flag_save_bytes_vector=True,
        retriever_config=config.retriever_config.__dict__,
    )

    log.info("向量构建完成，开始进行多模态LLM预测...")

    mllm_predict_res = pipeline.mllm_pred(
        input=img_ndarray,
        key_list=all_key_words,
        mllm_chat_bot_config=config.mllm_chat_bot_config.__dict__,
    )
    if "调用失败" in mllm_predict_res["mllm_res"]:
        log.error("多模态LLM调用失败，请检查接口配置！")
        return "多模态LLM调用失败，请检查接口配置！"

    log.debug(f"mllm_predict_res: {mllm_predict_res}")

    if not mllm_predict_res or "mllm_res" not in mllm_predict_res:
        return "多模态LLM预测返回无效结果"

    log.info("多模态LLM处理完成，正在整理结果")
    invoice_type = "common_invoice"
    key_words = base_key_words + invoice_key_words
    for key in mllm_predict_res["mllm_res"].keys():
        if "中国铁路祝您旅途愉快" in mllm_predict_res["mllm_res"][key]:
            log.debug("当前发票类型为火车票")
            key_words = ticket_key_words + base_key_words
            invoice_type = "train_ticket"
            break
        else:
            continue

    mllm_predict_info = mllm_predict_res["mllm_res"]
    chat_result = pipeline.chat(
        key_list=key_words,
        visual_info=visual_info_list,
        vector_info=vector_info,
        mllm_predict_info=mllm_predict_info,
        chat_bot_config=config.chat_bot_config.__dict__,
        retriever_config=config.retriever_config.__dict__,
    )

    if chat_result := chat_result["chat_res"]:
        log.info(f"chat_result: {chat_result}")
    else:
        return "成果整理失败"

    verified_result = ocr_llm_verify(chat_result)
    log.info(f"OCR识别和多模态LLM处理完成:{verified_result}")

    if not invoice_type:
        log.error("没有找到发票类型！")
        return "这是一个内部错误，请联系管理员！"

    result = None
    match invoice_type:
        case "train_ticket":
            verified_result["invoice_type"] = "火车票"
            content = {
                "passenger_name": verified_result.get("passenger_name", ""),
                "first_station": verified_result.get("first_station", ""),
                "second_station": verified_result.get("second_station", ""),
                "seat_class": verified_result.get("seat_class", ""),
            }
            result = invoice_content(
                program=verified_result["invoice_type"],
                date=verified_result.get("travel_date", ""),
                amount=verified_result.get("price", ""),
                content=json.dumps(
                    content,
                    indent=2,
                ),
                invoice_number=verified_result.get("invoice_number", 0),
                invoice_type=verified_result["invoice_type"],
            )
        case "common_invoice":
            verified_result["invoice_type"] = "普通发票"
            result = invoice_content(
                date=verified_result.get("invoice_date", ""),
                program=verified_result.get("program_name", ""),
                amount=verified_result.get("total_amount", ""),
                content="",
                invoice_number=verified_result.get("invoice_number", 0),
                invoice_type=verified_result["invoice_type"],
            )

        case _:
            log.error(f"未知的发票类型: {invoice_type}")
            return "未知的发票类型"

    assert result, "result is None, Result should not be None at this point"

    log.info(f"最终结果: {result}")

    return result
