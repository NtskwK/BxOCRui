import paddle
from paddleocr import PPChatOCRv4Doc
from config import config
from loguru import logger as log

if paddle.device.is_compiled_with_cuda():
    log.info("PaddlePaddle supports CUDA, setting device to GPU")
    device = paddle.device.set_device("gpu")
else:
    log.warning("PaddlePaddle does not support CUDA, setting device to CPU")
    device = paddle.device.set_device("cpu")

model_dir = config.model_dir

pipeline = PPChatOCRv4Doc(
    layout_detection_model_name="RT-DETR-H_layout_3cls",
    layout_detection_model_dir=model_dir + "RT-DETR-H_layout_3cls",
    doc_orientation_classify_model_name="PP-LCNet_x1_0_doc_ori",
    doc_orientation_classify_model_dir=model_dir + "PP-LCNet_x1_0_doc_ori",
    doc_unwarping_model_name="UVDoc",
    doc_unwarping_model_dir=model_dir + "UVDoc",
    text_detection_model_name="PP-OCRv5_server_det",
    text_detection_model_dir=model_dir + "PP-OCRv5_server_det",
    text_recognition_model_name="PP-OCRv5_server_rec",
    text_recognition_model_dir=model_dir + "PP-OCRv5_server_rec",
    textline_orientation_model_name="PP-LCNet_x1_0_textline_ori",
    textline_orientation_model_dir=model_dir + "PP-LCNet_x1_0_textline_ori",
    seal_text_recognition_model_name="PP-OCRv4_server_rec_doc",
    seal_text_recognition_model_dir=model_dir + "PP-OCRv4_server_rec_doc",
    seal_text_detection_model_name="PP-OCRv4_server_seal_det",
    seal_text_detection_model_dir=model_dir + "PP-OCRv4_server_seal_det",
    table_structure_recognition_model_name="SLANet_plus",
    table_structure_recognition_model_dir=model_dir + "SLANet_plus",
)
