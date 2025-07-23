import io
import binascii
from loguru import logger as log
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol

from PIL import Image
from numpy import array

from utils import invoice_verify, ocr_pipline

from classes import api_invoice_error, api_invoice_return, invoice_content


def get_img(image_data: str) -> Image.Image | None:
    """
    Converts a base64-encoded image data URL to a PIL Image object.
    Args:
        image_data (str): A string containing the image data in data URL format (e.g., "data:image/png;base64,...").
    Returns:
        Image.Image | None: The decoded PIL Image object if successful, otherwise None.
    Logs:
        - Logs an error if the input format is invalid or if the image cannot be identified.
        - Logs the length of the base64 data for debugging purposes.
    """

    if not image_data.startswith("data:image/"):
        log.error("Invalid image data format")
        return

    # 提取 base64 编码部分
    base64_data = image_data.split(",")[1]
    log.debug(f"Base64 data siez: {len(base64_data) / 1024} KB")
    qr_image_data = binascii.a2b_base64(base64_data)

    image_stream = io.BytesIO(qr_image_data)

    try:
        img = Image.open(image_stream)
    except (IOError, ValueError) as e:
        log.error(f"Cannot identify image file: {e}")
        return

    return img


class API:
    """
    API class for handling requests from the front-end.
    """

    def __init__(self):
        self._window = None

    def set_window(self, webview_window):
        self._window = webview_window

    # 可以添加更多的方法来实现与前端的交互
    def echo(self, message):
        return message

    def scan_qrcode(self, qr_image_data):
        """
        Scans and decodes a QR code from a base64-encoded image string.
        Args:
            qr_image_data (str): A base64-encoded image string in the format "data:image/<type>;base64,<data>".
        Returns:
            dict: A dictionary containing the result of the QR code scan.
                On success:
                    {
                            "fixed_value": str,
                            "invoice_type": str,
                            "invoice_code": str,
                            "invoice_number": str,
                            "amount": str,
                            "date": str,
                            "check_code": str,
                            "encrypt": str,
                On failure:
                    {
                        "success": False,
                        "error": str
        Raises:
            ValueError: If no valid QR code is found, more than one QR code is detected,
                        or the QR code fails verification.
        Notes:
            - The function expects the QR code to contain comma-separated invoice information.
            - The QR code is validated using the `invoice_verify` function.
        """
        # return {"success": False, "error": "No QR code found"}

        # 将解码后的数据转换为字节流
        img = get_img(qr_image_data)

        if not img:
            return {"success": False, "error": "Cannot identify image file"}

        results = pyzbar.decode(img, symbols=[ZBarSymbol.QRCODE])

        results = list(map(lambda x: x.data.decode("utf-8"), results))

        log.debug(f"解析到的二维码内容: {results}")

        if not results or len(results) != 1:
            return {"success": False, "error": "未找到有效的二维码或二维码数量不为1"}

        result: str = results[0]
        if not invoice_verify(result):
            return {"success": False, "error": "无效的二维码！"}

        if codes := result.split(","):
            return {
                "success": True,
                "content": {
                    "fixed_value": codes[0],
                    "invoice_type": codes[1],
                    "invoice_code": codes[2],
                    "invoice_number": codes[3],
                    "amount": codes[4],
                    "date": codes[5],
                    "check_code": codes[6],
                    "encrypt": codes[7],
                },
            }
        else:
            return {"success": False, "error": "No QR code found"}

    def img_ocr(self, img_data: str) -> dict:
        result = self._img_ocr(img_data)
        return result.to_dict()

    def _img_ocr(self, img_data) -> api_invoice_return | api_invoice_error:
        """
        Placeholder for image OCR functionality.
        Args:
            img_data (str): Base64-encoded image data.
        Returns:
            dict: A dictionary containing the OCR result.
        """
        img = get_img(img_data)

        if not img:
            return api_invoice_error("Cannot identify image file")

        if img.format not in ["JPEG", "PNG", "BMP", "TIFF"]:
            return api_invoice_error(f"Unsupported image format: {img.format}")

        img_ndarray = array(img)
        if img_ndarray.size == 0:
            return api_invoice_error("Image size is zero")

        result = ocr_pipline(img_ndarray)

        if isinstance(result, invoice_content):
            return api_invoice_return(content=result)

        if isinstance(result, str):
            return api_invoice_error(error=result)

        return api_invoice_error(error="Unknow pipline result！请联系管理员！")
