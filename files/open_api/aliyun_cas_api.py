# -*- coding: utf-8 -*-

from alibabacloud_cas20200407 import models as cas_20200407_models
from alibabacloud_cas20200407.client import Client as cas20200407Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models


def upload_user_certificate(
        access_key_id, access_key_secret,
        cert_name, cert, key
):
    """
    上传证书
    """
    # 工程代码泄露可能会导致 AccessKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考。
    # 建议使用更安全的 STS 方式，更多鉴权访问方式请参见：https://help.aliyun.com/document_detail/378659.html。
    config = open_api_models.Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret
    )

    config.endpoint = 'cas.aliyuncs.com'    # Endpoint 请参考 https://api.aliyun.com/product/cas

    client = cas20200407Client(config)
    upload_user_certificate_request = cas_20200407_models.UploadUserCertificateRequest(
        name=cert_name,
        cert=cert,
        key=key,
    )

    runtime = util_models.RuntimeOptions()

    response = client.upload_user_certificate_with_options(upload_user_certificate_request, runtime)

    return response.body.cert_id
